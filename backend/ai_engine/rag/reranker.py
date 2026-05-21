from __future__ import annotations

import asyncio
from ai_engine.rag.pg_retriever import RetrievedChunk
from ai_engine.config import AIEngineConfig


class Reranker:
    """Cross-encoder 重排序器。

    在初始召回（top_k=10）之后，用 cross-encoder 对 (query, chunk) 对
    重新打分，解决双塔模型召回阶段的语义误差，提升最终精度。

    推荐模型：BAAI/bge-reranker-base（中文，轻量）
    """

    def __init__(self, config: AIEngineConfig) -> None:
        self._top_k = config.rerank_top_k
        self._model = None  # 延迟加载

    def _ensure_loaded(self) -> None:
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder("BAAI/bge-reranker-base")

    async def rerank(
        self, query: str, chunks: list[RetrievedChunk], top_k: int | None = None
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []
        self._ensure_loaded()
        k = top_k or self._top_k
        pairs = [(query, c.content) for c in chunks]
        loop = asyncio.get_event_loop()
        scores = await loop.run_in_executor(None, self._model.predict, pairs)
        ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
        result = []
        for score, chunk in ranked[:k]:
            chunk.score = float(score)
            result.append(chunk)
        return result
