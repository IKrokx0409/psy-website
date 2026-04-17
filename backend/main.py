import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from hiagent_client import HiAgentClient
from database import engine
from models import Base
from routers import announcements, treehole, admin, diary, resources, questionnaires

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

client = HiAgentClient()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = client.ask_ai(request.message, request.conversation_id)
        return {
            "status": "success",
            "conversation_id": result["conversation_id"],
            "thought": result["thought"],
            "reply": result["reply"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
