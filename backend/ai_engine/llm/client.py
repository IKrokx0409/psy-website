# ============================================================
# 【学习顺序 ②】llm/client.py — LLM 调用封装
#
# 学习目标：
#   理解怎么用代码调用大语言模型，以及"流式输出"是怎么实现的。
#
# 核心概念：
#   complete()  = 等 LLM 生成完整回复再返回（像发邮件，等回信）
#   stream()    = LLM 生成一个字就立刻推送一个字（像打电话，实时听）
#
# 关键设计：
#   "供应商无关" —— 只要支持 OpenAI 协议（DeepSeek/通义/GPT 都支持），
#   改一行 base_url 就能切换，代码其他地方完全不用改。
# ============================================================

from __future__ import annotations

from typing import AsyncIterator
import httpx
from openai import AsyncOpenAI  # 使用 OpenAI 官方 SDK，但可对接任何兼容服务

from ai_engine.config import AIEngineConfig


class LLMClient:
    """供应商无关的 LLM 调用封装。

    【为什么要封装一层而不直接用 AsyncOpenAI？】
    1. 统一入口：整个项目所有 LLM 调用都走这里，以后要加日志/重试/
       限流，只改这一个文件
    2. 解耦：agent.py 不需要知道用的是 DeepSeek 还是 GPT，只管调用
       complete() / stream()
    3. 测试方便：写单元测试时可以用 mock 替换这个类
    """

    def __init__(self, config: AIEngineConfig) -> None:
        # 【重要 Bug 修复】proxy=None 显式禁用代理
        #
        # 问题背景：WSL2 环境下系统设置了 SOCKS 代理，
        # httpx（网络请求库）会自动读取系统代理环境变量，
        # 导致发往 DeepSeek 的请求被转发到代理，而代理不支持该域名，
        # 请求就会永远卡住（没有超时报错，就是不返回）。
        #
        # 修复方式：给 httpx 客户端传入 proxy=None，
        # 明确告诉它"不走任何代理，直连目标服务器"。
        self._client = AsyncOpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,      # 改这里就能换供应商
            http_client=httpx.AsyncClient(proxy=None),  # 绕过系统代理
        )
        self._model = config.llm_model

    async def complete(self, system: str, messages: list[dict]) -> str:
        """非流式调用：等待 LLM 生成完整回复后一次性返回。

        【参数说明】
        system   : 系统提示词，定义 AI 的"角色"和"行为准则"
                   例如："你是一位专业的心理咨询师，不提供诊断结论..."
        messages : 对话历史列表，格式固定为 OpenAI 的 messages 格式：
                   [{"role": "user", "content": "我最近很焦虑"},
                    {"role": "assistant", "content": "我理解你的感受..."},
                    {"role": "user", "content": "怎么缓解？"}]
                   LLM 看到完整历史才能理解上下文

        【什么时候用 complete？】
        Query 改写（Step2）：需要等改写结果出来才能去检索
        回复生成（非流式模式）：一次性返回完整答案
        """
        response = await self._client.chat.completions.create(
            model=self._model,
            # system 作为第一条 message 插入，OpenAI 协议要求这种格式
            messages=[{"role": "system", "content": system}, *messages],
            temperature=0.7,
            # temperature 控制"随机性"：
            #   0.0 = 每次输出完全一样（适合需要精确结果的任务）
            #   1.0 = 输出很有创意但也可能乱说（适合写作）
            #   0.7 = 平衡，稍有变化但不会乱
        )
        return response.choices[0].message.content or ""

    async def stream(self, system: str, messages: list[dict]) -> AsyncIterator[str]:
        """流式调用：LLM 生成一个 token 就立刻 yield 出来。

        【什么是 token？】
        LLM 不是按字生成的，而是按 token（词片段）。
        中文大概每 1~2 个字是一个 token，英文每 3~4 个字母是一个 token。
        这里为了前端体验，直接把 token 当"字"推送。

        【async generator 是什么？】
        普通函数 return 一个值就结束了。
        async generator 函数可以 yield 很多次，每次 yield 一个值，
        调用方用 `async for token in stream(...)` 逐个接收。
        这样 LLM 生成一个字，前端就能立刻显示一个字，
        而不是等全部生成完才显示。

        【什么时候用 stream？】
        最终回复生成（Step4 流式模式）：让用户看到"打字机效果"
        """
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, *messages],
            stream=True,    # ← 关键参数：告诉服务器"用流式模式返回"
            temperature=0.7,
        )
        # 逐个 chunk（数据块）处理
        # 每个 chunk 对应 LLM 生成的一小段文字
        async for chunk in resp:
            delta = chunk.choices[0].delta.content
            if delta:   # delta 可能为 None（比如最后一个结束信号的 chunk）
                yield delta  # 立刻把这一小段文字发出去
