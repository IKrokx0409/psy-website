from __future__ import annotations

import numpy as np
from enum import Enum

from ai_engine.config import AIEngineConfig
from ai_engine.rag.embedder import Embedder


class CrisisLevel(Enum):
    NONE = "none"       # 无危机信号
    LOW = "low"         # 负面情绪，需要关注
    MEDIUM = "medium"   # 明显焦虑/压力，需要主动引导
    HIGH = "high"       # 自伤/自杀倾向，触发危机协议


# 预设危机响应，不经过 RAG，确保响应速度和内容安全
_CRISIS_RESPONSES: dict[CrisisLevel, str] = {
    CrisisLevel.HIGH: (
        "我注意到你现在非常痛苦，我很担心你的安全。"
        "请立刻拨打心理援助热线：**北京 010-82951332**，**全国 400-161-9995**。"
        "你不是一个人，我们在你身边。"
    ),
    CrisisLevel.MEDIUM: (
        "听起来你现在承受着很大的压力，这种感受是真实的，我理解你。"
        "如果你愿意，可以和我多说说发生了什么？学校心理中心也随时欢迎你预约。"
    ),
}

# 语义检测阈值（偏保守：假阴性代价远高于假阳性）
_THRESHOLD_HIGH = 0.82
_THRESHOLD_MEDIUM = 0.68


class CrisisTool:
    """危机检测工具，Agent 循环的第一道门控。

    两层检测策略：
    1. 关键词规则层（毫秒级）—— 命中即升级为 HIGH
    2. 语义相似度层（百毫秒级）—— 捕捉隐晦表达，如"我觉得很累，不想撑了"

    在心理健康场景中，假阴性（漏检）的代价远高于假阳性（误报），
    因此阈值设置偏保守。
    """

    def __init__(self, config: AIEngineConfig, embedder: Embedder) -> None:
        self._keywords = config.crisis_keywords
        self._embedder = embedder
        # 危机语义锚点，用于语义层检测
        self._crisis_anchors: list[str] = [
            "我想结束自己的生命",
            "活着没有意义",
            "我想消失",
            "不想活下去了",
            "我要自杀",
        ]
        self._anchor_embeddings: list[list[float]] | None = None

    async def _ensure_anchors(self) -> None:
        if self._anchor_embeddings is None:
            self._anchor_embeddings = await self._embedder.embed_batch(self._crisis_anchors)

    async def detect(self, message: str) -> CrisisLevel:
        """检测消息危机等级。关键词命中直接返回 HIGH，不进语义层。"""
        # 规则层
        for kw in self._keywords:
            if kw in message:
                return CrisisLevel.HIGH

        # 语义层
        await self._ensure_anchors()
        q = np.array(await self._embedder.embed(message))
        q_norm = np.linalg.norm(q)
        if q_norm < 1e-9:
            return CrisisLevel.NONE

        max_sim = 0.0
        for anchor_emb in self._anchor_embeddings:
            a = np.array(anchor_emb)
            sim = float(np.dot(q, a) / (q_norm * np.linalg.norm(a) + 1e-9))
            if sim > max_sim:
                max_sim = sim

        if max_sim >= _THRESHOLD_HIGH:
            return CrisisLevel.HIGH
        if max_sim >= _THRESHOLD_MEDIUM:
            return CrisisLevel.MEDIUM
        return CrisisLevel.NONE

    def get_protocol_response(self, level: CrisisLevel) -> str | None:
        """返回预设危机响应文本，NONE 级别返回 None（继续正常 Agent 流程）。"""
        return _CRISIS_RESPONSES.get(level)
