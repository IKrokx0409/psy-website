import calendar as cal_module
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import cast, Date as DateType, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import ChatRecord, ClassGroup, ClassMember, DiaryEntry

router = APIRouter(prefix="/api/stats", tags=["stats"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class DailyStatOut(BaseModel):
    date: str
    diary_count: int = 0
    diary_low_mood_count: int = 0
    chat_count: int = 0
    chat_low_mood_count: int = 0


class MonthlyStatsOut(BaseModel):
    student_total: int
    days: List[DailyStatOut]


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _student_ids(
    class_id: Optional[int],
    teacher_id: Optional[str],
    db: AsyncSession,
) -> List[str]:
    if class_id:
        rows = (await db.execute(
            select(ClassMember.student_id).where(ClassMember.class_id == class_id)
        )).all()
    elif teacher_id:
        cids = [r[0] for r in (await db.execute(
            select(ClassGroup.id).where(ClassGroup.teacher_id == teacher_id)
        )).all()]
        if not cids:
            return []
        rows = (await db.execute(
            select(ClassMember.student_id).where(ClassMember.class_id.in_(cids))
        )).all()
    else:
        return []
    return list({r[0] for r in rows})   # deduplicate across classes


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("/monthly", response_model=MonthlyStatsOut)
async def monthly_stats(
    year:       int           = Query(..., ge=2020, le=2100),
    month:      int           = Query(..., ge=1,    le=12),
    threshold:  int           = Query(4,   ge=1,    le=9),
    class_id:   Optional[int] = Query(None),
    teacher_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    sids = await _student_ids(class_id, teacher_id, db)
    if not sids:
        _, dim = cal_module.monthrange(year, month)
        return MonthlyStatsOut(
            student_total=0,
            days=[
                DailyStatOut(date=f"{year}-{month:02d}-{d:02d}")
                for d in range(1, dim + 1)
            ],
        )

    _, days_in_month = cal_module.monthrange(year, month)
    month_prefix = f"{year}-{month:02d}-"

    # ── Diary entries ─────────────────────────────────────────────────────────
    diary_rows = (await db.execute(
        select(DiaryEntry.user_id, DiaryEntry.date, DiaryEntry.mood_score)
        .where(
            DiaryEntry.user_id.in_(sids),
            DiaryEntry.date.startswith(month_prefix),
        )
    )).all()

    # ── Chat sessions (distinct user × date) ──────────────────────────────────
    start_dt = datetime(year, month, 1, tzinfo=timezone.utc)
    ny = year if month < 12 else year + 1
    nm = month + 1 if month < 12 else 1
    end_dt = datetime(ny, nm, 1, tzinfo=timezone.utc)

    chat_rows = (await db.execute(
        select(
            ChatRecord.user_id,
            cast(ChatRecord.sent_at, DateType).label("chat_date"),
        )
        .where(
            ChatRecord.user_id.in_(sids),
            ChatRecord.sent_at >= start_dt,
            ChatRecord.sent_at < end_dt,
        )
        .distinct()
    )).all()

    # ── Aggregate ─────────────────────────────────────────────────────────────
    # diary_mood: (user_id, date_str) → mood_score  (for chat low-mood cross-ref)
    diary_mood: dict = {}
    diary_by_date: dict = defaultdict(lambda: {"count": 0, "low": 0})

    for uid, date_str, score in diary_rows:
        diary_mood[(uid, date_str)] = score
        diary_by_date[date_str]["count"] += 1
        if score <= threshold:
            diary_by_date[date_str]["low"] += 1

    chat_by_date: dict = defaultdict(set)
    for uid, chat_date in chat_rows:
        chat_by_date[str(chat_date)].add(uid)

    # ── Build output ──────────────────────────────────────────────────────────
    days_out: List[DailyStatOut] = []
    for d in range(1, days_in_month + 1):
        ds = f"{year}-{month:02d}-{d:02d}"
        di   = diary_by_date.get(ds, {"count": 0, "low": 0})
        cuids = chat_by_date.get(ds, set())
        chat_low = sum(
            1 for uid in cuids
            if diary_mood.get((uid, ds), 999) <= threshold
        )
        days_out.append(DailyStatOut(
            date=ds,
            diary_count=di["count"],
            diary_low_mood_count=di["low"],
            chat_count=len(cuids),
            chat_low_mood_count=chat_low,
        ))

    return MonthlyStatsOut(student_total=len(sids), days=days_out)
