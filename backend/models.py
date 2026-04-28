from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from database import Base



class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(20), nullable=False)   # 中心公告 / 活动预告 / 心理讲座
    published_at = Column(String(20))               # "2026-04-07" 字符串，便于排序显示
    is_published = Column(Boolean, default=True)
    body = Column(Text, nullable=True)              # Markdown 正文
    cover_image = Column(String(500), nullable=True) # 封面图 URL（可选）
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TreeholePost(Base):
    __tablename__ = "treehole_posts"

    id = Column(Integer, primary_key=True, index=True)
    anonymous_name = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=[])
    # pending → approved / rejected；approved → delete_requested
    status = Column(String(20), nullable=False, default="pending")
    author_token = Column(String(64), nullable=False)   # 不对外暴露，用于验证删除权限
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(30), nullable=False)   # 情绪管理/压力应对/人际关系/睡眠健康/危机干预
    summary = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)            # Markdown 正文
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    questions_json = Column(Text, nullable=False, default="[]")  # JSON array
    scoring_json = Column(Text, nullable=False, default="[]")    # JSON array
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    date = Column(String(10), nullable=False)           # YYYY-MM-DD
    mood_score = Column(Integer, nullable=False)         # 1–10
    mood_label = Column(String(20))
    emotions = Column(ARRAY(String), default=[])
    content = Column(Text, default="")
    json_data = Column(Text)                             # JSON string for Agent workflow
    ai_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── 心理课 ────────────────────────────────────────────────────────────────────

class Course(Base):
    __tablename__ = "courses"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)       # 课程名称
    semester    = Column(String(30),  nullable=False)       # 如 2025-2026-2
    teacher_id  = Column(String(50),  nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class ClassGroup(Base):
    __tablename__ = "class_groups"

    id         = Column(Integer, primary_key=True, index=True)
    course_id  = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    name       = Column(String(100), nullable=False)        # 班级名称，如"计算机2301班"
    teacher_id = Column(String(50),  nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ClassMember(Base):
    __tablename__ = "class_members"

    id           = Column(Integer, primary_key=True, index=True)
    class_id     = Column(Integer, ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False)
    student_id   = Column(String(50), nullable=False)
    student_name = Column(String(50), nullable=False)
    added_at     = Column(DateTime(timezone=True), server_default=func.now())


class Assignment(Base):
    __tablename__ = "assignments"

    id              = Column(Integer, primary_key=True, index=True)
    class_id        = Column(Integer, ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False)
    title           = Column(String(200), nullable=False)
    description     = Column(Text, nullable=True)           # Markdown，所有类型通用
    due_date        = Column(String(10),  nullable=True)    # YYYY-MM-DD
    type            = Column(String(20),  nullable=False, default="qa")  # checkin|qa|paper
    # 情绪打卡专属
    required_days   = Column(Integer,     nullable=True)    # 要求天数
    start_date      = Column(String(10),  nullable=True)    # 统计起始日期
    # 课堂问答专属
    questions_json  = Column(Text,        nullable=True)    # JSON: [{text, description?}]
    # 综合作业专属
    submission_mode = Column(String(20),  nullable=True)    # file|markdown|both
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class Submission(Base):
    __tablename__ = "submissions"

    id              = Column(Integer, primary_key=True, index=True)
    assignment_id   = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id      = Column(String(50), nullable=False)
    student_name    = Column(String(50), nullable=False)
    content         = Column(Text, nullable=True)           # paper markdown 正文
    answers_json    = Column(Text, nullable=True)           # qa 逐题回答 JSON
    file_path       = Column(String(500), nullable=True)    # paper 文件路径
    file_name       = Column(String(200), nullable=True)    # paper 原始文件名
    score           = Column(Integer, nullable=True)        # 0–100
    teacher_comment = Column(Text, nullable=True)
    submitted_at    = Column(DateTime(timezone=True), server_default=func.now())
    graded_at       = Column(DateTime(timezone=True), nullable=True)


class CourseGroup(Base):
    """小组讨论 — 班级内的小组"""
    __tablename__ = "course_groups"

    id         = Column(Integer, primary_key=True, index=True)
    class_id   = Column(Integer, ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False)
    name       = Column(String(100), nullable=False)
    member_ids = Column(ARRAY(String), default=[])          # student_id 列表
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GroupMessage(Base):
    """小组讨论消息"""
    __tablename__ = "group_messages"

    id          = Column(Integer, primary_key=True, index=True)
    group_id    = Column(Integer, ForeignKey("course_groups.id", ondelete="CASCADE"), nullable=False)
    author_id   = Column(String(50), nullable=False)
    author_name = Column(String(50), nullable=False)
    content     = Column(Text, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class DiscussionThread(Base):
    __tablename__ = "discussion_threads"

    id          = Column(Integer, primary_key=True, index=True)
    class_id    = Column(Integer, ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False)
    author_id   = Column(String(50), nullable=False)
    author_name = Column(String(50), nullable=False)
    title       = Column(String(200), nullable=False)
    content     = Column(Text, nullable=True)
    pinned      = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class DiscussionReply(Base):
    __tablename__ = "discussion_replies"

    id          = Column(Integer, primary_key=True, index=True)
    thread_id   = Column(Integer, ForeignKey("discussion_threads.id", ondelete="CASCADE"), nullable=False)
    author_id   = Column(String(50), nullable=False)
    author_name = Column(String(50), nullable=False)
    content     = Column(Text, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
