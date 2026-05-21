"""AI Demo 入口 — 唯一的"开关"。

学校部署：uvicorn main:app --reload
面试演示：uvicorn main_ai:app --reload

两个入口共享所有业务路由，仅 /api/chat 不同：
- main.py     → HiAgent（学校硬性要求）
- main_ai.py  → PsychAgent（Agentic RAG，面试展示）
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
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
from ai_engine.agent import PsychAgent
from ai_engine.config import AIEngineConfig

load_dotenv()
_config = AIEngineConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        migration_path = os.path.join(
            os.path.dirname(__file__),
            "ai_engine", "knowledge_base", "migration.sql",
        )
        migration_sql = open(migration_path, encoding="utf-8").read()
        # 逐条执行，避免 asyncpg 不支持多语句
        for stmt in migration_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                await conn.execute(text(stmt))
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


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    agent = PsychAgent(config=_config, db=db)
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
