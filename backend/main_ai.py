"""AI Demo 入口 — 唯一的"开关"。

学校部署：uvicorn main:app --reload
面试演示：uvicorn main_ai:app --reload

两个入口共享所有业务路由，仅 /api/chat 不同：
- main.py     → HiAgent（学校硬性要求）
- main_ai.py  → PsychAgent（Agentic RAG，面试展示）
"""

import json
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, get_db
from models import Base
from routers import (
    announcements, treehole, admin, diary,
    resources, questionnaires, courses, stats, tips,
)
from ai_engine.agent import PsychAgent, StreamEvent
from ai_engine.config import AIEngineConfig
from ai_engine.rag.embedder import Embedder
from ai_engine.rag.reranker import Reranker

load_dotenv()
_config = AIEngineConfig()

# ── 单例共享资源 ──────────────────────────────────────────────────────────────
# Embedder / Reranker 在进程级单例化：模型文件只从磁盘加载一次（约 2-3s），
# 后续所有请求复用同一实例。PsychAgent 仍可 per-request 实例化（无状态）。
_embedder: Embedder | None = None
_reranker: Reranker | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _embedder, _reranker

    # 1. DB 迁移
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        migration_path = os.path.join(
            os.path.dirname(__file__),
            "ai_engine", "knowledge_base", "migration.sql",
        )
        migration_sql = open(migration_path, encoding="utf-8").read()
        for stmt in migration_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                await conn.execute(text(stmt))

    # 2. 预热 Embedding / Reranker 模型（在事件循环中异步加载，避免阻塞首个请求）
    import asyncio
    _embedder = Embedder(_config)
    _reranker = Reranker(_config)

    # 用线程池预热（lazy load → 第一次 embed 触发磁盘加载）
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _embedder._ensure_loaded)
    await loop.run_in_executor(None, _reranker._ensure_loaded)
    print("✅ AI Engine 预热完成（Embedder + Reranker 已加载）")

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

_uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


def _make_agent(db: AsyncSession) -> PsychAgent:
    """创建 PsychAgent，注入进程级单例 Embedder/Reranker（已预热，无加载延迟）。"""
    return PsychAgent(config=_config, db=db, embedder=_embedder, reranker=_reranker)


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """非流式接口（向后兼容）。"""
    agent = _make_agent(db)
    try:
        result = await agent.run(
            message=request.message,
            conversation_id=request.conversation_id or "",
        )
        return {
            "status": "success",
            "conversation_id": result.conversation_id,
            "thought": result.thought,
            "reply": result.reply,
        }
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=f"未实现：{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/stream")
async def chat_stream_endpoint(
    message: str = Query(..., description="用户消息"),
    conversation_id: str = Query(default="", description="会话 ID，空则新建"),
    db: AsyncSession = Depends(get_db),
):
    """SSE 流式接口 — 两阶段推送（RAG进度 + LLM逐token）。

    使用 GET + QueryString，兼容浏览器原生 EventSource API。

    SSE 事件格式：
      event: thinking\\ndata: <思考进度文本>\\n\\n
      event: token\\ndata: <LLM生成的token>\\n\\n
      event: done\\ndata: <JSON元数据>\\n\\n

    元数据字段：thought / conversation_id / ttft_ms / rag_ms / retrieval_quality / retry_count
    """
    agent = _make_agent(db)

    async def sse_generator() -> AsyncIterator[str]:
        try:
            async for event in agent.stream(
                message=message,
                conversation_id=conversation_id,
            ):
                # SSE 格式：event: <type>\ndata: <payload>\n\n
                yield f"event: {event.event}\ndata: {event.data}\n\n"
        except Exception as e:
            err = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"event: error\ndata: {err}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # 关闭 nginx 缓冲，确保实时推送
        },
    )
