"""
DBMemoryTool — 持久化对话记忆，基于 PostgreSQL chat_history 表。

替代原有 MemoryTool（内存内 deque），解决两个问题：
1. 原 MemoryTool 在 per-request PsychAgent 实例化模式下，每次请求都丢失历史（真实 Bug）
2. 多 Worker / 负载均衡场景下跨进程共享状态（分布式场景）

设计决策：
- 每次 run() 开始时，从 DB 拉取最近 N 条历史（轻量 SELECT）
- 每次 run() 结束时，写入 user + assistant 两条记录（异步写入）
- 不使用内存缓存——服务层无状态，DB 是唯一真相来源
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.config import AIEngineConfig


class DBMemoryTool:
    """基于 PostgreSQL 的持久化对话记忆工具。

    用法：
        mem = DBMemoryTool(db, conversation_id, config)
        await mem.load()                     # 拉取历史
        messages = mem.get_messages()        # 给 LLM 的消息列表
        await mem.save_turn("user", text)    # 写入一条记录
        await mem.save_turn("assistant", text)
    """

    def __init__(
        self,
        db: AsyncSession,
        conversation_id: str,
        config: AIEngineConfig,
    ) -> None:
        self._db = db
        self._conversation_id = conversation_id
        self._max_turns = config.max_history_turns
        self._history: list[dict] = []  # [{"role": ..., "content": ...}, ...]

    async def load(self) -> None:
        """从 DB 拉取最近 max_turns 轮历史（每轮含 user+assistant 两条）。"""
        limit = self._max_turns * 2  # user + assistant 各一条
        sql = text("""
            SELECT role, content
            FROM (
                SELECT role, content, created_at
                FROM chat_history
                WHERE conversation_id = :conv_id
                ORDER BY created_at DESC
                LIMIT :limit
            ) sub
            ORDER BY sub.created_at ASC
        """)
        result = await self._db.execute(
            sql, {"conv_id": self._conversation_id, "limit": limit}
        )
        self._history = [
            {"role": row.role, "content": row.content}
            for row in result.fetchall()
        ]

    def get_messages(self) -> list[dict]:
        """返回 OpenAI messages 格式，直接传入 LLMClient。"""
        return list(self._history)

    async def save_turn(self, role: str, content: str) -> None:
        """异步写入一条对话记录。"""
        sql = text("""
            INSERT INTO chat_history (conversation_id, role, content)
            VALUES (:conv_id, :role, :content)
        """)
        await self._db.execute(
            sql,
            {"conv_id": self._conversation_id, "role": role, "content": content},
        )
        await self._db.commit()
        # 同步更新本地缓存（同一请求内后续步骤可见）
        self._history.append({"role": role, "content": content})
