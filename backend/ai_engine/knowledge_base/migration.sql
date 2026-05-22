-- 启用 pgvector 扩展（需要 PostgreSQL >= 13 且已安装 pgvector）
CREATE EXTENSION IF NOT EXISTS vector;

-- 知识库分块表
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id          SERIAL PRIMARY KEY,
    content     TEXT        NOT NULL,
    -- 向量维度与 AIEngineConfig.embedding_dim 保持一致（bge-base-zh-v1.5 = 768）
    embedding   vector(768),
    source      VARCHAR(255),            -- 原始文件名或 URL
    category    VARCHAR(50),             -- 情绪管理 / 压力应对 / 危机干预 等
    metadata    JSONB       DEFAULT '{}',
    -- 全文检索列：'simple' 分词器支持中文字符级匹配
    -- 如需词级分词，安装 pg_jieba 后改为 'jieba'
    fts         tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW 近似最近邻索引（余弦距离），比 IVFFlat 在小数据量下更准确
CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
    ON knowledge_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- GIN 索引加速全文检索
CREATE INDEX IF NOT EXISTS knowledge_chunks_fts_idx
    ON knowledge_chunks USING gin(fts);

-- ── 持久化对话历史表 ────────────────────────────────────────────────────────
-- 解决 per-request 实例化导致内存记忆丢失的 Bug，同时支持多 Worker 部署
CREATE TABLE IF NOT EXISTS chat_history (
    id              SERIAL PRIMARY KEY,
    conversation_id VARCHAR(64)  NOT NULL,
    role            VARCHAR(16)  NOT NULL,   -- 'user' | 'assistant'
    content         TEXT         NOT NULL,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- 按 conversation_id 排序查询专用索引
CREATE INDEX IF NOT EXISTS chat_history_conv_idx
    ON chat_history (conversation_id, created_at DESC);

-- ── 请求链路追踪表 ──────────────────────────────────────────────────────────
-- 记录每次 Agent 调用的完整决策链路，用于 Bad Case 排查和性能分析
-- 面试时可直接 SELECT 出来展示：哪步慢、检索质量如何、重试了几次
CREATE TABLE IF NOT EXISTS request_traces (
    id                  SERIAL PRIMARY KEY,
    request_id          UUID         DEFAULT gen_random_uuid(),
    conversation_id     VARCHAR(64),
    crisis_level        VARCHAR(16)  DEFAULT 'none',
    query_original      TEXT,
    query_rewritten     TEXT,
    retrieval_quality   FLOAT,
    retry_count         INTEGER      DEFAULT 0,
    -- 各步骤耗时（毫秒），JSONB 方便增删字段
    step_timings        JSONB        DEFAULT '{}',
    -- 完整 thought 链路（含每步日志）
    thought             TEXT,
    total_ms            FLOAT,
    created_at          TIMESTAMPTZ  DEFAULT NOW()
);

-- 按时间倒序查询最近 N 条 trace
CREATE INDEX IF NOT EXISTS request_traces_time_idx
    ON request_traces (created_at DESC);
-- 按会话 ID 回溯历史 trace
CREATE INDEX IF NOT EXISTS request_traces_conv_idx
    ON request_traces (conversation_id, created_at DESC);
