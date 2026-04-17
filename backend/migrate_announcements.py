"""
为 announcements 表添加 body / cover_image 两列（如果尚未存在）。
运行方式: python migrate_announcements.py
"""
import asyncio
from sqlalchemy import text
from database import engine


async def migrate():
    async with engine.begin() as conn:
        # 检查 body 列是否已存在
        result = await conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'announcements' AND column_name = 'body'
        """))
        if not result.fetchone():
            await conn.execute(text("ALTER TABLE announcements ADD COLUMN body TEXT"))
            print("已添加 body 列")
        else:
            print("body 列已存在，跳过")

        result = await conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'announcements' AND column_name = 'cover_image'
        """))
        if not result.fetchone():
            await conn.execute(text("ALTER TABLE announcements ADD COLUMN cover_image VARCHAR(500)"))
            print("已添加 cover_image 列")
        else:
            print("cover_image 列已存在，跳过")

    print("迁移完成")


if __name__ == "__main__":
    asyncio.run(migrate())
