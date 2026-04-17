from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from models import Announcement
from schemas import AnnouncementListItem, AnnouncementOut

router = APIRouter(prefix="/api/announcements", tags=["announcements"])


@router.get("", response_model=List[AnnouncementListItem])
async def get_announcements(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Announcement).where(Announcement.is_published == True)
    if category:
        stmt = stmt.where(Announcement.category == category)
    stmt = stmt.order_by(Announcement.published_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{ann_id}", response_model=AnnouncementOut)
async def get_announcement(ann_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Announcement).where(
            Announcement.id == ann_id,
            Announcement.is_published == True,
        )
    )
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="公告不存在")
    return ann
