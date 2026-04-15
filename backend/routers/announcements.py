from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from models import Announcement
from schemas import AnnouncementOut

router = APIRouter(prefix="/api/announcements", tags=["announcements"])


@router.get("", response_model=List[AnnouncementOut])
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
