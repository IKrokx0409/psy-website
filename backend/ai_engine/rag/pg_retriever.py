from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.config import AIEngineConfig
from ai_engine.rag.embedder import Embedder


@dataclass
class RetrievedChunk:
    id: int
    content: str
    source: str
    category: str
    score: float  # 融合后的最终分数，范围 [0, 1]


def _vec_literal(vec: list[float]) -> str:
    """将向量转为 PostgreSQL vector 字面量字符串，用于 SQL 内联。"""
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"


class PGRetriever:
    """基于 pgvector + PostgreSQL 全文检索的混合检索器。

    单次 SQL 同时执行语义检索（向量余弦距离）和关键词检索（tsvector），
    加权融合后返回，无需额外进程或服务。

    注意：PostgreSQL 中文全文检索默认使用 'simple' 分词器（字符级），
    如需词级分词需安装 pg_jieba 或 zhparser 扩展。
    """

    def __init__(self, db: AsyncSession, embedder: Embedder, config: AIEngineConfig) -> None:
        self._db = db
        self._embedder = embedder
        self._alpha = config.hybrid_alpha  # 语义权重
        self._top_k = config.top_k

    async def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """纯语义检索（向量余弦相似度）。"""
        k = top_k or self._top_k
        vec = await self._embedder.embed(query)
        vl = _vec_literal(vec)
        sql = text(f"""
            SELECT id, content,
                   COALESCE(source, '')   AS source,
                   COALESCE(category, '') AS category,
                   1 - (embedding <=> '{vl}'::vector) AS score
            FROM knowledge_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> '{vl}'::vector
            LIMIT :k
        """)
        result = await self._db.execute(sql, {"k": k})
        return [
            RetrievedChunk(
                id=row.id, content=row.content, source=row.source,
                category=row.category, score=float(row.score),
            )
            for row in result.fetchall()
        ]

    async def hybrid_retrieve(
        self,
        query: str,
        top_k: int | None = None,
        alpha: float | None = None,
    ) -> list[RetrievedChunk]:
        """混合检索：alpha * 语义分数 + (1-alpha) * BM25分数。"""
        k = top_k or self._top_k
        a = alpha if alpha is not None else self._alpha
        vec = await self._embedder.embed(query)
        vl = _vec_literal(vec)
        sql = text(f"""
            SELECT id, content,
                   COALESCE(source, '')   AS source,
                   COALESCE(category, '') AS category,
                   :alpha * (1 - (embedding <=> '{vl}'::vector)) +
                   (1 - :alpha) * ts_rank(fts, plainto_tsquery('simple', :q)) AS score
            FROM knowledge_chunks
            WHERE embedding IS NOT NULL
            ORDER BY score DESC
            LIMIT :k
        """)
        result = await self._db.execute(sql, {"alpha": a, "q": query, "k": k})
        return [
            RetrievedChunk(
                id=row.id, content=row.content, source=row.source,
                category=row.category, score=float(row.score),
            )
            for row in result.fetchall()
        ]
