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

## Code Style
- **Backend**: PEP8. All AI calls go through `HiAgentClient`. Endpoint response shape is always `{"thought": "...", "reply": "..."}`.
- **Frontend**: Vue 3 Composition API (`<script setup>`). Use `markdown-it` to render AI replies (via `v-html` with `renderMd()`). No linting configured — follow existing style.
