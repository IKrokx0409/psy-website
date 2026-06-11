import os, uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from models import Resource
from schemas import ResourceCreate, ResourceUpdate, ResourceListItem, ResourceOut
from routers.admin import require_teacher

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {
    'video': ['video/mp4', 'video/webm', 'video/ogg'],
    'audio': ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a'],
    'pdf':   ['application/pdf'],
}
MAX_SIZE = 200 * 1024 * 1024  # 200 MB

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


@router.post("/upload", response_model=ResourceOut, status_code=201,
             dependencies=[Depends(require_teacher)])
async def upload_resource_file(
    title:         str        = Form(...),
    category:      str        = Form(...),
    resource_type: str        = Form(...),
    summary:       Optional[str] = Form(None),
    is_published:  bool       = Form(True),
    file:          UploadFile = File(...),
    db:            AsyncSession = Depends(get_db),
):
    if resource_type not in ALLOWED_TYPES:
        raise HTTPException(400, "不支持的资源类型")
    if file.content_type not in ALLOWED_TYPES[resource_type]:
        raise HTTPException(400, f"文件类型 {file.content_type} 与资源类型 {resource_type} 不匹配")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "文件超过 200MB 限制")

    ext = os.path.splitext(file.filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, safe_name), "wb") as f:
        f.write(content)

    r = Resource(title=title, category=category, resource_type=resource_type,
                 summary=summary, file_path=f"/uploads/{safe_name}", is_published=is_published)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@router.patch("/{resource_id}/file", response_model=ResourceOut,
              dependencies=[Depends(require_teacher)])
async def replace_resource_file(
    resource_id: int,
    resource_type: str        = Form(...),
    file:          UploadFile = File(...),
    db:            AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "资源不存在")
    if resource_type not in ALLOWED_TYPES:
        raise HTTPException(400, "不支持的资源类型")
    if file.content_type not in ALLOWED_TYPES[resource_type]:
        raise HTTPException(400, f"文件类型 {file.content_type} 与资源类型 {resource_type} 不匹配")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "文件超过 200MB 限制")

    # 删除旧文件
    if r.file_path:
        old = os.path.join(UPLOAD_DIR, os.path.basename(r.file_path))
        if os.path.exists(old):
            os.remove(old)

    ext = os.path.splitext(file.filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, safe_name), "wb") as f:
        f.write(content)

    r.file_path = f"/uploads/{safe_name}"
    r.resource_type = resource_type
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
