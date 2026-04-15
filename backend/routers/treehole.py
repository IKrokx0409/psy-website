import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import TreeholePost
from schemas import (
    TreeholePostCreate,
    TreeholePostOut,
    TreeholePostCreateResponse,
    DeleteRequest,
)

router = APIRouter(prefix="/api/treehole", tags=["treehole"])


@router.get("", response_model=List[TreeholePostOut])
async def get_posts(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(TreeholePost)
        .where(TreeholePost.status == "approved")
        .order_by(TreeholePost.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=TreeholePostCreateResponse, status_code=201)
async def create_post(data: TreeholePostCreate, db: AsyncSession = Depends(get_db)):
    token = secrets.token_hex(32)
    post = TreeholePost(
        anonymous_name=data.anonymous_name,
        content=data.content,
        tags=data.tags,
        status="pending",
        author_token=token,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return TreeholePostCreateResponse(
        id=post.id,
        anonymous_name=post.anonymous_name,
        content=post.content,
        tags=post.tags or [],
        created_at=post.created_at,
        author_token=token,
    )


@router.post("/{post_id}/delete-request")
async def request_delete(
    post_id: int,
    body: DeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TreeholePost).where(TreeholePost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if post.author_token != body.author_token:
        raise HTTPException(status_code=403, detail="无权限")
    if post.status != "approved":
        raise HTTPException(status_code=400, detail="仅可对已发布的帖子申请删除")
    post.status = "delete_requested"
    await db.commit()
    return {"message": "删除申请已提交，等待审核"}
