# ============================================================
# 【学习顺序 ⑥】tools/crisis.py — 危机检测工具
#
# 学习目标：
#   理解 Agent 中"工具（Tool）"的概念，以及"分层防御"策略。
#
# 核心概念：Tool（工具）
#   在 Agent 架构里，Tool 是 Agent 可以调用的"能力模块"。
#   Agent 根据用户输入决定"调用哪个工具"来处理当前步骤。
#   这个文件实现的危机检测工具是整个 Agent 流程的第一道关卡：
#   任何用户消息都要先过这里，再决定后续流程。
#
# 两层防御策略（体现工程设计思维）：
#   Layer 1 规则层（关键词匹配）：
#     - 速度：< 1 毫秒
#     - 覆盖：明确表达（"我想自杀"）
#     - 特点：100% 精确，不会漏掉这些词
#
#   Layer 2 语义层（向量相似度）：
#     - 速度：约 150 毫秒
#     - 覆盖：隐晦表达（"我感觉很累了，不想继续了"）
#     - 特点：能理解潜台词，捕捉关键词层覆盖不到的情况
#
# 【为什么阈值要设得保守（偏高）？】
# 在心理场景中，"假阴性"（该检测到但没检测到）比"假阳性"（误报）的代价高得多。
# 宁可多响应一次危机协议，也不能漏掉一个真正需要帮助的人。
# ============================================================

from __future__ import annotations

import numpy as np
from enum import Enum

from ai_engine.config import AIEngineConfig
from ai_engine.rag.embedder import Embedder


class CrisisLevel(Enum):
    """危机等级枚举。

    【为什么用 Enum 而不是字符串？】
    字符串 "high" 可能拼错（"hign"），而 CrisisLevel.HIGH 在 IDE 里有自动补全
    且拼错会直接报错，代码更健壮。
    """
    NONE = "none"       # 无危机信号，走正常 RAG 流程
    LOW = "low"         # 轻微负面情绪（目前未使用，预留扩展）
    MEDIUM = "medium"   # 明显焦虑/压力，返回关怀话术，建议预约咨询
    HIGH = "high"       # 自伤/自杀倾向，立即给出危机热线，跳过 RAG


# 预设危机响应文本（不经过 RAG，不经过 LLM 生成，确保内容安全可控）
# 【为什么预设而不让 LLM 生成？】
# 危机场景需要精确、权威、无歧义的响应，不能让 LLM 发挥创意
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

# 语义检测阈值（余弦相似度，0~1）
# HIGH：相似度 >= 0.82 判定为高危（宁可误报，不能漏报）
# MEDIUM：0.68 <= 相似度 < 0.82 判定为中危
_THRESHOLD_HIGH = 0.82
_THRESHOLD_MEDIUM = 0.68


class CrisisTool:
    """危机检测工具，Agent 循环的第一道门控。

    两层检测策略：
    1. 关键词规则层（毫秒级）—— 命中即升级为 HIGH
    2. 语义相似度层（百毫秒级）—— 捕捉隐晦表达
    """

    def __init__(self, config: AIEngineConfig, embedder: Embedder) -> None:
        self._keywords = config.crisis_keywords
        self._embedder = embedder
        # 语义锚点：精心挑选的"标准危机表达"，用于和用户消息做相似度比较
        # 用户说的话和这些句子越相似，危机概率越高
        self._crisis_anchors: list[str] = [
            "我想结束自己的生命",
            "活着没有意义",
            "我想消失",
            "不想活下去了",
            "我要自杀",
        ]
        self._anchor_embeddings: list[list[float]] | None = None  # 延迟计算

    async def _ensure_anchors(self) -> None:
        """把锚点句子向量化（只做一次，之后缓存在内存里）。

        锚点向量不会变，没必要每次请求都重新计算，
        所以用 None 做标记，第一次调用时计算并缓存。
        """
        if self._anchor_embeddings is None:
            self._anchor_embeddings = await self._embedder.embed_batch(self._crisis_anchors)

    async def detect(self, message: str) -> CrisisLevel:
        """检测消息危机等级。

        【流程】
        1. 遍历关键词列表，有一个命中就直接返回 HIGH（最快路径）
        2. 如果关键词未命中，计算消息和所有锚点的余弦相似度
        3. 取最高相似度，与阈值比较得出结论

        【余弦相似度计算】
        cos(A, B) = (A·B) / (|A| × |B|)
        结果范围 [-1, 1]，1 表示完全相同，0 表示无关，-1 表示相反
        用 numpy 向量运算实现，比 Python 循环快很多
        """
        # 第一层：关键词规则（O(n) 字符串查找，极快）
        for kw in self._keywords:
            if kw in message:
                return CrisisLevel.HIGH  # 命中关键词，立即返回，不进入语义层

        # 第二层：语义相似度（需要向量计算，慢一些但能捕捉隐晦表达）
        await self._ensure_anchors()
        q = np.array(await self._embedder.embed(message))
        q_norm = np.linalg.norm(q)  # 向量的模（长度）
        if q_norm < 1e-9:           # 防止除以零（全零向量的边界情况）
            return CrisisLevel.NONE

        # 遍历所有锚点，找最高相似度
        max_sim = 0.0
        for anchor_emb in self._anchor_embeddings:
            a = np.array(anchor_emb)
            # 余弦相似度公式：点积 / (模A × 模B)
            # 加 1e-9 防止 anchor 向量模为零时除以零
            sim = float(np.dot(q, a) / (q_norm * np.linalg.norm(a) + 1e-9))
            if sim > max_sim:
                max_sim = sim

        # 与阈值比较，得出最终等级
        if max_sim >= _THRESHOLD_HIGH:
            return CrisisLevel.HIGH
        if max_sim >= _THRESHOLD_MEDIUM:
            return CrisisLevel.MEDIUM
        return CrisisLevel.NONE

    def get_protocol_response(self, level: CrisisLevel) -> str | None:
        """返回预设危机响应文本。

        NONE 级别返回 None，表示"没有危机，继续正常流程"。
        调用方通过判断返回值是否为 None 决定是否跳过 RAG。
        """
        return _CRISIS_RESPONSES.get(level)
