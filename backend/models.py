from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
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
