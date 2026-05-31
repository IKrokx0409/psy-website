"""
测试数据生成脚本
- 学生 student001 ~ student020，7天日记记录（随机缺勤，模拟真实情况）
- 教师 teacher001，创建课程 + 两个班级
  - 班A：student001 ~ student010
  - 班B：student011 ~ student020
- 每班各发布 4 种作业（checkin / qa / paper / chat），有效期 2026-05-01 ~ 2026-06-30
运行：python seed_test_data.py
"""

import asyncio
import json
import random
from datetime import date, timedelta

from sqlalchemy import select, delete
from database import AsyncSessionLocal
from models import (
    Course, ClassGroup, ClassMember,
    DiaryEntry, Assignment,
)

TEACHER_ID = "teacher001"
TODAY = date(2026, 5, 31)
DIARY_DAYS = [(TODAY - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]  # 5.25~5.31

MOOD_MAP = {
    (1, 2):  ("很差",  ["低落", "绝望", "麻木", "疲惫"]),
    (3, 4):  ("较差",  ["焦虑", "烦躁", "沮丧", "担心"]),
    (5, 6):  ("一般",  ["平静", "无聊", "迷茫", "还好"]),
    (7, 8):  ("较好",  ["开心", "满足", "轻松", "充实"]),
    (9, 10): ("很好",  ["愉快", "兴奋", "感恩", "自信"]),
}

DIARY_TEMPLATES = {
    "很差": ["今天状态很差，什么都不想做。", "感觉很低落，难以集中精神。"],
    "较差": ["今天有些焦虑，事情压着没处理。", "心情不太好，睡眠也不好。"],
    "一般": ["今天平平淡淡，没什么特别的。", "还好，不算差，不算好。"],
    "较好": ["今天过得不错，完成了一些计划。", "心情挺好的，效率也高。"],
    "很好": ["今天很充实，感觉很棒！", "心情很愉快，和朋友聊了很多。"],
}

ASSIGNMENTS = [
    {
        "type": "checkin",
        "title": "每日情绪打卡（5-6月）",
        "description": "请每天记录你的情绪状态，完成情绪打卡任务。",
        "due_date": "2026-06-30",
        "required_days": 30,
        "start_date": "2026-05-01",
    },
    {
        "type": "qa",
        "title": "心理健康知识测验",
        "description": "回答以下关于心理健康的问题，没有标准答案，请真实作答。",
        "due_date": "2026-06-30",
        "questions_json": json.dumps([
            {"text": "你通常用什么方式缓解压力？"},
            {"text": "当你感到焦虑时，你会怎么做？"},
            {"text": "你认为什么对你的心理健康最重要？"},
        ], ensure_ascii=False),
    },
    {
        "type": "paper",
        "title": "心理成长反思报告",
        "description": "结合本学期学习，撰写一篇关于个人心理成长的反思报告（800字以上）。",
        "due_date": "2026-06-30",
        "submission_mode": "markdown",
    },
    {
        "type": "chat",
        "title": "AI 心理对话练习",
        "description": "与 AI 心理助手完成至少 5 轮有效对话，探索你当前的心理状态。",
        "due_date": "2026-06-30",
        "required_rounds": 5,
    },
]


def mood_for_score(score):
    for (lo, hi), (label, emotions) in MOOD_MAP.items():
        if lo <= score <= hi:
            return label, emotions
    return "一般", ["平静"]


async def main():
    async with AsyncSessionLocal() as db:

        # ── 清理旧测试数据 ──────────────────────────────────────────────────────
        print("清理旧测试数据...")
        existing_courses = await db.execute(
            select(Course).where(Course.teacher_id == TEACHER_ID)
        )
        for course in existing_courses.scalars().all():
            class_ids = (await db.execute(
                select(ClassGroup.id).where(ClassGroup.course_id == course.id)
            )).scalars().all()
            for cid in class_ids:
                await db.execute(delete(Assignment).where(Assignment.class_id == cid))
                await db.execute(delete(ClassMember).where(ClassMember.class_id == cid))
            await db.execute(delete(ClassGroup).where(ClassGroup.course_id == course.id))
            await db.execute(delete(Course).where(Course.id == course.id))

        student_ids = [f"student{i:03d}" for i in range(1, 21)]
        await db.execute(
            delete(DiaryEntry).where(DiaryEntry.user_id.in_(student_ids))
        )
        await db.commit()

        # ── 课程 ────────────────────────────────────────────────────────────────
        print("创建课程...")
        course = Course(
            name="大学生心理健康教育",
            semester="2025-2026-2",
            teacher_id=TEACHER_ID,
            description="面向全体在校学生的心理健康教育课程，涵盖情绪管理、压力应对、人际关系等模块。",
        )
        db.add(course)
        await db.flush()

        # ── 两个班级 ────────────────────────────────────────────────────────────
        class_a = ClassGroup(course_id=course.id, name="计算机2301班", teacher_id=TEACHER_ID)
        class_b = ClassGroup(course_id=course.id, name="软件工程2302班", teacher_id=TEACHER_ID)
        db.add_all([class_a, class_b])
        await db.flush()

        # ── 班级成员 ────────────────────────────────────────────────────────────
        print("添加学生成员...")
        for i in range(1, 21):
            sid = f"student{i:03d}"
            sname = f"测试学生{i:03d}"
            cls = class_a if i <= 10 else class_b
            db.add(ClassMember(class_id=cls.id, student_id=sid, student_name=sname))

        # ── 日记记录（7天，随机缺勤率 ~25%）────────────────────────────────────
        print("生成日记记录...")
        diary_count = 0
        for i in range(1, 21):
            sid = f"student{i:03d}"
            for day in DIARY_DAYS:
                if random.random() < 0.25:   # 25% 概率当天没写
                    continue
                score = random.randint(1, 10)
                label, emotion_pool = mood_for_score(score)
                emotions = random.sample(emotion_pool, k=min(2, len(emotion_pool)))
                content = random.choice(DIARY_TEMPLATES[label])
                db.add(DiaryEntry(
                    user_id=sid,
                    date=day,
                    mood_score=score,
                    mood_label=label,
                    emotions=emotions,
                    content=content,
                ))
                diary_count += 1

        # ── 作业（每班各 4 种）──────────────────────────────────────────────────
        print("发布作业...")
        for cls in [class_a, class_b]:
            for tmpl in ASSIGNMENTS:
                db.add(Assignment(
                    class_id=cls.id,
                    title=tmpl["title"],
                    description=tmpl.get("description"),
                    due_date=tmpl.get("due_date"),
                    type=tmpl["type"],
                    required_days=tmpl.get("required_days"),
                    start_date=tmpl.get("start_date"),
                    required_rounds=tmpl.get("required_rounds"),
                    questions_json=tmpl.get("questions_json"),
                    submission_mode=tmpl.get("submission_mode"),
                ))

        await db.commit()

    print(f"\n完成！")
    print(f"  课程：大学生心理健康教育（teacher001）")
    print(f"  班级：计算机2301班（student001-010）/ 软件工程2302班（student011-020）")
    print(f"  日记条目：{diary_count} 条（7天，~25%缺勤）")
    print(f"  作业：每班 4 种 × 2 班 = 8 条，有效期 2026-05-01 ~ 2026-06-30")


if __name__ == "__main__":
    asyncio.run(main())
