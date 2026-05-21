# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Please ignore files listed in `.claudeignore`.

## Project Overview

A mental health / psychological healing social platform for university students, built with FastAPI (backend) and Vue 3 + Vite (frontend), integrated with HITSZ HiAgent 2.0 AI agent service.

## Commands

### Backend (Python/FastAPI)
- **Start dev server**: `cd backend && uvicorn main:app --reload`
- **Install deps**: `cd backend && pip install -r requirements.txt`

### Frontend (Vue 3/Vite)
- **Start dev server**: `cd frontend && npm run dev`
- **Install deps**: `cd frontend && npm install`
- **Build production**: `cd frontend && npm run build`

> The frontend dev server proxies nothing — the Chat page hardcodes `http://127.0.0.1:8000/api/chat`. Both servers must be running simultaneously for full functionality.

## Architecture

### Backend (`backend/`)
- `main.py` — FastAPI app with a single POST `/api/chat` endpoint. Accepts `{message, conversation_id}`, returns `{status, conversation_id, thought, reply}`.
- `hiagent_client.py` — `HiAgentClient` class wrapping the HITSZ HiAgent 2.0 API. Two-step flow:
  1. `create_conversation()` — POST to `create_conversation` to get an `AppConversationID`.
  2. `ask_ai(prompt, conversation_id)` — POST to `chat_query_v2` with `ResponseMode: streaming`, parse SSE lines.
- `backend/.env` — must contain `HITSZ_API_KEY`.

### Frontend (`frontend/src/`)
- `main.js` + `App.vue` — root mount; `App.vue` wraps all pages with `<NavBar>` and a `<router-view>`. The `/chat` route gets `overflow: hidden` + full-height flex layout; all other routes scroll normally.
- `router/index.js` — routes: `/`, `/chat`, `/diary`, `/science`, `/appointment`, `/about`, `/treehouse`.
- **Views**: `Home.vue` composes multiple section components. `Chat.vue` is the full AI chat interface (self-contained, ~700 lines). Other views (`Diary`, `Science`, `Appointment`, `About`, `Treehouse`) are independent pages.
- **Components**: Section-level UI blocks used by `Home.vue` (`HeroBanner`, `QuickEntry`, `AnnouncementBoard`, `SidePanel`, `TreeholeSection`, `DiaryPreview`, `ContactSection`, `SiteFooter`) and `NavBar`.

### HiAgent API Integration (critical details)
- **Proxy path**: Must use `/api/proxy/api/v1/` prefix on `zhiwen.hitsz.edu.cn:10211` to bypass CSRF.
- **Auth**: Header `Apikey: <key>`. `UserID` must be 1–20 characters (e.g. `ikrokx_001`).
- **SSE stream parsing**: Each line is prefixed `data: `. JSON payload has `event` field:
  - `event: think_message` → accumulate into `thought`
  - `event: message` → accumulate into `reply`
  - Line `[DONE]` signals end of stream.

### Conversation Persistence (Chat.vue)
- `hiagentConvId` (the `AppConversationID` from HiAgent) is passed back on every request to continue context server-side.
- Local conversation history (messages + `hiagentConvId`) is stored in `localStorage` under key `wellbeing_conversations` as a JSON array.

## AI Engine（面试演示模式）

### 启动方式
```bash
# 必须在 psy_agent conda 环境下运行（Python 3.10）
conda run -n psy_agent uvicorn main_ai:app --reload --port 8001
# 或激活环境后：
conda activate psy_agent && cd backend && uvicorn main_ai:app --reload
```
> `main_ai.py` 与 `main.py` 共享所有业务路由，仅 `/api/chat` 替换为 PsychAgent。

### 依赖安装（首次 / 新机器）
```bash
conda activate psy_agent
pip install -r backend/requirements.txt -r backend/requirements_ai.txt
# PyTorch 用 CPU 版（无 GPU）
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### 已知环境坑（重要！）
1. **pgvector 扩展**：首次部署需用 postgres 超级用户建扩展：
   ```bash
   sudo -u postgres psql -d psy_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```
2. **SOCKS 代理阻断 LLM 调用**：WSL2 环境下 `http_proxy`/`all_proxy` 环境变量会被 httpx 自动读取，导致 DeepSeek API 请求永久卡死。已在 `ai_engine/llm/client.py` 通过 `httpx.AsyncClient(proxy=None)` 修复，勿删除。
3. **SQL 类型转换**：asyncpg 不支持 `:param::type` 语法，统一改为 `CAST(:param AS type)`。

### 知识库入库
```bash
# 文档放入 backend/ai_engine/knowledge_base/docs/
# 支持：txt / md / pdf / xlsx / csv（含伪装成 csv 的 xlsx）
conda run -n psy_agent python -m ai_engine.knowledge_base.ingest
```
当前知识库：`q_and_a.csv`（259行，518个向量块），格式：
`类别 | 问题1 | 回答1 | 问题2 | 回答2 | 关键词1 | 关键词2 | 关键词3`

### Agent 架构（`ai_engine/`）
```
agent.py          — PsychAgent 主循环（危机检测→Query改写→检索→生成）
config.py         — AIEngineConfig（LLM/Embedding/检索参数，读 .env）
llm/client.py     — LLMClient（AsyncOpenAI 封装，proxy=None）
rag/embedder.py   — Embedder（BAAI/bge-base-zh-v1.5，本地，768维）
rag/pg_retriever.py — PGRetriever（pgvector 余弦 + FTS 混合检索）
rag/reranker.py   — Reranker（cross-encoder 重排序，保留 top_k=3）
tools/crisis.py   — CrisisTool（HIGH/MEDIUM/LOW 三级危机协议）
tools/memory.py   — MemoryTool（滑动窗口对话记忆，10轮）
tools/retrieval.py — RetrievalTool（检索+重排+质量评分）
knowledge_base/   — ingest.py + migration.sql + docs/
```

### .env 必要字段
```
DATABASE_URL=postgresql+asyncpg://...
AI_LLM_PROVIDER=deepseek
AI_LLM_API_KEY=<key>
AI_LLM_MODEL=deepseek-chat
AI_LLM_BASE_URL=https://api.deepseek.com
# 可选（默认值已够用）：
# AI_EMBEDDING_MODEL=BAAI/bge-base-zh-v1.5
```

## Code Style
- **Backend**: PEP8. All AI calls go through `HiAgentClient`（正式）或 `PsychAgent`（演示）. Endpoint response shape is always `{"thought": "...", "reply": "..."}`.
- **Frontend**: Vue 3 Composition API (`<script setup>`). Use `markdown-it` to render AI replies (via `v-html` with `renderMd()`). No linting configured — follow existing style.
