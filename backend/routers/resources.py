from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from models import Resource
from schemas import ResourceCreate, ResourceUpdate, ResourceListItem, ResourceOut
from routers.admin import require_teacher

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get("", response_model=List[ResourceListItem])
async def list_resources(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Resource).where(Resource.is_published == True).order_by(Resource.created_at.desc())
    if category:
        stmt = stmt.where(Resource.category == category)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/admin", response_model=List[ResourceListItem],
            dependencies=[Depends(require_teacher)])
async def admin_list_resources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resource).order_by(Resource.created_at.desc()))
    return result.scalars().all()


@router.get("/{resource_id}", response_model=ResourceOut)
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="资源不存在")
    return r


@router.post("", response_model=ResourceOut, status_code=201,
             dependencies=[Depends(require_teacher)])
async def create_resource(data: ResourceCreate, db: AsyncSession = Depends(get_db)):
    r = Resource(**data.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@router.patch("/{resource_id}", response_model=ResourceOut,
              dependencies=[Depends(require_teacher)])
async def update_resource(
    resource_id: int, data: ResourceUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="资源不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(r, k, v)
    await db.commit()
    await db.refresh(r)
    return r


@router.delete("/{resource_id}", dependencies=[Depends(require_teacher)])
async def delete_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="资源不存在")
    await db.delete(r)
    await db.commit()
    return {"message": "删除成功"}
