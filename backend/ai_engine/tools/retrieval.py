# ============================================================
# 【学习顺序 ⑧】tools/retrieval.py — 检索编排工具
#
# 学习目标：
#   理解如何把多个组件（retriever + reranker）封装成一个高层工具，
#   以及"质量门控"（Quality Gate）模式。
#
# 核心概念：为什么要有这一层封装？
#   Agent 不应该直接操作底层组件（PGRetriever/Reranker），
#   而应该通过工具（Tool）来使用能力，原因：
#   1. 封装复杂度：agent.py 只需要调用 tool.run(query)，
#      不用关心"先 hybrid_retrieve 再 rerank"的细节
#   2. 可替换：未来想换检索策略（换向量库、换重排模型），
#      只改这个文件，agent.py 完全不用动
#   3. 职责分离：检索逻辑的变化不影响 Agent 主循环
#
# 质量门控（Quality Gate）模式：
#   运行检索后，检查结果质量是否达标。
#   如果不达标（retrieval_quality < threshold），
#   Agent 会触发"改写查询并重试"的循环（最多2次）。
#   这是一种"自我纠错"机制，是 Agentic RAG 的核心特征之一。
# ============================================================

from __future__ import annotations

from ai_engine.config import AIEngineConfig
from ai_engine.rag.pg_retriever import PGRetriever, RetrievedChunk
from ai_engine.rag.reranker import Reranker


class RetrievalTool:
    """RAG 检索工具，Agent 通过此工具访问心理健康知识库。

    流程：混合检索（召回 top_k）→ Cross-encoder 重排序（保留 rerank_top_k）→ 质量评估
    Agent 根据质量评估结果决定是否改写查询重试。
    """

    # Tool 的 name 和 description 是 Agent 框架约定的接口
    # 在更复杂的 Agent 框架（如 LangChain）中，Agent 会读这两个字段
    # 来决定"什么时候该调用这个工具"
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
        self._threshold = config.retrieval_score_threshold  # 质量阈值（默认 0.4）

    async def run(self, query: str) -> tuple[list[RetrievedChunk], float]:
        """执行完整检索流程并返回结果和质量分数。

        【返回值解读】
        tuple[0] = chunks：精排后的知识片段列表（最多 rerank_top_k 条）
        tuple[1] = quality_score：重排后 top-1 的分数，代表"最佳匹配"的质量
                   0.0 = 没找到任何内容
                   < 0.4 = 找到了但相关性很低，可能知识库没有这方面内容
                   >= 0.4 = 找到了相关内容，质量达标

        【为什么用 top-1 分数而不是平均分数？】
        我们主要关心"最好的那条"是否足够好。
        如果最好的一条都低于阈值，说明知识库里真的没有相关内容。
        """
        chunks = await self._retriever.hybrid_retrieve(query)
        if not chunks:
            return [], 0.0                          # 没有任何检索结果

        ranked = await self._reranker.rerank(query, chunks)
        quality = ranked[0].score if ranked else 0.0   # top-1 分数作为质量指标
        return ranked, quality

    def is_quality_sufficient(self, quality_score: float) -> bool:
        """质量门控：判断检索结果是否达到质量要求。

        被 agent.py 用来决定是否需要"改写查询并重试"：
            if not tool.is_quality_sufficient(quality):
                # 质量不达标，改写查询再试一次
                state = await self._step_query_rewrite(state, is_retry=True)
        """
        return quality_score >= self._threshold

    @staticmethod
    def format_context(chunks: list[RetrievedChunk]) -> str:
        """把检索结果格式化成 LLM prompt 里的参考资料块。

        【格式示例】
        [1] 类别：情绪管理\n问题：如何缓解焦虑...\n回答：可以尝试深呼吸...（来源：q_and_a.csv）

        [2] 类别：压力应对\n...（来源：q_and_a.csv）

        这个文本块会被拼到 LLM 的 prompt 里：
            "参考以下知识库内容：\n{context}\n\n请回复用户的问题：{message}"

        LLM 看到这段参考资料，就会"基于资料回答"而不是凭空生成。
        没有检索结果时返回特殊标记，让 LLM 知道知识库里没有相关内容。
        """
        if not chunks:
            return "（未检索到相关知识库内容）"
        parts = [f"[{i+1}] {c.content}（来源：{c.source}）" for i, c in enumerate(chunks)]
        return "\n\n".join(parts)
