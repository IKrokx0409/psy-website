# 心灵驿站 — 高校心理健康平台

> 面向高校学生的心理健康社交平台，FastAPI 后端 + Vue 3 前端，集成自研 **PsychAgent（Agentic RAG）** AI 引擎。

---

## 目录

- [快速启动](#快速启动)
- [项目文件结构](#项目文件结构)
- [AI Engine 架构图](#ai-engine-架构图)
- [一次请求的完整数据流](#一次请求的完整数据流)
- [数据库表结构](#数据库表结构)
- [文件索引速查表](#文件索引速查表)

---

## 快速启动

### 正式部署模式（HiAgent）
```bash
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

### 面试演示模式（PsychAgent / AI Engine）
```bash
conda activate psy_agent
cd backend && uvicorn main_ai:app --reload
cd frontend && npm run dev
```

### 知识库入库（首次/新增文档）
```bash
# 将文档放入 backend/ai_engine/knowledge_base/docs/
conda run -n psy_agent python -m ai_engine.knowledge_base.ingest
```

> 前端 dev server 通过 `/api` 代理到 `http://127.0.0.1:8000`，两个服务必须同时运行。

---

## 项目文件结构

```
psy_website/
├── README.md                    ← 本文档
├── CLAUDE.md                    ← Claude Code 工程指南（项目规范/坑点/面试素材）
│
├── backend/                     ← Python / FastAPI 后端
│   ├── main.py                  ← 正式入口：HiAgent 版 /api/chat
│   ├── main_ai.py               ← 演示入口：PsychAgent 版 /api/chat + /api/chat/stream
│   ├── database.py              ← SQLAlchemy 异步引擎 + get_db 依赖
│   ├── models.py                ← ORM 模型（Announcement/DiaryEntry/TreeholePost 等）
│   ├── schemas.py               ← Pydantic 请求/响应 Schema
│   ├── hiagent_client.py        ← HiAgent 2.0 API 封装（学校正式部署用）
│   ├── requirements.txt         ← 正式部署依赖
│   ├── requirements_ai.txt      ← AI Engine 额外依赖
│   ├── seed.py                  ← 数据库初始种子数据
│   ├── migrate_announcements.py ← 公告数据迁移脚本
│   ├── .env                     ← 环境变量（不入库）
│   │
│   ├── routers/                 ← 业务 API 路由（main.py 和 main_ai.py 共享）
│   │   ├── announcements.py     ← 公告增删改查 /api/announcements
│   │   ├── treehole.py          ← 树洞帖子 /api/treehole（匿名发帖/点赞/举报）
│   │   ├── diary.py             ← 心情日记 /api/diary（含 HiAgent 情感分析）
│   │   ├── admin.py             ← 教师管理后台 /api/admin（树洞审核/公告管理）
│   │   ├── resources.py         ← 心理资源库 /api/resources
│   │   ├── questionnaires.py    ← 心理测评问卷 /api/questionnaires
│   │   ├── courses.py           ← 心理课程中心 /api/courses
│   │   ├── stats.py             ← 班级数据统计 /api/stats
│   │   └── tips.py              ← 每日心理小贴士 /api/tips
│   │
│   ├── ai_engine/               ← ★ 自研 AI 引擎（PsychAgent）
│   │   ├── __init__.py
│   │   ├── agent.py             ← PsychAgent 主循环（五步状态机 + 流式/非流式双入口）
│   │   ├── config.py            ← AIEngineConfig（全部超参读 .env，统一配置入口）
│   │   │
│   │   ├── llm/                 ← LLM 调用层
│   │   │   └── client.py        ← LLMClient（AsyncOpenAI 封装，供应商无关，proxy=None）
│   │   │
│   │   ├── rag/                 ← 检索增强生成（RAG）层
│   │   │   ├── embedder.py      ← Embedder（BAAI/bge-base-zh-v1.5，768维，本地推理）
│   │   │   ├── pg_retriever.py  ← PGRetriever（pgvector 余弦 + tsvector BM25 混合检索）
│   │   │   └── reranker.py      ← Reranker（BAAI/bge-reranker-base，cross-encoder 精排）
│   │   │
│   │   ├── tools/               ← Agent 工具集
│   │   │   ├── crisis.py        ← CrisisTool（关键词规则层 + 语义余弦双重危机检测）
│   │   │   ├── db_memory.py     ← DBMemoryTool（PostgreSQL 持久化对话记忆，滑动窗口）
│   │   │   ├── retrieval.py     ← RetrievalTool（编排检索→重排→质量评分→格式化 context）
│   │   │   └── memory.py        ← MemoryTool（旧版内存记忆，已废弃，保留供对比）
│   │   │
│   │   └── knowledge_base/      ← 知识库管理
│   │       ├── ingest.py        ← KnowledgeBaseIngestor（离线入库流水线）
│   │       ├── migration.sql    ← DB Schema DDL（3张表 + 4个索引）
│   │       └── docs/            ← 原始知识文档目录
│   │           └── q_and_a.csv  ← 心理健康 Q&A（259行→518向量块，已入库）
│   │
│   ├── eval/                    ← 检索评测层
│   │   ├── golden_dataset.json  ← 40条黄金 Query（10类别，手工标注）
│   │   ├── eval_retrieval.py    ← 自动评测脚本（HR@K / MRR / 延迟对比）
│   │   └── eval_results.json    ← 最新评测结果快照
│   │
│   ├── data/
│   │   └── nicknames.py         ← 树洞匿名昵称词库
│   │
│   └── uploads/                 ← 用户上传文件目录（运行时自动创建）
│
└── frontend/                    ← Vue 3 + Vite 前端
    ├── index.html               ← HTML 入口
    ├── vite.config.js           ← Vite 配置（含 /api 反向代理）
    ├── package.json             ← 依赖声明
    │
    └── src/
        ├── main.js              ← Vue 应用挂载入口
        ├── App.vue              ← 根组件（NavBar + router-view 布局）
        ├── style.css            ← 全局样式
        │
        ├── router/
        │   └── index.js         ← 路由表（/ /chat /diary /science /appointment /about /treehouse 等）
        │
        ├── api/                 ← 前端 API 封装层
        │   ├── http.js          ← axios 实例（baseURL + 请求拦截）
        │   ├── announcements.js ← 公告接口
        │   ├── diary.js         ← 日记接口
        │   ├── treehole.js      ← 树洞接口
        │   ├── courses.js       ← 课程接口
        │   ├── questionnaires.js← 问卷接口
        │   ├── resources.js     ← 资源接口
        │   ├── stats.js         ← 统计接口
        │   ├── tips.js          ← 贴士接口
        │   └── admin.js         ← 管理后台接口
        │
        ├── composables/         ← Vue 组合式逻辑复用
        │   ├── useAuth.js       ← 用户身份（角色/Token）状态管理
        │   └── useUserId.js     ← 匿名用户 ID 生成与持久化
        │
        ├── components/          ← 可复用 UI 组件（首页各区块）
        │   ├── NavBar.vue           ← 顶部导航栏（全站共享）
        │   ├── HeroBanner.vue       ← 首页英雄区
        │   ├── QuickEntry.vue       ← 功能快速入口卡片
        │   ├── AnnouncementBoard.vue← 公告栏
        │   ├── SidePanel.vue        ← 侧边栏（贴士/活动）
        │   ├── TreehouseSection.vue ← 首页树洞预览区
        │   ├── DiaryPreview.vue     ← 首页日记预览区
        │   ├── OnlineResources.vue  ← 在线资源展示
        │   ├── ClassStats.vue       ← 班级心理统计图表
        │   ├── ContactSection.vue   ← 联系方式区块
        │   └── SiteFooter.vue       ← 页脚
        │
        └── views/               ← 页面级视图（路由对应）
            ├── Home.vue             ← 首页（组合各 Section 组件）
            ├── Chat.vue             ← ★ AI 对话页（SSE 流式 + 历史管理）
            ├── Diary.vue            ← 心情日记页
            ├── Science.vue          ← 心理科普页
            ├── Appointment.vue      ← 预约咨询页
            ├── About.vue            ← 关于我们页
            ├── Treehouse.vue        ← 树洞社区页
            ├── Login.vue            ← 登录页
            ├── CourseCenter.vue     ← 课程中心页
            ├── ClassHome.vue        ← 班级主页（教师视角）
            ├── TeacherPanel.vue     ← 教师管理面板
            ├── AnnouncementList.vue ← 公告列表页
            ├── AnnouncementDetail.vue← 公告详情页
            ├── ResourceDetail.vue   ← 资源详情页
            ├── GroupDetail.vue      ← 小组详情页
            ├── DiscussionDetail.vue ← 讨论详情页
            └── AssignmentDetail.vue ← 作业详情页
```

---

## AI Engine 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HTTP 接入层                                        │
│                                                                              │
│  main_ai.py — FastAPI 应用入口                                               │
│  ├─ lifespan()       启动时建表(migration.sql) + 预热 Embedder/Reranker      │
│  ├─ POST /api/chat   非流式接口（向后兼容 HiAgent 版本）                     │
│  ├─ GET /api/chat/stream  SSE 流式接口（浏览器 EventSource 兼容）            │
│  └─ _make_agent()    工厂方法，注入进程级单例 Embedder/Reranker              │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ 每次请求 new 一个（无状态）
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Agent 核心（agent.py）                                │
│                                                                              │
│  PsychAgent — 五步状态机主循环                                               │
│                                                                              │
│  AgentState (TypedDict)                                                      │
│  message → crisis_level → rewritten_query → retrieved_chunks                │
│         → retrieval_quality → retry_count → thought → final_response        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────┐               │
│  │  Step 1  危机检测      CrisisTool.detect()               │               │
│  │          ↓ HIGH/MEDIUM → 直接返回协议响应，跳过 RAG       │               │
│  │  Step 2  Query 改写   LLMClient.complete() × N次重试     │               │
│  │  Step 3  混合检索     RetrievalTool.run()                 │               │
│  │          ↓ quality < 0.4 → 回到 Step 2 重写（最多2次）   │               │
│  │  Step 4  LLM 生成     LLMClient.complete() / .stream()   │               │
│  │  Step 5  持久化       DBMemoryTool.save_turn() × 2        │               │
│  │          + 链路写入   _write_trace() → request_traces     │               │
│  └──────────────────────────────────────────────────────────┘               │
│                                                                              │
│  run()    → 阻塞等待完整回复  → AgentResponse                               │
│  stream() → 两阶段 SSE 生成器 → Iterator[StreamEvent]                       │
│             阶段1: RAG前处理 → thinking事件                                  │
│             阶段2: 逐token流 → token事件 → done事件(含TTFT元数据)            │
└──────┬───────────────┬──────────────────┬────────────────────────────────────┘
       │               │                  │
       ▼               ▼                  ▼
┌──────────────┐ ┌─────────────────┐ ┌──────────────────────────────────────┐
│   LLM 层     │ │    Tools 层      │ │              RAG 层                   │
│              │ │                 │ │                                        │
│ llm/         │ │ tools/crisis.py │ │ rag/embedder.py — Embedder            │
│ client.py    │ │                 │ │ ├─ 模型：BAAI/bge-base-zh-v1.5(768维) │
│              │ │ CrisisTool      │ │ ├─ 延迟加载 + lifespan 预热           │
│ LLMClient    │ │ ├─ 关键词规则层  │ │ └─ embed() / embed_batch()           │
│              │ │ │  11个高危词   │ │                                        │
│ complete()   │ │ └─ 语义相似层   │ │ rag/pg_retriever.py — PGRetriever     │
│ stream()     │ │    余弦相似度   │ │ ├─ hybrid_retrieve()                  │
│              │ │    5句锚点文本  │ │ │  α×向量余弦+(1-α)×BM25(tsvector)   │
│ 供应商无关   │ │                 │ │ │  单条 SQL，无额外服务               │
│ AsyncOpenAI  │ │ tools/          │ │ └─ retrieve() 纯向量检索              │
│ proxy=None   │ │ retrieval.py    │ │                                        │
│ (绕SOCKS Bug)│ │                 │ │ rag/reranker.py — Reranker            │
│              │ │ RetrievalTool   │ │ ├─ BAAI/bge-reranker-base            │
│ DeepSeek API │ │ ├─ run()        │ │ │  (cross-encoder 精排)               │
│ (兼容OpenAI  │ │ │  hybrid→      │ │ ├─ 延迟加载 + lifespan 预热           │
│ 协议可切换)  │ │ │  rerank→      │ │ └─ rerank() top10→top3               │
│              │ │ │  quality      │ │                                        │
└──────────────┘ │ └─ format_      │ └──────────────────────────────────────┘
                 │   context()     │
                 │                 │
                 │ tools/          │
                 │ db_memory.py    │
                 │                 │
                 │ DBMemoryTool    │
                 │ ├─ load()       │
                 │ │  SELECT最近   │
                 │ │  N轮历史      │
                 │ ├─ get_         │
                 │ │  messages()   │
                 │ └─ save_turn()  │
                 │    异步写DB     │
                 └─────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PostgreSQL 数据库（3张 AI 表）                           │
│                                                                              │
│  knowledge_chunks              chat_history          request_traces          │
│  ────────────────              ────────────          ──────────────────      │
│  id SERIAL PK                  id SERIAL PK          id SERIAL PK            │
│  content TEXT                  conversation_id       request_id UUID         │
│  embedding vector(768) ←Embed  role user/assistant   conversation_id         │
│  source VARCHAR                content TEXT          crisis_level            │
│  category VARCHAR              created_at            query_original          │
│  fts tsvector GENERATED ←BM25 [索引] conv+time      query_rewritten         │
│  metadata JSONB                                      retrieval_quality       │
│  [索引] HNSW cosine(m=16)                           retry_count             │
│  [索引] GIN(fts)                                    step_timings JSONB      │
│                                                      thought TEXT            │
│                                                      total_ms FLOAT          │
└─────────────────────────────────────────────────────────────────────────────┘
                         ▲
                         │ 离线入库（一次性）
┌─────────────────────────────────────────────────────────────────────────────┐
│                   知识库入库流水线（knowledge_base/）                         │
│                                                                              │
│  ingest.py — KnowledgeBaseIngestor                                          │
│  ├─ ingest_directory()  递归扫描 docs/ 目录                                  │
│  ├─ ingest_file()       txt/md/pdf → 滑动窗口分块(512/64) → embed → INSERT  │
│  └─ _ingest_qa_spreadsheet() xlsx/csv → Q&A格式每行2块 → embed → INSERT    │
│                                                                              │
│  migration.sql   建表 DDL + pgvector 扩展 + 4个索引                         │
│  docs/q_and_a.csv  259行原始数据 → 518个向量块（已入库）                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    评测层（eval/）                                            │
│                                                                              │
│  golden_dataset.json   40条黄金 Query（10类别，手工标注相关文档）             │
│  eval_retrieval.py     自动评测脚本，对比三种策略                             │
│  eval_results.json     最新评测结果快照                                       │
│                                                                              │
│  策略对比结果（40 Query，10类别）：                                           │
│  ┌──────────────┬───────┬───────┬───────┬───────┬──────────┐               │
│  │ 策略         │ HR@1  │ HR@3  │ HR@5  │  MRR  │ 平均延迟 │               │
│  ├──────────────┼───────┼───────┼───────┼───────┼──────────┤               │
│  │ A. 纯向量    │ 42.5% │ 75.0% │ 77.5% │ 0.596 │  840ms   │               │
│  │ B. 混合      │ 42.5% │ 75.0% │ 77.5% │ 0.596 │  109ms   │               │
│  │ C. 混合+重排 │ 57.5% │ 72.5% │ 72.5% │ 0.637 │ 1725ms   │               │
│  └──────────────┴───────┴───────┴───────┴───────┴──────────┘               │
│  结论：混合比纯向量快 8x；重排将 HR@1 提升 15pp，质量阈值 0.4 有数据支撑     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    配置层（config.py）                                        │
│                                                                              │
│  AIEngineConfig (dataclass, 读 .env)                                        │
│  ├─ LLM:       provider / api_key / model / base_url                        │
│  ├─ Embedding: model=BAAI/bge-base-zh-v1.5, dim=768                         │
│  ├─ 检索:      top_k=10, rerank_top_k=3, threshold=0.4, alpha=0.7           │
│  ├─ 记忆:      max_history_turns=10 (滑动窗口)                               │
│  └─ 危机词:    11个高危关键词（规则层种子）                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 一次请求的完整数据流

```
用户消息
    │
    ▼
main_ai.py  GET /api/chat/stream  (浏览器 EventSource)
    │
    ├─ _make_agent()  注入预热好的 Embedder/Reranker 进程级单例
    │
    ▼
PsychAgent.stream()
    │
    ├─ [1] DBMemoryTool.load()
    │       └─ SELECT 最近 10 轮对话历史 FROM chat_history
    │
    ├─ [2] CrisisTool.detect()
    │       ├─ 关键词规则层（11个高危词，毫秒级）→ 无命中
    │       └─ 语义层：Embedder.embed(消息) → 余弦 vs 5句锚点 → < 0.82，通过
    │
    ├─ ──→ yield StreamEvent("thinking", "危机检测通过...")   ——→ 前端 loading
    │
    ├─ [3] LLMClient.complete()   Query 改写：口语化表达 → 检索友好关键词
    │
    ├─ [4] RetrievalTool.run()
    │       ├─ PGRetriever.hybrid_retrieve()
    │       │   └─ 单 SQL：α×向量余弦 + (1-α)×ts_rank(BM25) → top 10
    │       └─ Reranker.rerank()
    │           └─ cross-encoder 对 (query, chunk) 对重新打分 → top 3
    │
    ├─ quality >= 0.4？  否 → 重写 → 重检索（最多重试 2 次）
    │
    ├─ ──→ yield StreamEvent("thinking", "检索质量 0.82 ...")  ——→ 前端更新
    │
    ├─ [5] LLMClient.stream()   基于 context 调用 LLM，逐 token 生成
    │       └─ ──→ yield StreamEvent("token", "心理...") × N  ——→ 前端逐字显示
    │
    ├─ [6] DBMemoryTool.save_turn("user", ...)
    │       DBMemoryTool.save_turn("assistant", ...)
    │       └─ INSERT INTO chat_history × 2
    │
    ├─ [7] _write_trace()   异步静默写入，失败不影响主流程
    │       └─ INSERT INTO request_traces (step_timings JSONB, ...)
    │
    └─ ──→ yield StreamEvent("done", {ttft_ms, rag_ms, retrieval_quality, ...})
```

---

## 数据库表结构

### AI Engine 专属表（migration.sql）

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `knowledge_chunks` | 知识库向量块 | `embedding vector(768)`, `fts tsvector`, `category` |
| `chat_history` | 持久化对话记忆 | `conversation_id`, `role`, `content`, `created_at` |
| `request_traces` | 全链路追踪 | `step_timings jsonb`, `retrieval_quality`, `ttft_ms`, `query_rewritten` |

**索引：**
- `knowledge_chunks_embedding_idx` — HNSW（余弦，m=16，ef=64）
- `knowledge_chunks_fts_idx` — GIN（全文检索）
- `chat_history_conv_idx` — `(conversation_id, created_at DESC)`
- `request_traces_conv_idx` — `(conversation_id, created_at DESC)`

### 业务表（models.py / SQLAlchemy ORM）

| 表名 | 用途 |
|------|------|
| `announcements` | 公告（标题/正文/标签/置顶） |
| `diary_entries` | 用户心情日记（含情感分析结果） |
| `treehole_posts` | 树洞匿名帖（待审核/已发布/已拒绝） |
| `treehole_likes` | 帖子点赞记录 |

---

## 文件索引速查表

### 后端 AI Engine

| 文件 | 职责一句话 |
|------|-----------|
| `main_ai.py` | 应用入口：lifespan预热 + 两个HTTP端点（非流/SSE）+ 路由装配 |
| `ai_engine/config.py` | 全局配置：所有超参（LLM/Embedding/检索/危机词）统一读 `.env` |
| `ai_engine/agent.py` | Agent主脑：五步状态机 + 流式/非流式双入口 + Trace写入 |
| `ai_engine/llm/client.py` | LLM封装：供应商无关，`proxy=None` 绕过WSL2 SOCKS代理Bug |
| `ai_engine/rag/embedder.py` | 向量化：BAAI/bge-base-zh-v1.5，延迟加载，进程级单例 |
| `ai_engine/rag/pg_retriever.py` | 混合检索器：单条SQL融合向量余弦 + tsvector BM25 |
| `ai_engine/rag/reranker.py` | 精排器：bge-reranker-base cross-encoder，top10→top3 |
| `ai_engine/tools/crisis.py` | 危机门控：关键词规则层 + 余弦语义层，双重保险 |
| `ai_engine/tools/db_memory.py` | 持久化记忆：PostgreSQL存对话历史，修复per-request内存丢失Bug |
| `ai_engine/tools/retrieval.py` | 检索编排：调retriever→reranker→质量评分→格式化context |
| `ai_engine/knowledge_base/ingest.py` | 离线入库：txt/md/pdf/xlsx/csv → 分块 → embed → INSERT |
| `ai_engine/knowledge_base/migration.sql` | DB Schema：3张表 + 4个索引（HNSW/GIN/B-tree） |
| `eval/golden_dataset.json` | 黄金集：40条标注Query，支撑检索策略选取和阈值设定 |
| `eval/eval_retrieval.py` | 评测脚本：自动对比纯向量/混合/混合+重排三种策略 |

### 后端业务层

| 文件 | 职责一句话 |
|------|-----------|
| `main.py` | 正式部署入口（HiAgent版），与main_ai.py共享所有业务路由 |
| `database.py` | SQLAlchemy异步引擎 + `get_db` FastAPI依赖 |
| `models.py` | ORM模型定义（Announcement / DiaryEntry / TreeholePost等） |
| `schemas.py` | Pydantic Schema（请求体/响应体类型验证） |
| `hiagent_client.py` | HiAgent 2.0 API封装（两步流：create_conversation → chat_query_v2） |
| `routers/announcements.py` | 公告CRUD + 置顶/标签管理 |
| `routers/treehole.py` | 树洞匿名发帖/点赞/举报/分类筛选 |
| `routers/diary.py` | 日记CRUD + HiAgent情感分析 |
| `routers/admin.py` | 教师专属：树洞审核 + 公告管理（`X-Role: teacher` 鉴权） |
| `routers/resources.py` | 心理资源库（视频/文章/工具）的增删查 |
| `routers/questionnaires.py` | 心理测评问卷与作答记录 |
| `routers/courses.py` | 心理课程、讨论组、作业管理 |
| `routers/stats.py` | 班级心理健康数据统计聚合 |
| `routers/tips.py` | 每日心理健康小贴士（随机/按日期） |

### 前端

| 文件/目录 | 职责一句话 |
|----------|-----------|
| `src/main.js` | Vue应用挂载，注册 router / markdown-it |
| `src/App.vue` | 根组件：全局NavBar + router-view（/chat路由特殊布局处理） |
| `src/router/index.js` | 路由表，定义所有页面路径映射 |
| `src/api/http.js` | axios基础实例，统一baseURL和请求拦截 |
| `src/api/*.js` | 各业务模块接口函数（与后端路由一一对应） |
| `src/composables/useAuth.js` | 用户角色/登录状态响应式管理 |
| `src/composables/useUserId.js` | 匿名用户ID（localStorage持久化） |
| `src/views/Chat.vue` | ★ AI对话页：SSE流式接收 + 逐字渲染 + 对话历史localStorage管理 |
| `src/views/Home.vue` | 首页：组合所有Section组件 |
| `src/views/Treehouse.vue` | 树洞社区：发帖/点赞/举报/分类筛选 |
| `src/views/Diary.vue` | 心情日记：CRUD + AI情感分析展示 |
| `src/components/NavBar.vue` | 顶部导航（全站共享，含登录状态） |
| `src/components/HeroBanner.vue` | 首页英雄区大图 |
| `src/components/AnnouncementBoard.vue` | 首页公告轮播 |
| `src/components/ClassStats.vue` | 班级心理数据图表（Chart.js） |

---

## 关键设计决策

| 决策 | 原因 |
|------|------|
| Embedder/Reranker 进程级单例 | 模型文件约400MB，per-request加载导致RAG耗时23s，单例后降至2.6s（↓89%） |
| DBMemoryTool 替代内存 MemoryTool | per-request实例化导致内存字典每次为空，对话记忆完全失效（已修复Bug） |
| `proxy=None` in LLMClient | WSL2下httpx自动读取SOCKS代理环境变量，导致DeepSeek API请求永久卡死 |
| `HF_HUB_OFFLINE=1` | WSL2网络环境下sentence-transformers启动时尝试访问HF Hub会崩溃 |
| SSE用GET端点 | 浏览器原生EventSource API只支持GET，POST需要polyfill |
| 混合检索而非纯ANN | 518条小规模知识库下BM25全扫比ANN更快（109ms vs 840ms），精度持平 |
| Cross-encoder重排 | 双塔模型召回阶段语义误差大，重排将HR@1从42.5%提升至57.5% |
| `_write_trace()` try/except静默 | Trace写入失败不应中断用户的对话回复 |
