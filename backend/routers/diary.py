import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from database import get_db
from models import DiaryEntry
from schemas import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryOut
from hiagent_client import HiAgentClient
from typing import List, Optional

router = APIRouter(prefix="/api/diary", tags=["diary"])


class DiaryAIRequest(BaseModel):
    user_id: str = ""
    today_diary: str = ""
    today_mood_score: int = 0
    today_mood_label: str = ""
    today_emotions: List[str] = []
    date: str = ""
    week_diaries: List[dict] = []   # [{date, mood_score, mood_label, emotions, content}]


def _format_week_diaries(entries: List[dict], today: str) -> str:
    """将近7天日记列表格式化为工作流可读的多行字符串，缺失天标注"无记录"。"""
    from datetime import date as date_cls, timedelta
    entry_map = {e["date"]: e for e in entries}
    lines = []
    base = date_cls.fromisoformat(today) if today else date_cls.today()
    for i in range(6, -1, -1):
        d = (base - timedelta(days=i)).isoformat()
        month_day = d[5:]   # MM-DD
        if d in entry_map:
            e = entry_map[d]
            tags = "、".join(e.get("emotions") or []) or "无"
            summary = (e.get("content") or "")[:30].replace("\n", " ")
            lines.append(f"{month_day} | 评分:{e['mood_score']} | 标签:{tags} | 摘要:{summary}")
        else:
            lines.append(f"{month_day} | 无记录")
    return "\n".join(lines)


@router.post("/ai-response")
async def get_diary_ai_response(request: DiaryAIRequest, db: AsyncSession = Depends(get_db)):
    week_str = _format_week_diaries(request.week_diaries, request.date)

    inputs = {
        "today_diary":      request.today_diary,
        "today_mood_score": str(request.today_mood_score) if request.today_mood_score else "",
        "today_mood_label": request.today_mood_label,
        "today_emotions":   "、".join(request.today_emotions) if request.today_emotions else "无",
        "date":             request.date,
        "week_diaries":     week_str,
    }

    api_key = os.getenv("HITSZ_DIARY_API_KEY") or os.getenv("HITSZ_API_KEY")
    client = HiAgentClient(api_key=api_key)
    result = client.run_workflow(inputs)

    emotional = result.get("emotional_response", "").strip()
    weekly    = result.get("weekly_summary", "").strip()
    if not emotional and not weekly:
        raise HTTPException(status_code=502, detail="AI 响应解析异常")

    # 将两个输出缓存为 JSON 存入日记条目
    if request.user_id and request.date:
        res = await db.execute(
            select(DiaryEntry).where(
                and_(DiaryEntry.user_id == request.user_id, DiaryEntry.date == request.date)
            )
        )
        entry = res.scalar_one_or_none()
        if entry:
            import json as _json
            entry.ai_feedback = _json.dumps(
                {"emotional_response": emotional, "weekly_summary": weekly},
                ensure_ascii=False,
            )
            await db.commit()

    return {"emotional_response": emotional, "weekly_summary": weekly}


@router.post("/seed-mock/{user_id}", tags=["dev"])
async def seed_mock_diaries(user_id: str, db: AsyncSession = Depends(get_db)):
    """开发调试用：为指定用户写入近7天的模拟日记数据（已存在则跳过）"""
    from datetime import date as date_cls, timedelta

    today = date_cls.today()
    mock = [
        {
            "days_ago": 6,
            "mood_score": 7, "mood_label": "较好",
            "emotions": ["开心", "充实"],
            "content": "今天和同学打了会儿羽毛球，久违地出汗了，感觉很舒服。晚上室友做了火锅，围坐一起聊天，没有想太多。",
        },
        {
            "days_ago": 5,
            "mood_score": 4, "mood_label": "有点低落",
            "emotions": ["焦虑", "疲惫"],
            "content": "期末项目 deadline 压力很大，对着屏幕坐了一整天，什么进展也没有。感觉脑子转不动，很挫败。",
        },
        # day -4: 无记录
        {
            "days_ago": 3,
            "mood_score": 6, "mood_label": "还不错",
            "emotions": ["平静", "充实"],
            "content": "在图书馆待了一整天，虽然累，但把一直拖着的文献综述写完了。有点小小的成就感。",
        },
        # day -2: 无记录
        {
            "days_ago": 1,
            "mood_score": 3, "mood_label": "有些低落",
            "emotions": ["焦虑", "委屈", "疲惫"],
            "content": "和室友因为宿舍卫生的事有点摩擦，说了些不好听的话。晚上躺着睡不着，反复想这件事。",
        },
        {
            "days_ago": 0,
            "mood_score": 5, "mood_label": "一般",
            "emotions": ["平静", "空白"],
            "content": "今天不知道为什么状态很飘，什么都做了一点，但什么都没做完。有点空，说不上来哪里不对。",
        },
    ]

    created = 0
    for item in mock:
        date_str = (today - timedelta(days=item["days_ago"])).isoformat()
        res = await db.execute(
            select(DiaryEntry).where(
                and_(DiaryEntry.user_id == user_id, DiaryEntry.date == date_str)
            )
        )
        if res.scalar_one_or_none():
            continue
        db.add(DiaryEntry(
            user_id=user_id,
            date=date_str,
            mood_score=item["mood_score"],
            mood_label=item["mood_label"],
            emotions=item["emotions"],
            content=item["content"],
        ))
        created += 1

    await db.commit()
    return {"ok": True, "created": created, "message": f"为用户 {user_id} 写入 {created} 条模拟日记"}


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
