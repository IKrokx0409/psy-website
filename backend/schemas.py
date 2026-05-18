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
    visibility: str = Field("public", pattern="^(public|bottle_only)$")


class TreeholePostOut(BaseModel):
    id: int
    anonymous_name: str
    content: str
    tags: List[str]
    visibility: str
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


# ── Course ────────────────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    name:        str  = Field(..., min_length=1, max_length=100)
    semester:    str  = Field(..., min_length=1, max_length=30)
    teacher_id:  str
    description: Optional[str] = None

class CourseOut(BaseModel):
    id:          int
    name:        str
    semester:    str
    teacher_id:  str
    description: Optional[str] = None
    created_at:  datetime
    model_config = {"from_attributes": True}


# ── ClassGroup ────────────────────────────────────────────────────────────────

class ClassGroupCreate(BaseModel):
    name:       str = Field(..., min_length=1, max_length=100)
    teacher_id: str

class ClassGroupOut(BaseModel):
    id:         int
    course_id:  int
    name:       str
    teacher_id: str
    created_at: datetime
    model_config = {"from_attributes": True}

class ClassGroupDetail(ClassGroupOut):
    member_count:     int = 0
    assignment_count: int = 0
    thread_count:     int = 0


# ── ClassMember ───────────────────────────────────────────────────────────────

class MemberAdd(BaseModel):
    student_id:   str = Field(..., min_length=1, max_length=50)
    student_name: str = Field(..., min_length=1, max_length=50)

class MemberOut(BaseModel):
    id:           int
    student_id:   str
    student_name: str
    added_at:     datetime
    model_config = {"from_attributes": True}


# ── Assignment ────────────────────────────────────────────────────────────────

class AssignmentCreate(BaseModel):
    title:           str  = Field(..., min_length=1, max_length=200)
    description:     Optional[str] = None
    due_date:        Optional[str] = None
    type:            str  = Field(..., pattern="^(checkin|qa|paper|chat)$")
    # 情绪打卡
    required_days:   Optional[int] = Field(None, ge=1)
    start_date:      Optional[str] = None
    # AI对话
    required_rounds: Optional[int] = Field(None, ge=1)
    # 课堂问答
    questions_json:  Optional[str] = None   # JSON string
    # 综合作业
    submission_mode: Optional[str] = Field(None, pattern="^(file|markdown|both)$")

class AssignmentUpdate(BaseModel):
    title:           Optional[str] = Field(None, min_length=1, max_length=200)
    description:     Optional[str] = None
    due_date:        Optional[str] = None
    required_days:   Optional[int] = Field(None, ge=1)
    start_date:      Optional[str] = None
    required_rounds: Optional[int] = Field(None, ge=1)
    questions_json:  Optional[str] = None
    submission_mode: Optional[str] = Field(None, pattern="^(file|markdown|both)$")

class AssignmentOut(BaseModel):
    id:              int
    class_id:        int
    title:           str
    description:     Optional[str] = None
    due_date:        Optional[str] = None
    type:            str
    required_days:   Optional[int] = None
    start_date:      Optional[str] = None
    required_rounds: Optional[int] = None
    questions_json:  Optional[str] = None
    submission_mode: Optional[str] = None
    created_at:      datetime
    model_config = {"from_attributes": True}

class AssignmentWithStats(AssignmentOut):
    submission_count: int = 0
    graded_count:     int = 0


# ── Submission ────────────────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    student_id:   str
    student_name: str
    content:      Optional[str] = None       # paper markdown
    answers_json: Optional[str] = None       # qa answers

class SubmissionGrade(BaseModel):
    score:           Optional[int] = Field(None, ge=0, le=100)
    teacher_comment: Optional[str] = None

class SubmissionOut(BaseModel):
    id:              int
    assignment_id:   int
    student_id:      str
    student_name:    str
    content:         Optional[str] = None
    answers_json:    Optional[str] = None
    file_path:       Optional[str] = None
    file_name:       Optional[str] = None
    score:           Optional[int] = None
    teacher_comment: Optional[str] = None
    submitted_at:    datetime
    graded_at:       Optional[datetime] = None
    model_config = {"from_attributes": True}

class CheckinProgress(BaseModel):
    assignment_id: int
    student_id:    str
    completed_days: int
    required_days:  int

class CheckinMemberStat(BaseModel):
    student_id:     str
    student_name:   str
    completed_days: int
    required_days:  int

class ChatProgress(BaseModel):
    assignment_id:    int
    student_id:       str
    completed_rounds: int
    required_rounds:  int

class ChatMemberStat(BaseModel):
    student_id:       str
    student_name:     str
    completed_rounds: int
    required_rounds:  int


# ── CourseGroup (小组讨论) ─────────────────────────────────────────────────────

class CourseGroupCreate(BaseModel):
    name:       str = Field(..., min_length=1, max_length=100)
    member_ids: List[str] = []

class CourseGroupOut(BaseModel):
    id:         int
    class_id:   int
    name:       str
    member_ids: List[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class GroupMessageCreate(BaseModel):
    author_id:   str
    author_name: str
    content:     str = Field(..., min_length=1)

class GroupMessageOut(BaseModel):
    id:          int
    group_id:    int
    author_id:   str
    author_name: str
    content:     str
    created_at:  datetime
    model_config = {"from_attributes": True}


class GroupConclusionOut(BaseModel):
    group_id:        int
    content:         str
    updated_by_id:   Optional[str] = None
    updated_by_name: Optional[str] = None
    updated_at:      Optional[datetime] = None
    model_config = {"from_attributes": True}


class GroupConclusionUpdate(BaseModel):
    content:         str
    updated_by_id:   str
    updated_by_name: str


class CourseGroupSummary(CourseGroupOut):
    message_count: int = 0
    conclusion:    Optional[GroupConclusionOut] = None


# ── Discussion ────────────────────────────────────────────────────────────────

class ThreadCreate(BaseModel):
    author_id:   str
    author_name: str
    title:       str  = Field(..., min_length=1, max_length=200)
    content:     Optional[str] = None

class ReplyCreate(BaseModel):
    author_id:   str
    author_name: str
    content:     str = Field(..., min_length=1)

class ReplyOut(BaseModel):
    id:          int
    thread_id:   int
    author_id:   str
    author_name: str
    content:     str
    created_at:  datetime
    model_config = {"from_attributes": True}

class ThreadOut(BaseModel):
    id:          int
    class_id:    int
    author_id:   str
    author_name: str
    title:       str
    content:     Optional[str] = None
    pinned:      bool
    created_at:  datetime
    model_config = {"from_attributes": True}

class ThreadWithReplies(ThreadOut):
    replies: List[ReplyOut] = []

class ThreadListItem(ThreadOut):
    reply_count: int = 0
