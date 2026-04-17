from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import Questionnaire
from schemas import QuestionnaireCreate, QuestionnaireUpdate, QuestionnaireListItem, QuestionnaireOut
from routers.admin import require_teacher

router = APIRouter(prefix="/api/questionnaires", tags=["questionnaires"])


@router.get("", response_model=List[QuestionnaireListItem])
async def list_questionnaires(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Questionnaire).where(Questionnaire.is_published == True)
        .order_by(Questionnaire.created_at.desc())
    )
    return result.scalars().all()


@router.get("/admin", response_model=List[QuestionnaireListItem],
            dependencies=[Depends(require_teacher)])
async def admin_list_questionnaires(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Questionnaire).order_by(Questionnaire.created_at.desc()))
    return result.scalars().all()


@router.get("/{q_id}", response_model=QuestionnaireOut)
async def get_questionnaire(q_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Questionnaire).where(Questionnaire.id == q_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="问卷不存在")
    return q


@router.post("", response_model=QuestionnaireOut, status_code=201,
             dependencies=[Depends(require_teacher)])
async def create_questionnaire(data: QuestionnaireCreate, db: AsyncSession = Depends(get_db)):
    q = Questionnaire(**data.model_dump())
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


@router.patch("/{q_id}", response_model=QuestionnaireOut,
              dependencies=[Depends(require_teacher)])
async def update_questionnaire(
    q_id: int, data: QuestionnaireUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Questionnaire).where(Questionnaire.id == q_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="问卷不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(q, k, v)
    await db.commit()
    await db.refresh(q)
    return q


@router.delete("/{q_id}", dependencies=[Depends(require_teacher)])
async def delete_questionnaire(q_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Questionnaire).where(Questionnaire.id == q_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="问卷不存在")
    await db.delete(q)
    await db.commit()
    return {"message": "删除成功"}
