import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
from hiagent_client import HiAgentClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = HiAgentClient()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = client.ask_ai(request.message, request.conversation_id)
        
        # 直接把整个字典返回给 Vue 前端
        return {
            "status": "success",
            "conversation_id": result["conversation_id"],
            "thought": result["thought"],
            "reply": result["reply"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))