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
