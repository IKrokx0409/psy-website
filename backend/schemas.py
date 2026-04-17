from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ── Announcement ──────────────────────────────────────────────────────────────

class AnnouncementListItem(BaseModel):
    """列表页使用，不含正文以节省带宽"""
    id: int
    title: str
    category: str
    published_at: Optional[str] = None
    cover_image: Optional[str] = None

    model_config = {"from_attributes": True}


class AnnouncementOut(BaseModel):
    """详情页使用，含完整正文"""
    id: int
    title: str
    category: str
    published_at: Optional[str] = None
    body: Optional[str] = None
    cover_image: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Treehole ──────────────────────────────────────────────────────────────────

class TreeholePostCreate(BaseModel):
    anonymous_name: str = Field(..., min_length=2, max_length=20)
    content: str = Field(..., min_length=5, max_length=500)
    tags: List[str] = []


class TreeholePostOut(BaseModel):
    id: int
    anonymous_name: str
    content: str
    tags: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TreeholePostCreateResponse(TreeholePostOut):
    """发帖成功时返回，额外携带 author_token 供前端保存"""
    author_token: str


class DeleteRequest(BaseModel):
    author_token: str


# ── Admin ─────────────────────────────────────────────────────────────────────

class TreeholePostAdminOut(BaseModel):
    id: int
    anonymous_name: str
    content: str
    tags: List[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewAction(BaseModel):
    action: str  # "approve" | "reject"


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., pattern="^(中心公告|活动预告|心理讲座)$")
    published_at: Optional[str] = None
    is_published: bool = True
    body: Optional[str] = None
    cover_image: Optional[str] = None


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, pattern="^(中心公告|活动预告|心理讲座)$")
    published_at: Optional[str] = None
    is_published: Optional[bool] = None
    body: Optional[str] = None
    cover_image: Optional[str] = None


class AnnouncementAdminOut(BaseModel):
    id: int
    title: str
    category: str
    published_at: Optional[str] = None
    is_published: bool
    body: Optional[str] = None
    cover_image: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Resource ──────────────────────────────────────────────────────────────────

RESOURCE_CATEGORIES = {"情绪管理", "压力应对", "人际关系", "睡眠健康", "危机干预"}

class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    is_published: bool = True

class ResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    is_published: Optional[bool] = None

class ResourceListItem(BaseModel):
    id: int
    title: str
    category: str
    summary: Optional[str] = None
    is_published: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class ResourceOut(BaseModel):
    id: int
    title: str
    category: str
    summary: Optional[str] = None
    content: Optional[str] = None
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ── Questionnaire ──────────────────────────────────────────────────────────────

class QuestionnaireCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    questions_json: str = "[]"
    scoring_json: str = "[]"
    is_published: bool = True

class QuestionnaireUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    questions_json: Optional[str] = None
    scoring_json: Optional[str] = None
    is_published: Optional[bool] = None

class QuestionnaireListItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_published: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class QuestionnaireOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    questions_json: str
    scoring_json: str
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ── Diary ─────────────────────────────────────────────────────────────────────

class DiaryEntryCreate(BaseModel):
    user_id: str
    date: str                                    # YYYY-MM-DD
    mood_score: int = Field(..., ge=1, le=10)
    mood_label: Optional[str] = None
    emotions: List[str] = []
    content: str = ""
    json_data: Optional[str] = None              # JSON string


class DiaryEntryUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    mood_label: Optional[str] = None
    emotions: Optional[List[str]] = None
    content: Optional[str] = None
    json_data: Optional[str] = None
    ai_feedback: Optional[str] = None


class DiaryEntryOut(BaseModel):
    id: int
    user_id: str
    date: str
    mood_score: int
    mood_label: Optional[str] = None
    emotions: List[str]
    content: str
    json_data: Optional[str] = None
    ai_feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
