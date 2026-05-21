from __future__ import annotations

from ai_engine.config import AIEngineConfig
from ai_engine.rag.pg_retriever import PGRetriever, RetrievedChunk
from ai_engine.rag.reranker import Reranker


class RetrievalTool:
    """RAG 检索工具，Agent 通过此工具访问心理健康知识库。

    流程：混合检索（召回 top_k） → Cross-encoder 重排序（保留 rerank_top_k）→ 质量评估
    Agent 根据质量评估结果决定是否改写查询重试。
    """

    name = "search_knowledge_base"
    description = "搜索心理健康知识库，返回与用户问题最相关的文档片段"

    def __init__(
        self,
        retriever: PGRetriever,
        reranker: Reranker,
        config: AIEngineConfig,
    ) -> None:
        self._retriever = retriever
        self._reranker = reranker
        self._threshold = config.retrieval_score_threshold

    async def run(self, query: str) -> tuple[list[RetrievedChunk], float]:
        """执行检索并返回 (chunks, quality_score)。

        quality_score 是 rerank 后 top-1 的分数，Agent 用它判断是否需要重试。
        """
        chunks = await self._retriever.hybrid_retrieve(query)
        if not chunks:
            return [], 0.0
        ranked = await self._reranker.rerank(query, chunks)
        quality = ranked[0].score if ranked else 0.0
        return ranked, quality

    def is_quality_sufficient(self, quality_score: float) -> bool:
        """质量门控：分数低于阈值时 Agent 应改写查询或走 fallback。"""
        return quality_score >= self._threshold

    @staticmethod
    def format_context(chunks: list[RetrievedChunk]) -> str:
        """将检索结果格式化为 prompt 中的 context 块。"""
        if not chunks:
            return "（未检索到相关知识库内容）"
        parts = [f"[{i+1}] {c.content}（来源：{c.source}）" for i, c in enumerate(chunks)]
        return "\n\n".join(parts)
