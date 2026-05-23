# ============================================================
# 【学习顺序 ③】rag/embedder.py — 文本向量化
#
# 学习目标：
#   理解"向量/Embedding"是什么，以及为什么它能实现语义搜索。
#
# 核心概念：Embedding（词嵌入/向量化）
#   把一段文字压缩成一串数字（向量），意思相近的文字向量也相近。
#
#   例如：
#     "我心情很差"  → [0.12, -0.34, 0.87, ...]  (768个数字)
#     "最近情绪低落" → [0.13, -0.31, 0.85, ...]  (768个数字，很接近！)
#     "今天天气不错" → [-0.45, 0.67, -0.23, ...]  (完全不同)
#
#   两个向量的"余弦相似度"越高，说明语义越相近。
#   这就是"语义搜索"的本质：不是找关键词，而是找意思相近的内容。
#
# 为什么要本地模型而不是 API？
#   1. 入库时需要对几百条知识做向量化，频繁调用 API 成本高
#   2. 检索时每次请求都要向量化用户问题，网络延迟不稳定
#   3. 这个模型（bge-base-zh-v1.5）专为中文优化，效果比通用模型好
# ============================================================

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
        self._model = None  # 【延迟加载】模型文件约 200MB，只在第一次使用时才加载

    def _ensure_loaded(self) -> None:
        """确保模型已加载到内存（懒加载模式）。

        【为什么用懒加载而不是在 __init__ 里直接加载？】
        1. 启动速度：服务启动时不用等模型加载，响应更快
        2. 按需加载：如果某个请求不需要检索，就不用加载模型
        3. 实际上 main_ai.py 在 lifespan 里会主动触发这个方法预热，
           所以第一个真实请求时模型已经在内存里了

        【Bug 修复：local_files_only】
        新版 sentence-transformers 在加载模型时会尝试访问 HuggingFace
        官网检查是否有更新版本。WSL2 下因为代理问题这个网络请求会失败，
        导致整个模型加载崩溃。
        local_files_only=True 告诉它"直接用本地缓存，不要联网检查"。
        """
        if self._model is None:
            import os
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self._model_name,
                local_files_only=os.getenv("HF_HUB_OFFLINE", "0") == "1",
            )

    async def embed(self, text: str) -> list[float]:
        """把一段文字转换成向量（768个浮点数的列表）。

        【为什么用 run_in_executor？】
        模型推理（CPU 计算）是同步阻塞操作，如果直接在 async 函数里调用，
        会"堵住"整个事件循环，其他请求都得等它算完。
        run_in_executor 把这个计算丢到线程池里执行，
        事件循环可以继续处理其他请求，计算完了再回来取结果。
        这是 Python 异步编程中处理 CPU 密集型任务的标准做法。
        """
        self._ensure_loaded()
        loop = asyncio.get_event_loop()
        # run_in_executor(None, ...) 中 None 表示用默认线程池
        embedding = await loop.run_in_executor(None, self._model.encode, text)
        return embedding.tolist()  # numpy array → Python list（JSON 可序列化）

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量向量化：一次处理多段文字，比逐条调用 embed() 快很多。

        【为什么批量比逐条快？】
        模型推理有"启动开销"（加载权重、初始化计算图等），
        批量处理时这个开销只付一次，然后并行处理所有文本。
        入库 518 条知识时用批量可以节省数十倍时间。
        """
        self._ensure_loaded()
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self._model.encode, texts)
        return [e.tolist() for e in embeddings]
