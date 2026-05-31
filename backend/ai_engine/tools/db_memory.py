# ============================================================
# 【学习顺序 ⑦】tools/db_memory.py — 双轨记忆架构
#
# ┌─────────────────────────────────────────────────────────┐
# │               双轨记忆架构示意图                          │
# │                                                         │
# │  Track 1：用户画像（user_profiles 表，JSONB）           │
# │  ┌──────────────────────────────────────────────┐       │
# │  │ {                                            │       │
# │  │   "nickname": "小明",                        │       │
# │  │   "main_issues": ["失眠", "考试焦虑"],        │       │
# │  │   "tried_methods": ["冥想"],                 │       │
# │  │   "key_events": ["期末周压力大"],             │       │
# │  │   "preferences": ["不喜欢说教"],              │       │
# │  │   "emotional_state": "焦虑中等"              │       │
# │  │ }                                            │       │
# │  └──────────────────────────────────────────────┘       │
# │         ↑ LLM 每轮提取，增量合并                        │
# │                                                         │
# │  Track 2：向量化历史（chat_history + embedding 列）      │
# │  ┌────────────────────────────────────────────────┐     │
# │  │ 近期 3 轮（固定窗口）                           │     │
# │  │ + 语义相关历史（向量搜索，不受时间限制）         │     │
# │  └────────────────────────────────────────────────┘     │
# │         ↑ 当前问题的向量检索早期重要对话                 │
# └─────────────────────────────────────────────────────────┘
#
# 解决的问题：
#   原方案：滑动窗口，第1轮说的"我叫小明/我最近失眠"，
#           第11轮之后就被截断，AI 彻底遗忘。
#   新方案：
#     - 画像提取：重要事实存进 JSONB，不依赖原始对话存活
#     - 向量检索：早期相关对话即使超出窗口也能被"想起来"
# ============================================================

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.config import AIEngineConfig

# 避免循环导入：仅用于类型提示，运行时不实际导入
if TYPE_CHECKING:
    from ai_engine.rag.embedder import Embedder
    from ai_engine.llm.client import LLMClient


# ── 画像提取 Prompt ────────────────────────────────────────────────────────────
# 给 LLM 的指令：从一轮对话里提取/更新用户信息，只输出 JSON，不解释。
# 注意：只提取对话里明确提到的信息，不推断、不脑补。
_PROFILE_EXTRACTION_PROMPT = """\
你是一个信息提取助手。请从下面这轮对话中提取或更新用户的心理健康相关信息。

【当前已有画像】
{current_profile}

【本轮新对话】
用户：{user_msg}
助手：{assistant_msg}

请输出更新后的完整画像 JSON，只包含有实际内容的字段，格式如下：
{{
  "nickname": "用户希望被叫的称呼（若未提及则省略此字段）",
  "main_issues": ["主要困扰列表，如失眠/焦虑/人际关系等"],
  "tried_methods": ["用户提到已经尝试过的方法"],
  "key_events": ["重要的生活事件，如考试、失恋、家庭变故等"],
  "preferences": ["偏好或禁忌，如不喜欢说教、希望直接给建议等"],
  "emotional_state": "当前对话中体现的情绪状态（一句话描述）"
}}

规则：
1. 只提取对话里明确出现的信息，不推测
2. 数组字段是累积的（合并旧有内容，去重）
3. 没有新信息可提取时，直接返回已有画像原文
4. 只输出 JSON，不要任何解释文字
"""


class DBMemoryTool:
    """双轨记忆工具。

    【用法（在 agent.py 中）】
        mem = DBMemoryTool(db, conversation_id, config, embedder=emb, llm=llm)
        await mem.load(message=user_message)   # 请求开始：加载画像 + 检索历史
        context = mem.get_profile_context()    # 获取格式化画像（拼入 system prompt）
        messages = mem.get_messages()          # 获取历史消息列表（传给 LLM）
        await mem.save_turn("user", text)      # 保存用户消息（含向量化）
        await mem.save_turn("assistant", text) # 保存 AI 回复（触发画像更新）
    """

    def __init__(
        self,
        db: AsyncSession,
        conversation_id: str,
        config: AIEngineConfig,
        embedder: "Embedder | None" = None,
        llm: "LLMClient | None" = None,
    ) -> None:
        self._db = db
        self._conversation_id = conversation_id
        self._max_recent_turns = 3          # 固定窗口：最近 3 轮（6 条消息）
        self._max_relevant_turns = 3        # 向量检索：语义最相关 3 轮
        self._embedder = embedder           # 可选，有则启用向量检索
        self._llm = llm                     # 可选，有则启用画像提取
        self._history: list[dict] = []      # 最终组合后的历史消息
        self._profile: dict = {}            # 当前用户画像
        self._last_user_msg: str = ""       # 暂存用户消息，等 assistant 回复后一起提取画像

    # ── 公开接口 ──────────────────────────────────────────────────────────────

    async def load(self, message: str = "") -> None:
        """双轨加载：用户画像 + 组合历史消息。

        【加载策略】
        1. 从 user_profiles 表读取 JSONB 画像
        2. 从 chat_history 取最近 3 轮（近期上下文，顺序固定）
        3. 如果提供了 message 且有 embedder，用向量检索再捞 3 轮语义相关历史
        4. 合并去重，按时间排序，最终作为 LLM 的 messages 上下文

        【为什么是"近期3轮 + 相关3轮"而不是"近期10轮"？】
        - 近期3轮：保证对话连贯性（LLM 知道刚才在聊什么）
        - 相关3轮：把"早期说过但重要的内容"精准召回，不浪费 token
        - 总共最多 12 条消息，比原来的 20 条更省 token，信息密度更高
        """
        # Track 1：加载用户画像
        self._profile = await self._load_profile()

        # Track 2a：近期固定窗口（带 row id 用于去重）
        recent_rows = await self._fetch_recent_with_id()

        # Track 2b：语义相关历史（需要 embedder 和用户消息）
        relevant_rows = []
        if message and self._embedder:
            recent_ids = {r["_id"] for r in recent_rows}
            relevant_rows = await self._fetch_relevant_with_id(message, exclude_ids=recent_ids)

        # 合并：相关历史（较早） + 近期历史（较新），按时间排序后去重
        all_rows = relevant_rows + recent_rows
        seen_ids: set[int] = set()
        deduped: list[dict] = []
        for row in all_rows:
            if row["_id"] not in seen_ids:
                seen_ids.add(row["_id"])
                deduped.append(row)

        # 按数据库 ID 升序（= 时间顺序），LLM 需要看时间正确的对话
        deduped.sort(key=lambda r: r["_id"])

        # 剥掉内部字段，只保留 role/content 给 LLM
        self._history = [{"role": r["role"], "content": r["content"]} for r in deduped]

    def get_profile_context(self) -> str:
        """把用户画像格式化成一段文字，供 agent.py 追加到 system prompt 末尾。

        【示例输出】
        ── 用户已知信息 ──
        称呼：小明
        主要困扰：失眠、考试焦虑
        已尝试：冥想
        重要事件：期末周压力大
        偏好/禁忌：不喜欢说教
        当前情绪：焦虑中等

        画像为空时返回空字符串（不影响 system prompt）。
        """
        if not self._profile:
            return ""
        lines = ["── 用户已知信息 ──"]
        field_labels = {
            "nickname":       "称呼",
            "main_issues":    "主要困扰",
            "tried_methods":  "已尝试",
            "key_events":     "重要事件",
            "preferences":    "偏好/禁忌",
            "emotional_state":"当前情绪",
        }
        for field, label in field_labels.items():
            value = self._profile.get(field)
            if not value:
                continue
            if isinstance(value, list): # 判断value是不是list
                text_val = "、".join(str(v) for v in value if v)
            else:
                text_val = str(value)
            if text_val:
                lines.append(f"{label}：{text_val}")
        return "\n".join(lines) if len(lines) > 1 else ""

    def get_messages(self) -> list[dict]:
        """返回 OpenAI messages 格式的历史列表，直接传入 LLMClient。"""
        return list(self._history)

    async def save_turn(self, role: str, content: str) -> None:
        """保存一条消息到 chat_history。

        【两种情况】
        role='user'：
            - 写入数据库
            - 有 embedder 则同时计算并存储向量（供后续语义检索）
            - 暂存消息内容，等 assistant 回复后一起做画像提取

        role='assistant'：
            - 写入数据库（无需向量，不作为检索锚点）
            - 如果有 llm，触发画像提取（异步，不阻塞主流程）
        """
        if role == "user":
            await self._save_with_embedding(role, content)
            self._last_user_msg = content  # 暂存，等 assistant 回复后提取画像
        else:
            await self._save_plain(role, content)
            # 攒够一轮（user + assistant）才提取画像
            if self._llm and self._last_user_msg:
                await self._update_profile(self._last_user_msg, content)
                self._last_user_msg = ""  # 清空暂存

        self._history.append({"role": role, "content": content})

    # ── 私有：数据读写 ────────────────────────────────────────────────────────

    async def _save_plain(self, role: str, content: str) -> None:
        """写入不含向量的消息（assistant 消息）。"""
        sql = text("""
            INSERT INTO chat_history (conversation_id, role, content)
            VALUES (:conv_id, :role, :content)
        """)
        await self._db.execute(sql, {
            "conv_id": self._conversation_id, "role": role, "content": content,
        })
        await self._db.commit()

    async def _save_with_embedding(self, role: str, content: str) -> None:
        """写入含向量的消息（user 消息），向量用于后续语义相关历史检索。"""
        if self._embedder:
            vec = await self._embedder.embed(content)
            vl = "[" + ",".join(f"{v:.8f}" for v in vec) + "]"
            sql = text(f"""
                INSERT INTO chat_history (conversation_id, role, content, embedding)
                VALUES (:conv_id, :role, :content, '{vl}'::vector)
            """)
        else:
            # 没有 embedder 时退化为普通写入
            sql = text("""
                INSERT INTO chat_history (conversation_id, role, content)
                VALUES (:conv_id, :role, :content)
            """)
        await self._db.execute(sql, {
            "conv_id": self._conversation_id, "role": role, "content": content,
        })
        await self._db.commit()

    async def _fetch_recent_with_id(self) -> list[dict]:
        """取最近 N 轮（含内部 id 字段用于去重排序）。"""
        limit = self._max_recent_turns * 2  # 每轮 user + assistant 各一条
        sql = text("""
            SELECT id AS _id, role, content
            FROM (
                SELECT id, role, content, created_at
                FROM chat_history
                WHERE conversation_id = :conv_id
                ORDER BY created_at DESC
                LIMIT :limit
            ) sub
            ORDER BY sub.created_at ASC
        """)
        result = await self._db.execute(sql, {
            "conv_id": self._conversation_id, "limit": limit,
        })
        return [{"_id": r.id, "role": r.role, "content": r.content}
                for r in result.fetchall()]

    async def _fetch_relevant_with_id(
        self, query: str, exclude_ids: set[int]
    ) -> list[dict]:
        """向量检索：找出与当前问题语义最相关的历史用户消息，
        同时把对应的 assistant 回复一起拉出来（保持对话完整性）。

        【为什么只搜 user 消息？】
        用户的提问是语义锚点——"我失眠了"这条才是和当前问题对比的对象。
        assistant 的回复跟着 user 消息一起返回即可。
        """
        if not self._embedder:
            return []
        try:
            vec = await self._embedder.embed(query)
            vl = "[" + ",".join(f"{v:.8f}" for v in vec) + "]"

            # 找语义相似的历史用户消息（排除近期已有的，避免重复）
            sql = text(f"""
                SELECT id AS _id, role, content
                FROM chat_history
                WHERE conversation_id = :conv_id
                  AND role = 'user'
                  AND embedding IS NOT NULL
                  AND id != ALL(:exclude_ids)
                ORDER BY embedding <=> '{vl}'::vector
                LIMIT :k
            """)
            result = await self._db.execute(sql, {
                "conv_id": self._conversation_id,
                "exclude_ids": list(exclude_ids) or [0],
                "k": self._max_relevant_turns,
            })
            user_rows = result.fetchall()
            if not user_rows:
                return []

            # 对每条命中的用户消息，找紧跟其后的 assistant 回复
            # 原理：同一 conversation 里，assistant 消息的 id 紧跟 user 消息之后
            rows_out: list[dict] = []
            for user_row in user_rows:
                rows_out.append({
                    "_id": user_row._id,
                    "role": user_row.role,
                    "content": user_row.content,
                })
                # 找比该 user 消息 id 大的最近一条 assistant 消息
                sql_asst = text("""
                    SELECT id AS _id, role, content
                    FROM chat_history
                    WHERE conversation_id = :conv_id
                      AND role = 'assistant'
                      AND id > :user_id
                    ORDER BY id ASC
                    LIMIT 1
                """)
                asst_result = await self._db.execute(sql_asst, {
                    "conv_id": self._conversation_id,
                    "user_id": user_row._id,
                })
                asst_row = asst_result.fetchone()
                if asst_row:
                    rows_out.append({
                        "_id": asst_row._id,
                        "role": asst_row.role,
                        "content": asst_row.content,
                    })
            return rows_out
        except Exception:
            return []  # 向量检索失败时静默降级，不影响主流程

    # ── 私有：用户画像 CRUD ────────────────────────────────────────────────────

    async def _load_profile(self) -> dict:
        """从 user_profiles 表读取画像，不存在则返回空 dict。"""
        sql = text("""
            SELECT profile FROM user_profiles
            WHERE conversation_id = :conv_id
        """)
        result = await self._db.execute(sql, {"conv_id": self._conversation_id})
        row = result.fetchone()
        if row and row.profile:
            return dict(row.profile)
        return {}

    async def _update_profile(self, user_msg: str, assistant_msg: str) -> None:
        """用 LLM 从最新一轮对话里提取信息，增量合并到用户画像。

        【为什么在 assistant 回复后才提取，而不是 user 消息来了就提取？】
        LLM 的回复有时候会"引导"用户说出更多信息，
        等一轮结束后提取，能捕捉到更完整的上下文。

        【try/except 静默失败】
        画像提取是"锦上添花"，不是核心链路，失败不应该影响用户收到回复。
        """
        if not self._llm:
            return
        try:
            prompt = _PROFILE_EXTRACTION_PROMPT.format(
                current_profile=json.dumps(self._profile, ensure_ascii=False, indent=2),
                user_msg=user_msg,
                assistant_msg=assistant_msg,
            )
            raw = await self._llm.complete(
                system="你是信息提取专家，只输出合法 JSON，不附加任何说明文字。",
                messages=[{"role": "user", "content": prompt}],
            )
            new_profile = _parse_json_safely(raw)
            if new_profile:
                merged = _merge_profiles(self._profile, new_profile)
                await self._save_profile(merged)
                self._profile = merged
        except Exception:
            pass  # 画像提取失败不影响主流程

    async def _save_profile(self, profile: dict) -> None:
        """UPSERT 用户画像（有则更新，无则插入）。"""
        sql = text("""
            INSERT INTO user_profiles (conversation_id, profile, updated_at)
            VALUES (:conv_id, CAST(:profile AS jsonb), NOW())
            ON CONFLICT (conversation_id)
            DO UPDATE SET profile = CAST(:profile AS jsonb), updated_at = NOW()
        """)
        await self._db.execute(sql, {
            "conv_id": self._conversation_id,
            "profile": json.dumps(profile, ensure_ascii=False),
        })
        await self._db.commit()


# ── 纯函数工具 ────────────────────────────────────────────────────────────────

def _parse_json_safely(raw: str) -> dict | None:
    """从 LLM 输出中提取 JSON，容忍 LLM 在 JSON 前后输出多余文字的情况。

    LLM 有时候会输出：
        "好的，以下是提取结果：\n{...}\n希望有帮助"
    用正则找到第一个 {...} 块，尝试解析。
    """
    raw = raw.strip()
    # 优先直接解析（LLM 乖乖只输出 JSON 时）
    try:
        result = json.loads(raw)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    # 用正则找 JSON 块（贪婪匹配最外层花括号）
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
    return None


def _merge_profiles(old: dict, new: dict) -> dict:
    """把新提取的画像增量合并到旧画像中。

    合并规则：
    - 数组字段（main_issues / tried_methods / key_events / preferences）：
      累积追加，去重，不覆盖
    - 字符串字段（nickname / emotional_state）：
      新值非空则覆盖（情绪状态应该反映最新情况）
    - 旧有字段新值为空时保留旧值（不清空）
    """
    merged = dict(old)
    list_fields = {"main_issues", "tried_methods", "key_events", "preferences"}
    for key, new_val in new.items():
        if not new_val and new_val != 0:  # 跳过空值
            continue
        if key in list_fields:
            # 数组合并去重（保持插入顺序）
            existing: list = merged.get(key, [])
            for item in (new_val if isinstance(new_val, list) else [new_val]):
                if item and item not in existing:
                    existing.append(item)
            merged[key] = existing
        else:
            # 字符串字段：新值非空则覆盖
            merged[key] = new_val
    return merged
