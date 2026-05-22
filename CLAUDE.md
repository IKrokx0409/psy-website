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

> The frontend dev server proxies `/api` to `http://127.0.0.1:8000`. Both servers must run simultaneously for full functionality.

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
- **Views**: `Home.vue` composes multiple section components. `Chat.vue` is the full AI chat interface (self-contained). Other views (`Diary`, `Science`, `Appointment`, `About`, `Treehouse`) are independent pages.
- **Components**: Section-level UI blocks used by `Home.vue` (`HeroBanner`, `QuickEntry`, `AnnouncementBoard`, `SidePanel`, `TreehouseSection`, `DiaryPreview`, `ContactSection`, `SiteFooter`) and `NavBar`.

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

---

## AI Engine（面试演示模式）

### 启动方式
```bash
# 必须在 psy_agent conda 环境下运行（Python 3.10）
# main_ai.py 与 main.py 共享所有业务路由，仅 /api/chat 替换为 PsychAgent
# 建议直接跑在 8000 端口，Vite proxy 无需改动
conda activate psy_agent
cd backend && uvicorn main_ai:app --reload
```

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
2. **SOCKS 代理阻断 LLM 调用**：WSL2 环境下 `http_proxy`/`all_proxy` 会被 httpx 自动读取，导致 DeepSeek API 请求永久卡死。已在 `ai_engine/llm/client.py` 通过 `httpx.AsyncClient(proxy=None)` 修复，勿删除。
3. **SQL 类型转换**：asyncpg 不支持 `:param::type` 语法，统一改为 `CAST(:param AS type)`。
4. **HuggingFace 网络检查**：新版 sentence-transformers 在每次 `SentenceTransformer()` 时会尝试请求 HF Hub 验证 adapter config，在 WSL2 下因代理问题崩溃。已通过 `.env` 设置 `HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1`，并在 `Embedder`/`Reranker` 传入 `local_files_only=True` 修复。**模型已缓存，勿删除 `~/.cache/huggingface/`。**

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
agent.py              — PsychAgent 主循环（run/stream 两入口）
config.py             — AIEngineConfig（LLM/Embedding/检索参数，读 .env）
llm/client.py         — LLMClient（AsyncOpenAI 封装，proxy=None）
rag/embedder.py       — Embedder（BAAI/bge-base-zh-v1.5，本地，768维）
rag/pg_retriever.py   — PGRetriever（pgvector 余弦 + FTS 混合检索）
rag/reranker.py       — Reranker（BAAI/bge-reranker-base，cross-encoder，top_k=3）
tools/crisis.py       — CrisisTool（HIGH/MEDIUM/LOW 三级危机协议）
tools/db_memory.py    — DBMemoryTool（PostgreSQL 持久化对话记忆，滑动窗口 10 轮）
tools/retrieval.py    — RetrievalTool（检索+重排+质量评分）
knowledge_base/       — ingest.py + migration.sql + docs/
eval/                 — golden_dataset.json + eval_retrieval.py（量化评测）
```

### .env 必要字段
```
DATABASE_URL=postgresql+asyncpg://...
AI_LLM_PROVIDER=deepseek
AI_LLM_API_KEY=<key>
AI_LLM_MODEL=deepseek-chat
AI_LLM_BASE_URL=https://api.deepseek.com
# 模型离线模式（WSL2 必须）
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

### HTTP 端点（main_ai.py）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 非流式（向后兼容） |
| GET  | `/api/chat/stream` | SSE 流式，参数：`message` + `conversation_id` |

SSE 事件格式：
```
event: thinking   → RAG 前处理进度（含 Query 改写、检索分数）
event: token      → LLM 逐字生成
event: done       → 结束，data 为 JSON：{thought, ttft_ms, rag_ms, retrieval_quality, retry_count}
event: error      → 异常，data 为 JSON：{error}
```

---

## 面试素材：四个工程优化与 Bug 修复

> 以下是对项目进行生产级审查时发现的问题及实施的优化，按优先级排序。

---

### 🐛 Bug：对话记忆在任何部署模式下都不生效

**发现过程：** 代码审查时注意到 `main_ai.py` 中 `PsychAgent` 是 per-request 实例化的：
```python
agent = PsychAgent(config=_config, db=db)  # 每次请求 new 一个新实例
```
原 `MemoryTool` 是实例变量字典（`self._memories: dict[str, MemoryTool] = {}`），每次请求新建 Agent 实例时字典为空。这意味着**多轮对话记忆在单进程、单 Worker 下就已失效**，完全不需要等到多进程场景。

**修复：** 新增 `tools/db_memory.py`，将对话状态持久化到 PostgreSQL `chat_history` 表：
- 请求开始时按 `conversation_id` 从 DB 拉取最近 N 轮历史
- 生成回复后异步写入 user + assistant 两条记录
- 服务层真正无状态，可横向扩展、直接接负载均衡

**面试话术：**
> "在 Code Review 时我发现了一个隐藏 Bug：Agent 是 per-request 实例化的，原有内存字典每次都是空的，多轮记忆根本没有生效。修复路径是将对话状态下沉到 PostgreSQL，顺带实现了服务无状态，不需要 sticky session，可以直接接负载均衡。"

**相关文件：** `ai_engine/tools/db_memory.py`，`migration.sql`（`chat_history` 表），`agent.py`

---

### 🐛 Bug：Embedder/Reranker per-request 重建，模型重复加载

**发现过程：** SSE 端点上线后实测 RAG 前处理耗时 **23s**，排查发现 `Embedder._ensure_loaded()` 是延迟加载，每次 `PsychAgent.__init__()` 都创建新的 `Embedder` 对象，`_model = None` 被重置，每次请求都重新从磁盘加载模型文件（bge-base-zh + bge-reranker-base 合计约 400MB）。

**修复：** 在 `main_ai.py` 的 `lifespan` 启动阶段将 `Embedder` 和 `Reranker` 创建为进程级单例并预热；`PsychAgent.__init__` 新增 `embedder` / `reranker` 参数支持依赖注入（测试兼容性保持不变）。

**效果：** RAG 前处理耗时 **23s → 2.6s（↓89%）**，热启动 TTFT ≈ 2.4s。

**面试话术：**
> "在 SSE 上线后实测时发现 RAG 前处理要 23 秒，排查发现 Embedding 模型每次请求都在重新从磁盘加载。修复方式是在 FastAPI 的 lifespan 钩子里做单例预热，利用依赖注入将已加载的模型传入每次请求的 Agent，延迟从 23s 降到 2.6s，降幅 89%。"

**相关文件：** `main_ai.py`（`lifespan` + `_make_agent()`），`agent.py`（`__init__` 依赖注入）

---

### ✅ 优化 1 — 量化评测集（Golden Dataset）

**背景：** 检索质量阈值 0.4 是拍脑袋定的，无法回答"为什么用混合检索+重排，而不是纯向量？"

**实现：** `backend/eval/` 目录，40 条跨类别 Query + `eval_retrieval.py` 自动评测脚本。

**评测结果（40 Query，10 类别）：**

| 策略 | HR@1 | HR@3 | HR@5 | MRR | 平均延迟 |
|------|------|------|------|-----|---------|
| A. 纯向量检索 | 42.5% | 75.0% | 77.5% | 0.596 | 840ms |
| B. 混合检索 | 42.5% | 75.0% | 77.5% | 0.596 | 109ms |
| C. 混合+重排 | **57.5%** | 72.5% | 72.5% | **0.637** | 1725ms |

**关键结论：**
- 混合检索与纯向量等精度，但快 **8x**（518 条小规模知识库下 BM25 全扫比 ANN 更快）
- 重排序将 HR@1 从 42.5% → 57.5%（↑15pp），用户看到的第一条结果更准确
- MRR = 0.637 表明期望结果平均在 top-2 以内，0.4 质量阈值有数据支撑

**运行方式：**
```bash
conda run -n psy_agent python -m eval.eval_retrieval
```

**面试话术：**
> "在上线前我构建了 40 个真实场景 Query 的黄金测试集，量化对比了三种检索策略。混合检索与纯向量等精度但快 8 倍；加重排序后 HR@1 提升了 15 个百分点。这是我选择这套复杂架构的数据依据，质量阈值 0.4 也是基于评测集的分数分布分析确定的。"

**相关文件：** `eval/golden_dataset.json`，`eval/eval_retrieval.py`，`eval/eval_results.json`

---

### ✅ 优化 2 — SSE 流式响应 + TTFT 监控

**背景：** 原 `/api/chat` 是阻塞 POST，用户需等 LLM 完整生成后才收到回复（可能 10s+），心理咨询场景下体验很差。

**实现：** 两阶段 SSE 推送 + GET 端点（兼容浏览器原生 `EventSource` API）：
- **阶段 1（阻塞约 1-2s）**：危机检测 → Query 改写 → 混合检索 → 重排 → 发 `thinking` 事件（进度摘要）
- **阶段 2（流式）**：LLM 逐 token → 每个 token 发 `token` 事件 → 结束发 `done`（含 TTFT 元数据）

**TTFT 构成（实测，热启动）：**
```
危机检测(~150ms) + Query改写-LLM(~600ms) + 混合检索(~100ms) + 重排(~300ms) + LLM首Token(~200ms)
≈ 1.3 - 2.4s（视 DeepSeek API 响应速度）
```

`done` 事件携带的元数据（前端推理摘要框展示 TTFT 徽章）：
```json
{"thought": "...", "conversation_id": "...", "ttft_ms": 2408.6, "rag_ms": 1957.5, "retrieval_quality": 0.82, "retry_count": 0}
```

前端 `Chat.vue` 变更：
- `sendMessage` 改用 `fetch` + `ReadableStream` 解析 SSE 流
- `thinking` 阶段保持 loading 动画
- `token` 阶段：逐字追加 + 闪烁光标（完成后切换 Markdown 渲染）
- 推理摘要框展示绿色 TTFT 徽章

**面试话术：**
> "我采用两阶段 SSE：RAG 管道在后台运行时，前端显示思考中动画；管道完成后立即开始流式输出。端点用 GET + Query Params，兼容浏览器原生 EventSource API，这是 SSE 的 Web 标准。热启动下 TTFT 在 2.4 秒以内，用户不会感知到完整等待。"

**相关文件：** `main_ai.py`（`/api/chat/stream` 端点），`agent.py`（`stream()` 方法），`frontend/src/views/Chat.vue`

---

### ✅ 优化 3 — 结构化链路追踪（可观测性）

**背景：** 5 步 Agentic RAG 是个"决策黑盒"，线上出现 Bad Case（胡说八道/无关回答）时无法确定是哪一步出了问题。

**实现：** 新增 `request_traces` 表，每次 Agent 调用后异步写入完整决策链路：

```sql
-- 面试时可直接展示这条查询：
SELECT crisis_level, 
       ROUND(AVG(total_ms)) AS avg_ms,
       ROUND(AVG(retrieval_quality)::numeric, 3) AS avg_quality,
       ROUND(AVG(retry_count)::numeric, 2) AS avg_retry
FROM request_traces 
GROUP BY crisis_level;
```

字段设计：
- `step_timings`（JSONB）：各步骤耗时，如 `{"crisis_ms": 150, "rewrite_ms": 620, "retrieve_ms": 95, "generate_ms": 4500}`
- `query_rewritten`：LLM 改写后的查询，可对比原始消息分析改写效果
- `retrieval_quality`：重排 top-1 分数，低于 0.4 说明知识库未覆盖该话题
- `retry_count`：改写重试次数，频繁重试说明某类 Query 需要补充知识库

**设计原则：** `_write_trace()` 用 `try/except` 静默失败，Trace 写入不影响主业务链路。

**面试话术：**
> "出现 Bad Case 时，我可以通过 conversation_id 从 request_traces 表回溯完整决策链路：改写后的查询是什么、检索分数是多少、哪一步最慢。这是我自己实现的轻量级 LLM Tracing，不依赖外部服务，数据在本地数据库，可以直接 SELECT 出来展示。"

**相关文件：** `migration.sql`（`request_traces` 表），`agent.py`（`_write_trace()` + 各步骤计时埋点）

---

## 数据库表结构一览

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `knowledge_chunks` | 知识库向量块 | `embedding vector(768)`, `fts tsvector`, `category` |
| `chat_history` | 持久化对话记忆 | `conversation_id`, `role`, `content` |
| `request_traces` | 链路追踪 | `step_timings jsonb`, `retrieval_quality`, `ttft_ms` |

索引：
- `knowledge_chunks_embedding_idx`：HNSW（余弦，m=16）
- `knowledge_chunks_fts_idx`：GIN（全文）
- `chat_history_conv_idx`：`(conversation_id, created_at DESC)`
- `request_traces_conv_idx`：`(conversation_id, created_at DESC)`

---

## Code Style
- **Backend**: PEP8. All AI calls go through `HiAgentClient`（正式）或 `PsychAgent`（演示）. Endpoint response shape is always `{"thought": "...", "reply": "..."}`.
- **Frontend**: Vue 3 Composition API (`<script setup>`). Use `markdown-it` to render AI replies (via `v-html` with `renderMd()`). No linting configured — follow existing style.
