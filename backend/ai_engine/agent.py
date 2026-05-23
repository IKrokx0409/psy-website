# ============================================================
# 【学习顺序 ⑨】agent.py — PsychAgent 主循环 ★ 最终目标
#
# 学习目标：
#   理解 Agent 架构的核心：状态机 + 工具调用 + 决策循环。
#   读完前面 ①~⑧ 的代码后，这里你会看到它们是怎么被"组装"在一起的。
#
# ============================================================
# 什么是 Agent？
#
#   普通 LLM 调用（非 Agent）：
#     用户输入 → LLM → 输出
#     只有一步，LLM 直接回答，没有中间过程
#
#   Agent：
#     用户输入 → 【思考→选择工具→执行→观察结果→再思考→...】→ 输出
#     有一个"循环"，Agent 可以根据中间结果调整策略
#
# 这个项目的 Agent 是"硬编码流程"的 Agentic RAG：
#   不是 LLM 自主决定调哪个工具，而是按照固定的 5 个步骤执行，
#   但在步骤 3（检索）中有"质量不够就重试"的自适应循环，
#   体现了 Agent 的"根据观察结果调整行为"的特征。
#
# ============================================================
# 状态机（State Machine）是什么？
#
#   把一次处理流程的所有中间数据集中在一个 dict 里（AgentState），
#   每个步骤读取状态、修改状态、返回新状态，像接力棒一样传递。
#
#   好处：
#   1. 每个步骤是纯函数（输入 state → 输出 state），容易测试
#   2. 任意步骤都可以读取之前步骤留下的结果
#   3. 调试时直接 print(state) 就能看到当前处理到哪步
#
# ============================================================
# 两种输出模式：
#
#   run()    → 阻塞，等全部完成后一次性返回（向后兼容旧接口）
#   stream() → 两阶段 SSE 流式输出，用户体验更好：
#               阶段1：RAG 前处理（危机检测+改写+检索）→ 发 thinking 事件
#               阶段2：LLM 逐 token 生成 → 每个字发一个 token 事件
#               结束：发 done 事件（带 TTFT 等性能数据）
# ============================================================

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import AsyncIterator, TypedDict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.config import AIEngineConfig
from ai_engine.llm.client import LLMClient
from ai_engine.rag.embedder import Embedder
from ai_engine.rag.pg_retriever import PGRetriever, RetrievedChunk
from ai_engine.rag.reranker import Reranker
from ai_engine.tools.crisis import CrisisTool, CrisisLevel
from ai_engine.tools.db_memory import DBMemoryTool
from ai_engine.tools.retrieval import RetrievalTool


# ── 状态机数据结构 ────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Agent 处理一次请求的完整状态。

    【TypedDict 是什么？】
    Python 的普通 dict 没有类型提示，IDE 不知道里面有哪些 key。
    TypedDict 让 dict 有了"固定字段"的类型声明，IDE 可以自动补全。

    【每个字段在哪个步骤被赋值？】
    message          → 初始化时设置（用户原始输入）
    conversation_id  → 初始化时设置（前端传来的会话 ID）
    crisis_level     → Step1 危机检测后设置
    rewritten_query  → Step2 Query 改写后设置（初始值 = message）
    retrieved_chunks → Step3 检索后设置
    retrieval_quality→ Step3 检索后设置
    retry_count      → Step3 不达标时递增
    thought          → 各步骤追加，最终展示给用户看
    final_response   → Step4 生成后设置（最终 AI 回复）
    """
    message: str
    conversation_id: str
    crisis_level: CrisisLevel
    rewritten_query: str           # Query 改写后的版本，用于检索
    retrieved_chunks: list[RetrievedChunk]
    retrieval_quality: float       # [0, 1]，低于阈值触发重试
    retry_count: int               # 防止无限重试
    thought: str                   # Agent 推理过程（每步追加，最终传给前端）
    final_response: str


@dataclass
class AgentResponse:
    """非流式接口（run()）的返回值。"""
    conversation_id: str
    thought: str    # 完整的推理过程日志
    reply: str      # 最终 AI 回复


@dataclass
class StreamEvent:
    """SSE 流式传输的单个事件。

    【SSE（Server-Sent Events）是什么？】
    服务器主动向浏览器推送数据的协议，比 WebSocket 更轻量。
    每个事件的文本格式固定为：
        event: thinking\ndata: 正在搜索知识库...\n\n
        event: token\ndata: 你\n\n
        event: token\ndata: 好\n\n
        event: done\ndata: {"ttft_ms": 2408.6, ...}\n\n

    event 类型：
      thinking  — RAG 前处理进度（前端显示"思考中"动画）
      token     — LLM 生成的逐字 token（前端逐字追加显示）
      done      — 流结束，携带 thought/conversation_id/ttft_ms 等元数据
    """
    event: str   # thinking | token | done | error
    data: str


# ── 系统 Prompt ───────────────────────────────────────────────────────────────

# System Prompt 是给 LLM 的"角色说明书"，定义它应该是谁、怎么说话。
# 放在这里（模块级常量）而不是写在函数里，是因为：
# 1. 每次请求都用同一份，不需要每次重新创建字符串
# 2. 方便统一修改，所有调用都共享这份 prompt
_SYSTEM_PROMPT = """你是一位专业的高校心理健康助手，具备心理咨询知识，能够提供情感支持和心理健康指导。

回复原则：
1. 以检索到的知识库内容为依据，不编造信息
2. 语气温和、不评判、以倾听和支持为主
3. 遇到超出知识库范围的问题，诚实说明并建议寻求专业帮助
4. 绝对不提供诊断结论，引导用户咨询专业心理咨询师
"""

_MAX_RETRY = 2  # Query 改写最大重试次数（防止无限循环）


# ── Agent 主体 ────────────────────────────────────────────────────────────────

class PsychAgent:
    """心理健康 Agentic RAG 主循环（无状态版本）。

    【"无状态"是什么意思？】
    每次请求 new 一个新实例，处理完就丢弃。
    不在实例变量里保存用户数据（对话历史存在 DB 里，不在 self._xxx 里）。
    这样多个 Worker 进程都能处理同一个用户的请求，可以水平扩展。

    【依赖注入（Embedder / Reranker）】
    Embedder 和 Reranker 加载模型文件各需要 1-2 秒。
    如果每次请求都新建，每次都要加载模型，23 秒才能响应。
    解决：main_ai.py 在服务启动时创建好单例，通过构造函数传进来。
    这种"从外部传入依赖，而不是内部创建"的模式叫"依赖注入"。
    """

    def __init__(
        self,
        config: AIEngineConfig,
        db: AsyncSession,
        embedder: Embedder | None = None,    # 外部注入（已预热的单例）
        reranker: Reranker | None = None,    # 外部注入（已预热的单例）
    ) -> None:
        # 优先使用注入的单例，没有则新建（供测试脚本单独使用）
        _embedder = embedder or Embedder(config)
        _reranker = reranker or Reranker(config)

        # 把底层组件组装成高层工具
        retriever = PGRetriever(db, _embedder, config)

        self._llm = LLMClient(config)                          # LLM 调用
        self._crisis = CrisisTool(config, _embedder)           # 危机检测工具
        self._retrieval = RetrievalTool(retriever, _reranker, config)  # 检索工具
        self._config = config
        self._db = db
        self._embedder = _embedder                             # 供 DBMemoryTool 向量检索使用

    # ── 非流式主入口 ───────────────────────────────────────────────────────────

    async def run(self, message: str, conversation_id: str) -> AgentResponse:
        """Agent 主入口（非流式），等待所有步骤完成后一次性返回。

        【5 步流程】
        Step1 危机检测 → 命中则直接返回协议响应（跳过 2-4）
        Step2 Query 改写 → 把用户的口语化问题转为检索友好的查询
        Step3 混合检索 → 从知识库取出相关内容，不达标则循环改写重试
        Step4 LLM 生成 → 基于检索结果生成最终回复
        Step5 持久化 → 写 chat_history + request_traces

        各步骤均有计时，最终写入 request_traces 表供分析。
        """
        t0 = time.perf_counter()
        timings: dict[str, float] = {}

        # 初始化双轨记忆工具（传入 embedder/llm 启用向量检索 + 画像提取）
        mem = DBMemoryTool(
            self._db, conversation_id, self._config,
            embedder=self._embedder, llm=self._llm,
        )
        await mem.load(message=message)  # 加载画像 + 近期历史 + 语义相关历史

        # 初始化状态机（所有字段设为默认值）
        state: AgentState = {
            "message": message,
            "conversation_id": conversation_id,
            "crisis_level": CrisisLevel.NONE,
            "rewritten_query": message,      # 初始值 = 原始消息
            "retrieved_chunks": [],
            "retrieval_quality": 0.0,
            "retry_count": 0,
            "thought": "",
            "final_response": "",
        }

        # ── Step 1：危机检测 ──────────────────────────────────────────────────
        t1 = time.perf_counter()
        state = await self._step_crisis_detection(state)
        timings["crisis_ms"] = round((time.perf_counter() - t1) * 1000, 1)

        if state["crisis_level"] in (CrisisLevel.HIGH, CrisisLevel.MEDIUM):
            # 检测到危机：跳过所有 RAG 步骤，直接返回预设协议响应
            await self._persist_turn(mem, message, state["final_response"])
            total_ms = round((time.perf_counter() - t0) * 1000, 1)
            await self._write_trace(state, timings, total_ms)
            return self._build_response(state)

        # ── Step 2：Query 改写 ────────────────────────────────────────────────
        # 用户消息通常是口语化的，改写成"心理健康领域的检索关键词"效果更好
        # 例："我最近老睡不好" → "失眠 睡眠质量差 改善方法"
        t2 = time.perf_counter()
        state = await self._step_query_rewrite(state, mem)
        timings["rewrite_ms"] = round((time.perf_counter() - t2) * 1000, 1)

        # ── Step 3：检索（含自适应重试循环）────────────────────────────────────
        # 这是 Agentic RAG 的"自适应"部分：
        # 检索质量不达标时，会重新改写查询再试一次（最多 _MAX_RETRY 次）
        for _ in range(_MAX_RETRY + 1):
            t3 = time.perf_counter()
            state = await self._step_retrieve(state)
            timings["retrieve_ms"] = round((time.perf_counter() - t3) * 1000, 1)

            if self._retrieval.is_quality_sufficient(state["retrieval_quality"]):
                break  # 质量达标，退出循环

            # 质量不达标：改写查询，准备重试
            state["retry_count"] += 1
            t4 = time.perf_counter()
            state = await self._step_query_rewrite(state, mem, is_retry=True)
            timings[f"rewrite_retry{state['retry_count']}_ms"] = round((time.perf_counter() - t4) * 1000, 1)

        # ── Step 4：LLM 生成回复 ──────────────────────────────────────────────
        t5 = time.perf_counter()
        state = await self._step_generate(state, mem)
        timings["generate_ms"] = round((time.perf_counter() - t5) * 1000, 1)

        # ── Step 5：持久化 ────────────────────────────────────────────────────
        await self._persist_turn(mem, message, state["final_response"])
        total_ms = round((time.perf_counter() - t0) * 1000, 1)
        await self._write_trace(state, timings, total_ms)

        return self._build_response(state)

    # ── 流式主入口 ─────────────────────────────────────────────────────────────

    async def stream(
        self, message: str, conversation_id: str
    ) -> AsyncIterator[StreamEvent]:
        """Agent 流式入口 — 两阶段 SSE。

        【为什么需要流式输出？】
        非流式模式下，用户需要等 LLM 生成完整回复（可能 10 秒以上）才看到内容。
        心理咨询场景下这种等待体验很差，用户容易以为系统卡死了。
        流式模式把处理过程分两个阶段推送，让用户"看到进度"：

        阶段 1（阻塞，约 1-2 秒）：
          危机检测 → Query 改写 → 混合检索 → 重排序
          → 发送一个 thinking 事件（"正在查询知识库..."）
          前端收到 thinking 事件时显示思考动画

        阶段 2（流式，持续数秒）：
          LLM 逐 token 生成 → 每个 token 发一个 token 事件
          前端收到 token 事件时逐字追加显示（打字机效果）

        【TTFT（Time To First Token）】
        从用户发送消息到前端显示第一个字的时间。
        = 危机检测时间 + Query改写时间 + 检索时间 + LLM首token时间
        实测约 2.4 秒（热启动，DeepSeek API 响应正常时）。
        """
        t_start = time.perf_counter()

        mem = DBMemoryTool(
            self._db, conversation_id, self._config,
            embedder=self._embedder, llm=self._llm,
        )
        await mem.load(message=message)

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

        # 把用户画像注入 system prompt（画像为空时行为与原来完全相同）
        profile_ctx = mem.get_profile_context()
        system = _SYSTEM_PROMPT + (f"\n\n{profile_ctx}" if profile_ctx else "")

        full_reply = ""
        first_token = True
        ttft_ms = 0.0
        async for token in self._llm.stream(system=system, messages=messages):
            if first_token:
                # 记录第一个 token 到来的时刻（TTFT 结束点）
                ttft_ms = (time.perf_counter() - t_start) * 1000
                first_token = False
            full_reply += token
            yield StreamEvent("token", token)  # 每个 token 立即推送给前端

        # ── 收尾：持久化 + done 事件 ──────────────────────────────────────────
        state["final_response"] = full_reply
        await self._persist_turn(mem, message, full_reply)

        total_ms = round((time.perf_counter() - t_start) * 1000, 1)
        stream_timings = {
            "rag_ms": round(rag_ms, 1),
            "ttft_ms": round(ttft_ms, 1),
            "total_ms": total_ms,
        }
        await self._write_trace(state, stream_timings, total_ms)

        # done 事件携带性能数据，前端用来显示 TTFT 徽章
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

    # ── 各步骤实现 ────────────────────────────────────────────────────────────
    # 每个 _step_xxx 方法都是"纯函数式"：
    # 接收 state → 修改其中部分字段 → 返回修改后的 state
    # 这样 run() 和 stream() 可以复用相同的步骤逻辑

    async def _step_crisis_detection(self, state: AgentState) -> AgentState:
        """步骤 1：危机检测（详见 tools/crisis.py）。

        命中危机时：设置 crisis_level + final_response，主循环检查后直接返回。
        未命中时：crisis_level = NONE，继续后续步骤。
        """
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
        """步骤 2：Query 改写。

        【为什么要改写？】
        用户："我最近老是睡不着，脑子停不下来"
        直接检索这句话，BM25 找"睡不着"，向量找"脑子停不下来"
        改写后："失眠 思维反刍 睡眠障碍 改善方法"
        检索精准度大幅提升。

        【重试时的改写】
        第一次检索质量不达标时，换一个角度改写：
        告诉 LLM"上次分数是多少，请换个角度提取关键词"
        给 LLM 上下文，让它产出不同的改写结果。
        """
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
            # 带上对话历史，让改写时有上下文感知
            messages=mem.get_messages() + [{"role": "user", "content": prompt}],
        )
        state["rewritten_query"] = rewritten.strip()
        state["thought"] += f"\n查询改写{'（重试）' if is_retry else ''}：{state['rewritten_query']}"
        return state

    async def _step_retrieve(self, state: AgentState) -> AgentState:
        """步骤 3：混合检索 + 重排序（详见 tools/retrieval.py）。

        使用 rewritten_query（改写后的查询），而不是原始 message。
        检索结果和质量分数写入 state，供主循环的质量门控使用。
        """
        chunks, quality = await self._retrieval.run(state["rewritten_query"])
        state["retrieved_chunks"] = chunks
        state["retrieval_quality"] = quality
        state["thought"] += f"\n检索质量分数：{quality:.2f}（阈值 {self._config.retrieval_score_threshold}）"
        return state

    async def _step_generate(self, state: AgentState, mem: DBMemoryTool) -> AgentState:
        """步骤 4：基于检索结果调用 LLM 生成最终回复（非流式版本）。

        【Prompt 构造】
        system = 角色说明 + 用户画像（来自 Track 1）
        messages = 历史对话（来自 Track 2，近期+语义相关）+ 当前带 context 的问题

        用户画像注入 system prompt 末尾，让 LLM 在整个回复过程中都能感知用户信息。
        例如用户之前说"我叫小明"，system prompt 里就有"称呼：小明"，
        LLM 回复时会自然地使用这个称呼。
        """
        context = self._retrieval.format_context(state["retrieved_chunks"])
        user_prompt = (
            f"参考以下知识库内容：\n{context}\n\n"
            f"请回复用户的问题：{state['message']}"
        )
        messages = mem.get_messages() + [{"role": "user", "content": user_prompt}]

        # 把用户画像追加到 system prompt（画像为空时不影响原有行为）
        profile_ctx = mem.get_profile_context()
        system = _SYSTEM_PROMPT + (f"\n\n{profile_ctx}" if profile_ctx else "")

        response = await self._llm.complete(system=system, messages=messages)
        state["final_response"] = response
        state["thought"] += f"\n已生成回复（基于 {len(state['retrieved_chunks'])} 个检索片段）"
        return state

    # ── 辅助方法 ──────────────────────────────────────────────────────────────

    async def _persist_turn(
        self, mem: DBMemoryTool, user_msg: str, assistant_msg: str
    ) -> None:
        """把用户消息和 AI 回复都存入数据库（详见 tools/db_memory.py）。

        每次对话结束时调用，确保下一轮请求能读到这轮历史。
        """
        await mem.save_turn("user", user_msg)
        await mem.save_turn("assistant", assistant_msg)

    def _build_response(self, state: AgentState) -> AgentResponse:
        """从 state 构造 API 响应对象（run() 的返回值）。"""
        return AgentResponse(
            conversation_id=state["conversation_id"],
            thought=state["thought"].strip(),
            reply=state["final_response"],
        )

    async def _write_trace(
        self,
        state: AgentState,
        step_timings: dict,
        total_ms: float,
    ) -> None:
        """把这次请求的完整决策链路写入 request_traces 表。

        【为什么要链路追踪？】
        Agentic RAG 有 5 个步骤，当出现"AI 回答乱了"的问题时，
        不知道是改写写错了？还是检索没找到？还是 LLM 生成跑偏了？
        有了 request_traces，可以通过 conversation_id 回溯：
          SELECT * FROM request_traces WHERE conversation_id = '...'
        看到每步的耗时、改写结果、检索分数，精确定位问题在哪一步。

        【try/except 静默失败】
        Trace 写入失败（比如数据库临时抖动）不能影响用户收到回复。
        业务永远比观测重要，所以用 try/except pass 兜底。
        """
        try:
            sql = text("""
                INSERT INTO request_traces
                    (request_id, conversation_id, crisis_level,
                     query_original, query_rewritten, retrieval_quality,
                     retry_count, step_timings, thought, total_ms)
                VALUES
                    (CAST(:req_id AS uuid), :conv_id, :crisis,
                     :q_orig, :q_rw, :quality,
                     :retry, CAST(:timings AS jsonb), :thought, :total)
            """)
            await self._db.execute(sql, {
                "req_id":  str(uuid.uuid4()),
                "conv_id": state["conversation_id"],
                "crisis":  state["crisis_level"].value,
                "q_orig":  state["message"],
                "q_rw":    state["rewritten_query"],
                "quality": state["retrieval_quality"],
                "retry":   state["retry_count"],
                "timings": json.dumps(step_timings, ensure_ascii=False),
                "thought": state["thought"].strip(),
                "total":   total_ms,
            })
            await self._db.commit()
        except Exception:
            pass  # Trace 写入失败不影响主流程
