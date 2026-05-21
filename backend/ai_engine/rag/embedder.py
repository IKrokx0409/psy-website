from __future__ import annotations

import asyncio
from ai_engine.config import AIEngineConfig


class Embedder:
    """本地 sentence-transformers 模型封装。

    使用 BAAI/bge-base-zh-v1.5（768 维），在 CPU 上推理速度可接受，
    无需外部 Embedding API，消除网络依赖，提升鲁棒性。
    """

    def __init__(self, config: AIEngineConfig) -> None:
        self._model_name = config.embedding_model
        self._dim = config.embedding_dim
        self._model = None  # 延迟加载，首次调用时初始化

    def _ensure_loaded(self) -> None:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)

    async def embed(self, text: str) -> list[float]:
        self._ensure_loaded()
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, self._model.encode, text)
        return embedding.tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self._ensure_loaded()
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self._model.encode, texts)
        return [e.tolist() for e in embeddings]
