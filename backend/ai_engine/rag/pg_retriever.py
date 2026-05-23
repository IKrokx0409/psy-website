# ============================================================
# 【学习顺序 ④】rag/pg_retriever.py — 混合检索器
#
# 学习目标：
#   理解 RAG 中的"检索"步骤，以及为什么要"混合检索"。
#
# 核心概念：RAG（Retrieval-Augmented Generation，检索增强生成）
#   普通 LLM 只知道训练数据里的知识，无法回答"我们学校的心理咨询
#   怎么预约"这类私有知识。
#   RAG 的解决方案：先从知识库里搜出相关内容，再把搜索结果
#   拼进 prompt，让 LLM"看着资料回答"，而不是凭空编造。
#
# 两种检索方式：
#   语义检索（向量）：理解意思，能找到"措辞不同但意思相同"的内容
#                    "心情低落" 能匹配 "情绪抑郁"
#   关键词检索（BM25）：精确匹配关键词，不会被语义"误导"
#                      搜 "热线电话" 一定能找到含这个词的内容
#
# 混合检索 = 两种方式的加权融合，取长补短
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.config import AIEngineConfig
from ai_engine.rag.embedder import Embedder


@dataclass
class RetrievedChunk:
    """一条检索结果（知识库中的一个文本片段）。

    【字段说明】
    id       : 数据库主键，唯一标识这一块知识
    content  : 实际文本内容，最终会拼进 LLM 的 prompt
    source   : 来自哪个文件（如 "q_and_a.csv"）
    category : 知识类别（如 "情绪管理"、"压力应对"）
    score    : 本次检索的相关性分数，[0,1] 越高越相关
    """
    id: int
    content: str
    source: str
    category: str
    score: float


def _vec_literal(vec: list[float]) -> str:
    """把 Python 的浮点数列表转成 PostgreSQL 认识的向量字面量格式。

    Python:    [0.123456, -0.789012, ...]
    PostgreSQL: '[0.12345600,-0.78901200,...]'::vector

    这是因为 asyncpg（数据库驱动）不支持直接传向量类型的参数，
    只能把向量"嵌入"到 SQL 字符串里。
    """
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"


class PGRetriever:
    """基于 pgvector + PostgreSQL 全文检索的混合检索器。

    【架构选择：为什么用 PostgreSQL 而不是专用向量数据库（Pinecone/Weaviate）？】
    1. 知识库小（518条），用专用向量数据库杀鸡用牛刀
    2. 减少依赖：不需要额外部署和维护一个新服务
    3. 事务性：向量数据和业务数据在同一个数据库，操作一致
    4. pgvector 扩展让 PostgreSQL 支持向量运算，性能完全够用
    """

    def __init__(self, db: AsyncSession, embedder: Embedder, config: AIEngineConfig) -> None:
        self._db = db
        self._embedder = embedder
        self._alpha = config.hybrid_alpha   # 语义检索权重（默认 0.7）
        self._top_k = config.top_k          # 最多返回多少条结果

    async def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """纯语义检索：只用向量余弦相似度排序。

        【SQL 解读】
        embedding <=> '{vec}'::vector  是 pgvector 的运算符，计算余弦距离
        （注意是"距离"，值越小越相似，所以用 1 - 距离 = 相似度）

        WHERE embedding IS NOT NULL 排除没有向量的行
        ORDER BY embedding <=> ... 按距离升序（最相似的排前面）
        LIMIT :k 只取前 k 条
        """
        k = top_k or self._top_k
        vec = await self._embedder.embed(query)   # 先把查询文字向量化
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
        """混合检索：语义分数 + 关键词分数 加权融合后排序。

        【混合公式】
        最终分数 = alpha × 语义相似度 + (1-alpha) × BM25关键词分数
                 = 0.7  × 向量余弦    + 0.3      × ts_rank

        【BM25 / 全文检索（tsvector）是什么？】
        tsvector 是 PostgreSQL 内置的全文检索功能。
        BM25 是一种经典的关键词匹配算法，考虑词频和文档长度。
        ts_rank(fts, plainto_tsquery('simple', :q)) 会计算
        查询词在文档中出现的频率和重要性，返回一个相关性分数。

        【为什么混合比纯向量更好？】
        纯向量：可能会因为语义"漂移"返回意思相关但词不匹配的内容
               例如搜"热线电话"，向量可能返回"寻求帮助的方式"
        混合后：保留了对"热线电话"这个关键词的敏感性

        【实测数据（eval/eval_results.json）】
        混合检索比纯向量快 8 倍（109ms vs 840ms），精度相同
        原因：518条小知识库，BM25全扫比向量ANN索引反而更快
        """
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
