import random
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import DailyTip

router = APIRouter(prefix="/api/tips", tags=["tips"])


class TipOut(BaseModel):
    id: int
    content: str
    active: bool
    model_config = {"from_attributes": True}


class TipCreate(BaseModel):
    content: str
    active: bool = True


# ── Public ────────────────────────────────────────────────────────────────────

@router.get("/random", response_model=Optional[TipOut])
async def random_tip(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(DailyTip).where(DailyTip.active == True)
    )).scalars().all()
    if not rows:
        return None
    return random.choice(rows)


# ── Admin CRUD ────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[TipOut])
async def list_tips(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(DailyTip).order_by(DailyTip.id))).scalars().all()
    return rows


@router.post("/", response_model=TipOut, status_code=201)
async def create_tip(body: TipCreate, db: AsyncSession = Depends(get_db)):
    tip = DailyTip(content=body.content.strip(), active=body.active)
    db.add(tip)
    await db.commit()
    await db.refresh(tip)
    return tip


@router.patch("/{tip_id}", response_model=TipOut)
async def update_tip(tip_id: int, body: TipCreate, db: AsyncSession = Depends(get_db)):
    tip = await db.get(DailyTip, tip_id)
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    tip.content = body.content.strip()
    tip.active  = body.active
    await db.commit()
    await db.refresh(tip)
    return tip


@router.delete("/{tip_id}", status_code=204)
async def delete_tip(tip_id: int, db: AsyncSession = Depends(get_db)):
    tip = await db.get(DailyTip, tip_id)
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    await db.delete(tip)
    await db.commit()
