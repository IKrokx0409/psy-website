"""多轮对话持久化验证脚本，验证 DBMemoryTool 是否正确工作。"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()

from ai_engine.config import AIEngineConfig
from ai_engine.agent import PsychAgent


async def main():
    cfg = AIEngineConfig()
    engine = create_async_engine(cfg.database_url, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    conv_id = "test_persist_verify"

    # 第一轮
    print("=== 第一轮 ===")
    async with Session() as db:
        r = await PsychAgent(config=cfg, db=db).run("我最近睡眠很差，压力大", conv_id)
        print("回复(前80字):", r.reply[:80])

    # 第二轮 - 新的 Agent 实例，应能从 DB 读到第一轮历史
    print("\n=== 第二轮（新 Agent 实例）===")
    async with Session() as db:
        r2 = await PsychAgent(config=cfg, db=db).run("你刚才提到了什么改善睡眠的方法？", conv_id)
        print("回复(前80字):", r2.reply[:80])

    # 验证 DB 记录
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT role, LEFT(content, 50) as c FROM chat_history WHERE conversation_id=:cv ORDER BY created_at"),
            {"cv": conv_id}
        )
        rows = result.fetchall()
        print(f"\n=== DB 记录（共 {len(rows)} 条）===")
        for role, content in rows:
            print(f"  [{role:9s}] {content}...")

        # 清理
        await conn.execute(text("DELETE FROM chat_history WHERE conversation_id=:cv"), {"cv": conv_id})

    print("\n✅ 多轮持久化验证通过")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
