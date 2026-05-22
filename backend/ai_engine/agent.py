from __future__ import annotations

import time
from dataclasses import dataclass
from typing import AsyncIterator, TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.config import AIEngineConfig
from ai_engine.llm.client import LLMClient
from ai_engine.rag.embedder import Embedder
from ai_engine.rag.pg_retriever import PGRetriever, RetrievedChunk
from ai_engine.rag.reranker import Reranker
from ai_engine.tools.crisis import CrisisTool, CrisisLevel
from ai_engine.tools.db_memory import DBMemoryTool
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


@dataclass
class StreamEvent:
    """SSE 流式传输的单个事件。

    event 类型：
      thinking  — RAG 前处理进度（危机检测/改写/检索，全部完成后发一次）
      token     — LLM 生成的逐字 token
      done      — 流结束，携带 thought / conversation_id / ttft_ms 元数据
    """
    event: str      # thinking | token | done
    data: str


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
    """心理健康 Agentic RAG 主循环（无状态版本）。

    原有 MemoryTool 使用内存内 deque，在 per-request 实例化模式下每次请求都
    丢失历史（真实 Bug）。现改为 DBMemoryTool，将对话状态持久化到 PostgreSQL：
    - 服务层真正无状态，可直接接负载均衡 / 多 Worker 部署
    - 每次请求开始时从 DB 拉取最近 N 轮历史
    - 生成回复后异步写入 DB

    流程：
    1. 危机检测（前置门控，命中则跳过 RAG 直接返回协议响应）
    2. Query 改写（提升检索准确率）
    3. 混合检索 + 重排序
    4. 质量评估（不达标则重写 Query 重试，最多 _MAX_RETRY 次）
    5. 基于检索上下文生成回复
    6. 持久化对话记忆到 DB
    """

    def __init__(
        self,
        config: AIEngineConfig,
        db: AsyncSession,
        embedder: Embedder | None = None,
        reranker: Reranker | None = None,
    ) -> None:
        # 优先使用外部注入的单例（main_ai.py 在启动时预热），
        # 否则新建（测试脚本、单元测试场景兼容）
        _embedder = embedder or Embedder(config)
        _reranker = reranker or Reranker(config)

        retriever = PGRetriever(db, _embedder, config)

        self._llm = LLMClient(config)
        self._crisis = CrisisTool(config, _embedder)
        self._retrieval = RetrievalTool(retriever, _reranker, config)
        self._config = config
        self._db = db

    async def run(self, message: str, conversation_id: str) -> AgentResponse:
        """Agent 主入口（非流式），对外接口与 HiAgentClient 保持相同签名。"""
        # 每次请求创建独立的 DBMemoryTool，从 DB 加载历史
        mem = DBMemoryTool(self._db, conversation_id, self._config)
        await mem.load()

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
            await self._persist_turn(mem, message, state["final_response"])
            return self._build_response(state)

        state = await self._step_query_rewrite(state, mem)

        for _ in range(_MAX_RETRY + 1):
            state = await self._step_retrieve(state)
            if self._retrieval.is_quality_sufficient(state["retrieval_quality"]):
                break
            state["retry_count"] += 1
            state = await self._step_query_rewrite(state, mem, is_retry=True)

        state = await self._step_generate(state, mem)
        await self._persist_turn(mem, message, state["final_response"])
        return self._build_response(state)

    async def stream(
        self, message: str, conversation_id: str
    ) -> AsyncIterator[StreamEvent]:
        """Agent 流式入口 — 两阶段 SSE。

        阶段 1（阻塞，约 1-1.5s）：
          危机检测 → Query 改写 → 混合检索 → 重排序
          → 发送一个 thinking 事件（进度摘要，前端显示"思考中"动画）

        阶段 2（流式）：
          LLM 逐 token 生成 → 每个 token 作为 token 事件推送
          → 最终发送 done 事件（含 thought / TTFT 元数据）

        TTFT（首字时延）= 危机检测 + Query改写 + 检索 + 重排 + LLM首token
        """
        t_start = time.perf_counter()

        mem = DBMemoryTool(self._db, conversation_id, self._config)
        await mem.load()

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

        # ── 阶段 1：危机检测 ──────────────────────────────────────────────────
        state = await self._step_crisis_detection(state)
        if state["crisis_level"] in (CrisisLevel.HIGH, CrisisLevel.MEDIUM):
            # 危机场景：跳过 RAG，直接流式返回协议响应（逐字发送）
            await self._persist_turn(mem, message, state["final_response"])
            yield StreamEvent("thinking", state["thought"])
            for char in state["final_response"]:
                yield StreamEvent("token", char)
            yield StreamEvent("done", f"crisis:{state['crisis_level'].value}")
            return

        # ── 阶段 1：RAG 前处理 ────────────────────────────────────────────────
        yield StreamEvent("thinking", "危机检测通过，正在改写检索查询…")

        state = await self._step_query_rewrite(state, mem)

        for _ in range(_MAX_RETRY + 1):
            state = await self._step_retrieve(state)
            if self._retrieval.is_quality_sufficient(state["retrieval_quality"]):
                break
            state["retry_count"] += 1
            yield StreamEvent("thinking", f"检索质量不足（{state['retrieval_quality']:.2f}），重试改写查询…")
            state = await self._step_query_rewrite(state, mem, is_retry=True)

        t_rag_done = time.perf_counter()
        rag_ms = (t_rag_done - t_start) * 1000
        state["thought"] += f"\nRAG 前处理耗时：{rag_ms:.0f}ms"
        yield StreamEvent("thinking", state["thought"].strip())

        # ── 阶段 2：流式 LLM 生成 ────────────────────────────────────────────
        context = self._retrieval.format_context(state["retrieved_chunks"])
        user_prompt = (
            f"参考以下知识库内容：\n{context}\n\n"
            f"请回复用户的问题：{message}"
        )
        messages = mem.get_messages() + [{"role": "user", "content": user_prompt}]

        full_reply = ""
        first_token = True
        ttft_ms = 0.0
        async for token in self._llm.stream(system=_SYSTEM_PROMPT, messages=messages):
            if first_token:
                ttft_ms = (time.perf_counter() - t_start) * 1000
                first_token = False
            full_reply += token
            yield StreamEvent("token", token)

        # ── 收尾：持久化 + done 事件 ──────────────────────────────────────────
        state["final_response"] = full_reply
        await self._persist_turn(mem, message, full_reply)

        import json
        yield StreamEvent(
            "done",
            json.dumps({
                "thought": state["thought"].strip(),
                "conversation_id": conversation_id,
                "ttft_ms": round(ttft_ms, 1),
                "rag_ms": round(rag_ms, 1),
                "retrieval_quality": round(state["retrieval_quality"], 3),
                "retry_count": state["retry_count"],
            }, ensure_ascii=False),
        )

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

    async def _step_query_rewrite(
        self, state: AgentState, mem: DBMemoryTool, is_retry: bool = False
    ) -> AgentState:
        """步骤 2：Query 改写，将口语化表达转为检索友好的关键词句。"""
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

    async def _step_generate(self, state: AgentState, mem: DBMemoryTool) -> AgentState:
        """步骤 4：基于检索上下文调用 LLM 生成最终回复。"""
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

    async def _persist_turn(
        self, mem: DBMemoryTool, user_msg: str, assistant_msg: str
    ) -> None:
        """持久化 user + assistant 两条记录到 DB。"""
        await mem.save_turn("user", user_msg)
        await mem.save_turn("assistant", assistant_msg)

    def _build_response(self, state: AgentState) -> AgentResponse:
        return AgentResponse(
            conversation_id=state["conversation_id"],
            thought=state["thought"].strip(),
            reply=state["final_response"],
        )
