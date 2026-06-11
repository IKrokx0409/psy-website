import asyncio
import json as _json
import os
import threading
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from hiagent_client import HiAgentClient
from database import engine, get_db
from models import Base, ChatRecord
from routers import announcements, treehole, admin, diary, resources, questionnaires, courses, stats, tips

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时自动建表（表已存在则跳过），并迁移新增列"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(
            "ALTER TABLE resources ADD COLUMN IF NOT EXISTS resource_type VARCHAR(20) NOT NULL DEFAULT 'article'"
        ))
        await conn.execute(text(
            "ALTER TABLE resources ADD COLUMN IF NOT EXISTS file_path VARCHAR(500)"
        ))
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
_uploads_dir = os.environ.get("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "uploads"))
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


@app.get("/api/chat/stream")
async def chat_stream_endpoint(message: str, conversation_id: str = "", user_id: str = ""):
    loop = asyncio.get_running_loop()
    q: asyncio.Queue = asyncio.Queue()

    def _sse(event_type: str, data: str) -> str:
        # SSE 规范：多行内容每行都需要 "data: " 前缀，否则换行会丢失
        data_lines = '\n'.join(f'data: {line}' for line in data.split('\n'))
        return f"event: {event_type}\n{data_lines}\n\n"

    def producer():
        try:
            for event_type, data in client.stream_ask_ai(message, conversation_id or None, user_id or None):
                asyncio.run_coroutine_threadsafe(
                    q.put(_sse(event_type, data)), loop
                )
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                q.put(f"event: error\ndata: {_json.dumps({'error': str(e)})}\n\n"), loop
            )
        finally:
            asyncio.run_coroutine_threadsafe(q.put(None), loop)

    threading.Thread(target=producer, daemon=True).start()

    async def generate():
        while True:
            chunk = await q.get()
            if chunk is None:
                break
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
