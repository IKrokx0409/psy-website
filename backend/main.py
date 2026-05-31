import os
from contextlib import asynccontextmanager
from typing import Optional

import json
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_db
from models import Base, ChatRecord
from routers import announcements, treehole, admin, diary, resources, questionnaires, courses, stats, tips

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时自动建表（表已存在则跳过）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(announcements.router)
app.include_router(treehole.router)
app.include_router(admin.router)
app.include_router(diary.router)
app.include_router(resources.router)
app.include_router(questionnaires.router)
app.include_router(courses.router)
app.include_router(stats.router)
app.include_router(tips.router)

import os
_uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


@app.get("/api/chat/stream")
async def chat_stream_stub(request: Request):
    """no-ai 分支：立即返回提示，不发起任何外部请求。"""
    conv_id = request.query_params.get("conversation_id", "")

    async def _sse():
        done_payload = json.dumps({
            "thought": "当前运行环境无法连接 AI 服务（需要校园网）。",
            "reply": "AI 智能疏导功能需要在校园网环境下使用，当前网络不可用。",
            "conversation_id": conv_id,
            "ttft_ms": 0, "rag_ms": 0, "retrieval_quality": 0, "retry_count": 0,
        }, ensure_ascii=False)
        yield f"event: done\ndata: {done_payload}\n\n"

    return StreamingResponse(_sse(), media_type="text/event-stream")


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """no-ai 分支：立即返回占位回复。"""
    return {
        "status": "success",
        "conversation_id": request.conversation_id or "",
        "thought": "",
        "reply": "AI 智能疏导功能需要在校园网环境下使用，当前暂未接入。",
    }
