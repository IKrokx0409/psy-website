from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from ai_engine.config import AIEngineConfig


@dataclass
class Turn:
    role: str    # "user" | "assistant"
    content: str


class MemoryTool:
    """对话记忆管理，使用滑动窗口控制上下文长度。

    设计取舍：
    - 固定窗口（保留最近 N 轮）实现简单，足以覆盖大多数对话场景
    - 更复杂的方案（摘要压缩、重要性加权）留作后续迭代
    - 跨会话持久化依赖前端 localStorage（与现有 Chat.vue 行为一致）
    """

    def __init__(self, config: AIEngineConfig) -> None:
        self._max_turns = config.max_history_turns
        self._history: deque[Turn] = deque(maxlen=self._max_turns * 2)  # user+assistant各一条

    def add_turn(self, role: str, content: str) -> None:
        """追加一轮对话，超出窗口时自动丢弃最旧的。"""
        self._history.append(Turn(role=role, content=content))

    def get_messages(self) -> list[dict]:
        """返回 OpenAI 格式的消息列表，直接传入 LLMClient。"""
        return [{"role": t.role, "content": t.content} for t in self._history]

    def get_context_str(self) -> str:
        """返回纯文本格式的历史，用于 prompt 拼接。"""
        lines = [f"{t.role}: {t.content}" for t in self._history]
        return "\n".join(lines)

    def clear(self) -> None:
        self._history.clear()
