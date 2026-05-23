# ============================================================
# 【学习顺序 ⑤】rag/reranker.py — 精排序器
#
# 学习目标：
#   理解为什么"先粗筛再精排"比"直接精排"更高效，
#   以及"双塔模型"和"交叉编码器"的区别。
#
# 核心概念：为什么需要 Reranker（重排序）？
#
#   第一步（Embedder + PGRetriever）叫"双塔模型"：
#     ┌──────────┐        ┌──────────────────┐
#     │ 用户问题 │→embed→ │  向量 A（768维）  │
#     └──────────┘        └──────────────────┘
#                                  ↕ 余弦相似度
#     ┌──────────┐        ┌──────────────────┐
#     │ 知识片段 │→embed→ │  向量 B（768维）  │
#     └──────────┘        └──────────────────┘
#   优点：快（知识片段的向量提前算好存数据库，检索时只算一次）
#   缺点：问题和知识是"分开理解"的，可能错过细微的语义关联
#
#   第二步（Reranker）叫"交叉编码器（Cross-Encoder）"：
#     ┌─────────────────────────────────────┐
#     │  [用户问题] + [知识片段]  → 一个分数 │
#     └─────────────────────────────────────┘
#   问题和知识"放在一起"让模型联合理解，精度更高
#   缺点：慢，不能提前算，只能实时算
#
#   结合使用："双塔召回 top10，交叉精排 → top3"
#   先用快的粗筛，再用慢的在小范围内精排，兼顾速度和精度。
#
# 实测效果（来自 eval/eval_results.json）：
#   加重排后 HR@1（第一条就命中）从 42.5% 提升到 57.5%（+15pp）
# ============================================================

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
        self._top_k = config.rerank_top_k   # 精排后保留的条数（默认3）
        self._model = None                   # 延迟加载，同 Embedder 的设计

    def _ensure_loaded(self) -> None:
        """加载 cross-encoder 模型（同样使用本地缓存，不联网）。

        CrossEncoder 和 SentenceTransformer 是不同的模型架构：
        - SentenceTransformer：输入一段文字，输出一个向量
        - CrossEncoder：输入两段文字的拼接，输出一个相关性分数
        """
        if self._model is None:
            import os
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(
                "BAAI/bge-reranker-base",
                local_files_only=os.getenv("HF_HUB_OFFLINE", "0") == "1",
            )

    async def rerank(
        self, query: str, chunks: list[RetrievedChunk], top_k: int | None = None
    ) -> list[RetrievedChunk]:
        """对候选结果重新打分并按新分数排序，只返回前 top_k 条。

        【处理流程】
        1. 把 (query, chunk.content) 配对成 pairs 列表
           例如：[("我很焦虑", "焦虑是一种..."), ("我很焦虑", "压力管理方法...")]
        2. 把所有 pairs 一起丢给 cross-encoder 打分（批量处理，效率更高）
        3. 按分数降序排列，取前 top_k 条
        4. 用新分数覆盖原来的 score 字段（方便后续质量评估使用）

        【为什么用 run_in_executor？】
        原因同 embedder.py：模型推理是 CPU 密集型同步操作，
        需要放到线程池里执行，避免阻塞异步事件循环。
        """
        if not chunks:
            return []
        self._ensure_loaded()
        k = top_k or self._top_k

        # 构造 (查询, 候选文档) 对，cross-encoder 联合理解两段文字
        pairs = [(query, c.content) for c in chunks]

        loop = asyncio.get_event_loop()
        # model.predict(pairs) 返回每对的相关性分数（数组）
        scores = await loop.run_in_executor(None, self._model.predict, pairs)

        # 把分数和对应的 chunk 绑定在一起，按分数降序排列
        ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)

        result = []
        for score, chunk in ranked[:k]:
            chunk.score = float(score)  # 用精排分数覆盖粗排分数
            result.append(chunk)
        return result
