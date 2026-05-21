from __future__ import annotations

from typing import AsyncIterator
import httpx
from openai import AsyncOpenAI

from ai_engine.config import AIEngineConfig


class LLMClient:
    """供应商无关的 LLM 调用封装。

    通过 AIEngineConfig 切换 DeepSeek / OpenAI / 其他兼容 OpenAI 协议的服务，
    面试时可现场演示切换，体现系统解耦设计。
    """

    def __init__(self, config: AIEngineConfig) -> None:
        # 显式传入不走系统代理的 httpx 客户端，避免 SOCKS 代理导致请求卡死
        self._client = AsyncOpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            http_client=httpx.AsyncClient(proxy=None),
        )
        self._model = config.llm_model

    async def complete(self, system: str, messages: list[dict]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, *messages],
            temperature=0.7,
        )
        return response.choices[0].message.content or ""

    async def stream(self, system: str, messages: list[dict]) -> AsyncIterator[str]:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, *messages],
            stream=True,
            temperature=0.7,
        )
        async for chunk in resp:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
