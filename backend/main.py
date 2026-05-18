import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from hiagent_client import HiAgentClient
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

client = HiAgentClient()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = client.ask_ai(request.message, request.conversation_id)
        if request.user_id:
            db.add(ChatRecord(user_id=request.user_id))
            await db.commit()
        return {
            "status": "success",
            "conversation_id": result["conversation_id"],
            "thought": result["thought"],
            "reply": result["reply"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
