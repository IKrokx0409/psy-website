"""
初始化数据库种子数据，已有数据时自动跳过。
运行方式: python seed.py
"""
import asyncio
import secrets
from sqlalchemy import select

from database import engine, AsyncSessionLocal
from models import Base, Announcement, TreeholePost

ANNOUNCEMENTS = [
    {"title": '关于开展2026年春季"5·25"心理健康月系列活动的通知', "category": "中心公告", "published_at": "2026-04-07"},
    {"title": "心理健康教育与咨询中心2026年春季预约咨询安排",       "category": "中心公告", "published_at": "2026-04-01"},
    {"title": "关于心理测评系统维护升级的通知",                      "category": "中心公告", "published_at": "2026-03-25"},
    {"title": "2025-2026学年秋季心理普查结果反馈说明",              "category": "中心公告", "published_at": "2026-03-18"},
    {"title": '团体心理辅导"压力管理"课程开放报名',                  "category": "中心公告", "published_at": "2026-03-10"},
    {"title": "心理危机干预工作规范（修订版）正式施行",               "category": "中心公告", "published_at": "2026-03-01"},
    {"title": "【5·25系列】正念减压体验工作坊（第一期）",            "category": "活动预告", "published_at": "2026-04-15"},
    {"title": "大学生情绪管理专题沙龙 — 如何与焦虑共处",            "category": "活动预告", "published_at": "2026-04-20"},
    {"title": '"心灵绿洲"户外团体活动报名开启',                     "category": "活动预告", "published_at": "2026-04-22"},
    {"title": "2026届毕业生压力疏导专场团辅",                       "category": "活动预告", "published_at": "2026-04-28"},
    {"title": "人际关系与沟通技巧训练营（四期）",                    "category": "活动预告", "published_at": "2026-05-06"},
    {"title": "全国大学生心理健康日线上直播答疑",                    "category": "活动预告", "published_at": "2026-05-25"},
    {"title": "【讲座】睡眠与心理健康 — 为什么你总睡不好？",        "category": "心理讲座", "published_at": "2026-04-10"},
    {"title": "【讲座】如何建立安全的亲密关系",                      "category": "心理讲座", "published_at": "2026-04-17"},
    {"title": "【讲座】学业拖延背后的心理机制与应对",                "category": "心理讲座", "published_at": "2026-04-24"},
    {"title": "【讲座】抑郁情绪识别与自我关怀",                      "category": "心理讲座", "published_at": "2026-05-08"},
    {"title": "【讲座】大学生职业规划中的心理适应",                  "category": "心理讲座", "published_at": "2026-05-15"},
    {"title": "【讲座】正念冥想入门：活在当下的科学方法",            "category": "心理讲座", "published_at": "2026-05-22"},
]

TREEHOLE_POSTS = [
    {
        "anonymous_name": "迷路的云朵",
        "content": "最近论文压力太大了，感觉每天都睡不好，不知道自己还能撑多久。但又不知道跟谁说，怕麻烦别人……",
        "tags": ["学业压力"],
        "status": "approved",
    },
    {
        "anonymous_name": "温柔的水獭",
        "content": "和室友的关系越来越僵，宿舍气氛很压抑。每次回宿舍都很煎熬，不知道要怎么开口和解。",
        "tags": ["人际关系"],
        "status": "approved",
    },
    {
        "anonymous_name": "快乐的薯条",
        "content": "今天和同学一起去看了日落，真的很美，心情莫名变好了很多。分享一下这份快乐 🌅",
        "tags": ["分享快乐"],
        "status": "approved",
    },
    {
        "anonymous_name": "好奇的松鼠",
        "content": "看到周围同学陆续拿到实习 offer，自己投了很多简历却没有回音，开始怀疑自己是不是真的很差。",
        "tags": ["就业焦虑"],
        "status": "approved",
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing_ann = (await db.execute(select(Announcement).limit(1))).scalar_one_or_none()
        if not existing_ann:
            for a in ANNOUNCEMENTS:
                db.add(Announcement(**a))
            print(f"写入 {len(ANNOUNCEMENTS)} 条公告")
        else:
            print("公告数据已存在，跳过")

        existing_post = (await db.execute(select(TreeholePost).limit(1))).scalar_one_or_none()
        if not existing_post:
            for p in TREEHOLE_POSTS:
                db.add(TreeholePost(**p, author_token=secrets.token_hex(32)))
            print(f"写入 {len(TREEHOLE_POSTS)} 条树洞示例")
        else:
            print("树洞数据已存在，跳过")

        await db.commit()

    print("完成")


if __name__ == "__main__":
    asyncio.run(seed())
