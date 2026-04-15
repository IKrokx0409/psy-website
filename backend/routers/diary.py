from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database import get_db
from models import DiaryEntry
from schemas import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryOut
from typing import List, Optional

router = APIRouter(prefix="/api/diary", tags=["diary"])


@router.get("", response_model=List[DiaryEntryOut])
async def list_entries(
    user_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    filters = [DiaryEntry.user_id == user_id]
    if start:
        filters.append(DiaryEntry.date >= start)
    if end:
        filters.append(DiaryEntry.date <= end)
    result = await db.execute(
        select(DiaryEntry).where(and_(*filters)).order_by(DiaryEntry.date)
    )
    return result.scalars().all()


@router.post("", response_model=DiaryEntryOut)
async def create_or_upsert(data: DiaryEntryCreate, db: AsyncSession = Depends(get_db)):
    # Upsert: same user_id + date → update existing
    result = await db.execute(
        select(DiaryEntry).where(
            and_(DiaryEntry.user_id == data.user_id, DiaryEntry.date == data.date)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.mood_score = data.mood_score
        existing.mood_label = data.mood_label
        existing.emotions = data.emotions
        existing.content = data.content
        existing.json_data = data.json_data
        await db.commit()
        await db.refresh(existing)
        return existing

    entry = DiaryEntry(**data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/{entry_id}", response_model=DiaryEntryOut)
async def patch_entry(
    entry_id: int, data: DiaryEntryUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(DiaryEntry).where(DiaryEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)

    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}")
async def delete_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiaryEntry).where(DiaryEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    await db.delete(entry)
    await db.commit()
    return {"ok": True}
