from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.config import AIEngineConfig
from ai_engine.llm.client import LLMClient
from ai_engine.rag.embedder import Embedder
from ai_engine.rag.pg_retriever import PGRetriever, RetrievedChunk
from ai_engine.rag.reranker import Reranker
from ai_engine.tools.crisis import CrisisTool, CrisisLevel
from ai_engine.tools.memory import MemoryTool
from ai_engine.tools.retrieval import RetrievalTool


# ── 状态机 ────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    message: str
    conversation_id: str
    crisis_level: CrisisLevel
    rewritten_query: str          # Query 改写后的版本
    retrieved_chunks: list[RetrievedChunk]
    retrieval_quality: float      # [0, 1]，低于阈值触发重试
    retry_count: int              # 防止无限重试
    thought: str                  # Agent 推理过程（透传给前端展示）
    final_response: str


@dataclass
class AgentResponse:
    conversation_id: str
    thought: str
    reply: str


# ── 系统 Prompt ───────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """你是一位专业的高校心理健康助手，具备心理咨询知识，能够提供情感支持和心理健康指导。

回复原则：
1. 以检索到的知识库内容为依据，不编造信息
2. 语气温和、不评判、以倾听和支持为主
3. 遇到超出知识库范围的问题，诚实说明并建议寻求专业帮助
4. 绝对不提供诊断结论，引导用户咨询专业心理咨询师
"""

_MAX_RETRY = 2  # Query 改写最大重试次数


# ── Agent ─────────────────────────────────────────────────────────────────────

class PsychAgent:
    """心理健康 Agentic RAG 主循环。

    流程：
    1. 危机检测（前置门控，命中则跳过 RAG 直接返回协议响应）
    2. Query 改写（提升检索准确率）
    3. 混合检索 + 重排序
    4. 质量评估（不达标则重写 Query 重试，最多 _MAX_RETRY 次）
    5. 基于检索上下文生成回复
    6. 更新对话记忆
    """

    def __init__(self, config: AIEngineConfig, db: AsyncSession) -> None:
        embedder = Embedder(config)
        retriever = PGRetriever(db, embedder, config)
        reranker = Reranker(config)

        self._llm = LLMClient(config)
        self._crisis = CrisisTool(config, embedder)
        self._retrieval = RetrievalTool(retriever, reranker, config)
        # 每个 conversation_id 对应独立的 MemoryTool
        self._memories: dict[str, MemoryTool] = {}
        self._config = config

    def _get_memory(self, conversation_id: str) -> MemoryTool:
        if conversation_id not in self._memories:
            self._memories[conversation_id] = MemoryTool(self._config)
        return self._memories[conversation_id]

    async def run(self, message: str, conversation_id: str) -> AgentResponse:
        """Agent 主入口，对外接口与 HiAgentClient 保持相同签名。"""
        state: AgentState = {
            "message": message,
            "conversation_id": conversation_id,
            "crisis_level": CrisisLevel.NONE,
            "rewritten_query": message,
            "retrieved_chunks": [],
            "retrieval_quality": 0.0,
            "retry_count": 0,
            "thought": "",
            "final_response": "",
        }

        state = await self._step_crisis_detection(state)
        if state["crisis_level"] in (CrisisLevel.HIGH, CrisisLevel.MEDIUM):
            return self._build_response(state)

        state = await self._step_query_rewrite(state)

        for _ in range(_MAX_RETRY + 1):
            state = await self._step_retrieve(state)
            if self._retrieval.is_quality_sufficient(state["retrieval_quality"]):
                break
            state["retry_count"] += 1
            state = await self._step_query_rewrite(state, is_retry=True)

        state = await self._step_generate(state)
        self._update_memory(state)
        return self._build_response(state)

    # ── 步骤 ──────────────────────────────────────────────────────────────────

    async def _step_crisis_detection(self, state: AgentState) -> AgentState:
        """步骤 1：危机检测。"""
        level = await self._crisis.detect(state["message"])
        state["crisis_level"] = level
        if level != CrisisLevel.NONE:
            protocol = self._crisis.get_protocol_response(level)
            state["final_response"] = protocol or ""
            state["thought"] = f"检测到危机信号（{level.value}），跳过 RAG，执行危机协议。"
        return state

    async def _step_query_rewrite(self, state: AgentState, is_retry: bool = False) -> AgentState:
        """步骤 2：Query 改写，将口语化表达转为检索友好的关键词句。"""
        mem = self._get_memory(state["conversation_id"])
        if is_retry:
            prompt = (
                f"上一次检索质量不足（分数 {state['retrieval_quality']:.2f}）。\n"
                f"原始消息：{state['message']}\n"
                f"请换一个角度提取心理健康关键词，用于重新检索知识库。\n"
                f"只输出改写后的查询，不要解释。"
            )
        else:
            prompt = (
                f"请将以下用户消息改写为简洁的心理健康知识库检索查询，"
                f"提取核心关键词，去除口语化表达。\n"
                f"用户消息：{state['message']}\n"
                f"只输出改写后的查询，不要解释。"
            )
        rewritten = await self._llm.complete(
            system="你是信息检索专家，专注于心理健康领域。",
            messages=mem.get_messages() + [{"role": "user", "content": prompt}],
        )
        state["rewritten_query"] = rewritten.strip()
        state["thought"] += f"\n查询改写{'（重试）' if is_retry else ''}：{state['rewritten_query']}"
        return state

    async def _step_retrieve(self, state: AgentState) -> AgentState:
        """步骤 3：混合检索 + 重排序，更新 chunks 和 quality_score。"""
        chunks, quality = await self._retrieval.run(state["rewritten_query"])
        state["retrieved_chunks"] = chunks
        state["retrieval_quality"] = quality
        state["thought"] += f"\n检索质量分数：{quality:.2f}（阈值 {self._config.retrieval_score_threshold}）"
        return state

    async def _step_generate(self, state: AgentState) -> AgentState:
        """步骤 4：基于检索上下文调用 LLM 生成最终回复。"""
        mem = self._get_memory(state["conversation_id"])
        context = self._retrieval.format_context(state["retrieved_chunks"])
        user_prompt = (
            f"参考以下知识库内容：\n{context}\n\n"
            f"请回复用户的问题：{state['message']}"
        )
        messages = mem.get_messages() + [{"role": "user", "content": user_prompt}]
        response = await self._llm.complete(system=_SYSTEM_PROMPT, messages=messages)
        state["final_response"] = response
        state["thought"] += f"\n已生成回复（基于 {len(state['retrieved_chunks'])} 个检索片段）"
        return state

    # ── 辅助 ──────────────────────────────────────────────────────────────────

    def _update_memory(self, state: AgentState) -> None:
        mem = self._get_memory(state["conversation_id"])
        mem.add_turn("user", state["message"])
        mem.add_turn("assistant", state["final_response"])

    def _build_response(self, state: AgentState) -> AgentResponse:
        return AgentResponse(
            conversation_id=state["conversation_id"],
            thought=state["thought"].strip(),
            reply=state["final_response"],
        )
