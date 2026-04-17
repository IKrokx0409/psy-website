from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from models import TreeholePost, Announcement
from schemas import (
    TreeholePostAdminOut,
    ReviewAction,
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementAdminOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_teacher(x_role: str = Header(default="")):
    if x_role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可访问")


# ── 树洞管理 ──────────────────────────────────────────────────────────────────

@router.get("/treehole", response_model=List[TreeholePostAdminOut],
            dependencies=[Depends(require_teacher)])
async def admin_get_posts(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TreeholePost).order_by(TreeholePost.created_at.desc())
    if status:
        stmt = stmt.where(TreeholePost.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/treehole/{post_id}/review",
              dependencies=[Depends(require_teacher)])
async def admin_review_post(
    post_id: int,
    body: ReviewAction,
    db: AsyncSession = Depends(get_db),
):
    if body.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="action 须为 approve 或 reject")
    result = await db.execute(select(TreeholePost).where(TreeholePost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    post.status = "approved" if body.action == "approve" else "rejected"
    await db.commit()
    return {"message": "操作成功", "status": post.status}


@router.delete("/treehole/{post_id}",
               dependencies=[Depends(require_teacher)])
async def admin_delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TreeholePost).where(TreeholePost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    await db.delete(post)
    await db.commit()
    return {"message": "已删除"}


# ── 公告管理 ──────────────────────────────────────────────────────────────────

@router.get("/announcements", response_model=List[AnnouncementAdminOut],
            dependencies=[Depends(require_teacher)])
async def admin_get_announcements(db: AsyncSession = Depends(get_db)):
    stmt = select(Announcement).order_by(Announcement.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/announcements", response_model=AnnouncementAdminOut, status_code=201,
             dependencies=[Depends(require_teacher)])
async def admin_create_announcement(
    data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
):
    ann = Announcement(
        title=data.title,
        category=data.category,
        published_at=data.published_at,
        is_published=data.is_published,
        body=data.body,
        cover_image=data.cover_image,
    )
    db.add(ann)
    await db.commit()
    await db.refresh(ann)
    return ann


@router.patch("/announcements/{ann_id}", response_model=AnnouncementAdminOut,
              dependencies=[Depends(require_teacher)])
async def admin_update_announcement(
    ann_id: int,
    data: AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="公告不存在")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(ann, field, value)
    await db.commit()
    await db.refresh(ann)
    return ann


@router.delete("/announcements/{ann_id}",
               dependencies=[Depends(require_teacher)])
async def admin_delete_announcement(
    ann_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="公告不存在")
    await db.delete(ann)
    await db.commit()
    return {"message": "已删除"}
