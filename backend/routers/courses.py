import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from models import (
    Course, ClassGroup, ClassMember,
    Assignment, Submission,
    DiscussionThread, DiscussionReply,
    CourseGroup, GroupMessage, GroupConclusion,
    DiaryEntry, ChatRecord,
)
from schemas import (
    CourseCreate, CourseOut,
    ClassGroupCreate, ClassGroupOut, ClassGroupDetail,
    MemberAdd, MemberOut,
    AssignmentCreate, AssignmentUpdate, AssignmentOut, AssignmentWithStats,
    SubmissionCreate, SubmissionGrade, SubmissionOut,
    CheckinProgress, CheckinMemberStat,
    ChatProgress, ChatMemberStat,
    ThreadCreate, ReplyCreate, ReplyOut,
    ThreadOut, ThreadWithReplies, ThreadListItem,
    CourseGroupCreate, CourseGroupOut, CourseGroupSummary,
    GroupMessageCreate, GroupMessageOut,
    GroupConclusionOut, GroupConclusionUpdate,
)

router = APIRouter(prefix="/api", tags=["courses"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTS = {".pdf", ".docx", ".doc", ".zip", ".rar", ".md", ".txt"}


# ── 课程 ──────────────────────────────────────────────────────────────────────

@router.get("/courses", response_model=List[CourseOut])
async def list_courses(teacher_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course).where(Course.teacher_id == teacher_id).order_by(Course.created_at.desc())
    )
    return result.scalars().all()


@router.post("/courses", response_model=CourseOut)
async def create_course(data: CourseCreate, db: AsyncSession = Depends(get_db)):
    course = Course(**data.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "课程不存在")
    await db.delete(course)
    await db.commit()
    return {"ok": True}


# ── 班级 ──────────────────────────────────────────────────────────────────────

async def _fetch_class_stats(ids: list, db: AsyncSession):
    def _count_by(col, table):
        return select(col, func.count().label("cnt")).where(col.in_(ids)).group_by(col)

    member_rows = (await db.execute(_count_by(ClassMember.class_id, ClassMember))).all()
    assign_rows = (await db.execute(_count_by(Assignment.class_id, Assignment))).all()
    thread_rows = (await db.execute(_count_by(DiscussionThread.class_id, DiscussionThread))).all()
    return (
        {r[0]: r[1] for r in member_rows},
        {r[0]: r[1] for r in assign_rows},
        {r[0]: r[1] for r in thread_rows},
    )


async def _class_detail(g, db, mc=0, ac=0, tc=0) -> ClassGroupDetail:
    d = ClassGroupDetail.model_validate(g)
    d.member_count, d.assignment_count, d.thread_count = mc, ac, tc
    return d


@router.get("/courses/{course_id}/classes", response_model=List[ClassGroupDetail])
async def list_classes(course_id: int, db: AsyncSession = Depends(get_db)):
    groups = (await db.execute(
        select(ClassGroup).where(ClassGroup.course_id == course_id).order_by(ClassGroup.created_at)
    )).scalars().all()
    if not groups:
        return []
    ids = [g.id for g in groups]
    members, assigns, threads = await _fetch_class_stats(ids, db)
    return [
        await _class_detail(g, db, members.get(g.id, 0), assigns.get(g.id, 0), threads.get(g.id, 0))
        for g in groups
    ]


@router.post("/courses/{course_id}/classes", response_model=ClassGroupOut)
async def create_class(course_id: int, data: ClassGroupCreate, db: AsyncSession = Depends(get_db)):
    if not (await db.execute(select(Course).where(Course.id == course_id))).scalar_one_or_none():
        raise HTTPException(404, "课程不存在")
    group = ClassGroup(course_id=course_id, **data.model_dump())
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.get("/classes/{class_id}", response_model=ClassGroupDetail)
async def get_class(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClassGroup).where(ClassGroup.id == class_id))
    g = result.scalar_one_or_none()
    if not g:
        raise HTTPException(404, "班级不存在")
    members, assigns, threads = await _fetch_class_stats([class_id], db)
    return await _class_detail(g, db, members.get(class_id, 0), assigns.get(class_id, 0), threads.get(class_id, 0))


@router.patch("/classes/{class_id}", response_model=ClassGroupOut)
async def update_class(class_id: int, data: ClassGroupCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClassGroup).where(ClassGroup.id == class_id))
    g = result.scalar_one_or_none()
    if not g:
        raise HTTPException(404, "班级不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(g, k, v)
    await db.commit()
    await db.refresh(g)
    return g


@router.delete("/classes/{class_id}")
async def delete_class(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClassGroup).where(ClassGroup.id == class_id))
    g = result.scalar_one_or_none()
    if not g:
        raise HTTPException(404, "班级不存在")
    await db.delete(g)
    await db.commit()
    return {"ok": True}


# ── 学生：查询我所在的班级 ────────────────────────────────────────────────────

@router.get("/my/classes", response_model=List[ClassGroupDetail])
async def my_classes(student_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    memberships = (await db.execute(
        select(ClassMember).where(ClassMember.student_id == student_id)
    )).scalars().all()
    if not memberships:
        return []
    ids = [m.class_id for m in memberships]
    groups = (await db.execute(select(ClassGroup).where(ClassGroup.id.in_(ids)))).scalars().all()
    if not groups:
        return []
    members, assigns, threads = await _fetch_class_stats([g.id for g in groups], db)
    return [
        await _class_detail(g, db, members.get(g.id, 0), assigns.get(g.id, 0), threads.get(g.id, 0))
        for g in groups
    ]


# ── 成员管理 ──────────────────────────────────────────────────────────────────

@router.get("/classes/{class_id}/members", response_model=List[MemberOut])
async def list_members(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ClassMember).where(ClassMember.class_id == class_id).order_by(ClassMember.added_at)
    )
    return result.scalars().all()


@router.post("/classes/{class_id}/members", response_model=MemberOut)
async def add_member(class_id: int, data: MemberAdd, db: AsyncSession = Depends(get_db)):
    exists = (await db.execute(
        select(ClassMember).where(and_(ClassMember.class_id == class_id, ClassMember.student_id == data.student_id))
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(400, "该学生已在班级中")
    member = ClassMember(class_id=class_id, **data.model_dump())
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.get("/classes/{class_id}/members/{student_id}", response_model=MemberOut)
async def get_member(class_id: int, student_id: str, db: AsyncSession = Depends(get_db)):
    m = (await db.execute(
        select(ClassMember).where(and_(ClassMember.class_id == class_id, ClassMember.student_id == student_id))
    )).scalar_one_or_none()
    if not m:
        raise HTTPException(404, "成员不存在")
    return m


@router.delete("/classes/{class_id}/members/{student_id}")
async def remove_member(class_id: int, student_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ClassMember).where(and_(ClassMember.class_id == class_id, ClassMember.student_id == student_id))
    )
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(404, "成员不存在")
    await db.delete(m)
    await db.commit()
    return {"ok": True}


# ── 作业 ──────────────────────────────────────────────────────────────────────

@router.get("/classes/{class_id}/assignments", response_model=List[AssignmentWithStats])
async def list_assignments(class_id: int, db: AsyncSession = Depends(get_db)):
    assignments = (await db.execute(
        select(Assignment).where(Assignment.class_id == class_id).order_by(Assignment.created_at.desc())
    )).scalars().all()
    if not assignments:
        return []
    ids = [a.id for a in assignments]
    rows = (await db.execute(
        select(
            Submission.assignment_id,
            func.count().label("total"),
            func.count(case((Submission.score.isnot(None), 1))).label("graded"),
        )
        .where(Submission.assignment_id.in_(ids))
        .group_by(Submission.assignment_id)
    )).all()
    stats = {r.assignment_id: (r.total, r.graded) for r in rows}
    out = []
    for a in assignments:
        d = AssignmentWithStats.model_validate(a)
        d.submission_count, d.graded_count = stats.get(a.id, (0, 0))
        out.append(d)
    return out


@router.post("/classes/{class_id}/assignments", response_model=AssignmentOut)
async def create_assignment(class_id: int, data: AssignmentCreate, db: AsyncSession = Depends(get_db)):
    a = Assignment(class_id=class_id, **data.model_dump())
    db.add(a)
    await db.commit()
    await db.refresh(a)
    return a


@router.get("/assignments/{assignment_id}", response_model=AssignmentOut)
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise HTTPException(404, "作业不存在")
    return a


@router.patch("/assignments/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(assignment_id: int, data: AssignmentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise HTTPException(404, "作业不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    await db.commit()
    await db.refresh(a)
    return a


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    a = result.scalar_one_or_none()
    if not a:
        raise HTTPException(404, "作业不存在")
    await db.delete(a)
    await db.commit()
    return {"ok": True}


# ── 情绪打卡进度 ──────────────────────────────────────────────────────────────

async def _count_checkin(assignment: Assignment, student_id: str, db: AsyncSession) -> int:
    filters = [DiaryEntry.user_id == student_id]
    if assignment.start_date:
        filters.append(DiaryEntry.date >= assignment.start_date)
    if assignment.due_date:
        filters.append(DiaryEntry.date <= assignment.due_date)
    return (await db.execute(select(func.count()).where(and_(*filters)))).scalar() or 0


@router.get("/assignments/{assignment_id}/checkin-progress", response_model=CheckinProgress)
async def checkin_progress(
    assignment_id: int, student_id: str = Query(...), db: AsyncSession = Depends(get_db)
):
    a = (await db.execute(select(Assignment).where(Assignment.id == assignment_id))).scalar_one_or_none()
    if not a or a.type != "checkin":
        raise HTTPException(404, "作业不存在或类型不符")
    completed = await _count_checkin(a, student_id, db)
    return CheckinProgress(
        assignment_id=assignment_id,
        student_id=student_id,
        completed_days=completed,
        required_days=a.required_days or 0,
    )


@router.get("/assignments/{assignment_id}/checkin-stats", response_model=List[CheckinMemberStat])
async def checkin_stats(assignment_id: int, db: AsyncSession = Depends(get_db)):
    a = (await db.execute(select(Assignment).where(Assignment.id == assignment_id))).scalar_one_or_none()
    if not a or a.type != "checkin":
        raise HTTPException(404, "作业不存在或类型不符")
    members = (await db.execute(
        select(ClassMember).where(ClassMember.class_id == a.class_id)
    )).scalars().all()
    return [
        CheckinMemberStat(
            student_id=m.student_id,
            student_name=m.student_name,
            completed_days=await _count_checkin(a, m.student_id, db),
            required_days=a.required_days or 0,
        )
        for m in members
    ]


# ── AI对话进度 ────────────────────────────────────────────────────────────────

async def _count_chat(assignment: Assignment, student_id: str, db: AsyncSession) -> int:
    filters = [ChatRecord.user_id == student_id]
    if assignment.start_date:
        start_dt = datetime.strptime(assignment.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        filters.append(ChatRecord.sent_at >= start_dt)
    if assignment.due_date:
        due_dt = datetime.strptime(assignment.due_date, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, tzinfo=timezone.utc
        )
        filters.append(ChatRecord.sent_at <= due_dt)
    return (await db.execute(select(func.count()).where(and_(*filters)))).scalar() or 0


@router.get("/assignments/{assignment_id}/chat-progress", response_model=ChatProgress)
async def chat_progress(
    assignment_id: int, student_id: str = Query(...), db: AsyncSession = Depends(get_db)
):
    a = (await db.execute(select(Assignment).where(Assignment.id == assignment_id))).scalar_one_or_none()
    if not a or a.type != "chat":
        raise HTTPException(404, "作业不存在或类型不符")
    completed = await _count_chat(a, student_id, db)
    return ChatProgress(
        assignment_id=assignment_id,
        student_id=student_id,
        completed_rounds=completed,
        required_rounds=a.required_rounds or 0,
    )


@router.get("/assignments/{assignment_id}/chat-stats", response_model=List[ChatMemberStat])
async def chat_stats(assignment_id: int, db: AsyncSession = Depends(get_db)):
    a = (await db.execute(select(Assignment).where(Assignment.id == assignment_id))).scalar_one_or_none()
    if not a or a.type != "chat":
        raise HTTPException(404, "作业不存在或类型不符")
    members = (await db.execute(
        select(ClassMember).where(ClassMember.class_id == a.class_id)
    )).scalars().all()
    return [
        ChatMemberStat(
            student_id=m.student_id,
            student_name=m.student_name,
            completed_rounds=await _count_chat(a, m.student_id, db),
            required_rounds=a.required_rounds or 0,
        )
        for m in members
    ]


# ── 提交（qa / paper markdown）────────────────────────────────────────────────

@router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionOut])
async def list_submissions(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Submission).where(Submission.assignment_id == assignment_id)
        .order_by(Submission.submitted_at.desc())
    )
    return result.scalars().all()


@router.get("/assignments/{assignment_id}/my-submission", response_model=Optional[SubmissionOut])
async def my_submission(
    assignment_id: int, student_id: str = Query(...), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Submission).where(
            and_(Submission.assignment_id == assignment_id, Submission.student_id == student_id)
        )
    )
    return result.scalar_one_or_none()


@router.post("/assignments/{assignment_id}/submit", response_model=SubmissionOut)
async def submit_assignment(assignment_id: int, data: SubmissionCreate, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(
        select(Submission).where(
            and_(Submission.assignment_id == assignment_id, Submission.student_id == data.student_id)
        )
    )).scalar_one_or_none()
    if existing:
        existing.content      = data.content
        existing.answers_json = data.answers_json
        existing.submitted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing)
        return existing
    s = Submission(assignment_id=assignment_id, **data.model_dump())
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@router.post("/assignments/{assignment_id}/submit-file", response_model=SubmissionOut)
async def submit_file(
    assignment_id: int,
    student_id:   str       = Form(...),
    student_name: str       = Form(...),
    file:         UploadFile = File(...),
    db:           AsyncSession = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"不支持的文件格式 {ext}，允许：{', '.join(ALLOWED_EXTS)}")

    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOAD_DIR, safe_name)
    content_bytes = await file.read()
    with open(dest, "wb") as f_out:
        f_out.write(content_bytes)

    existing = (await db.execute(
        select(Submission).where(
            and_(Submission.assignment_id == assignment_id, Submission.student_id == student_id)
        )
    )).scalar_one_or_none()

    if existing:
        if existing.file_path:
            old = os.path.join(UPLOAD_DIR, os.path.basename(existing.file_path))
            if os.path.exists(old):
                os.remove(old)
        existing.file_path    = f"/uploads/{safe_name}"
        existing.file_name    = file.filename
        existing.submitted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing)
        return existing

    s = Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        student_name=student_name,
        file_path=f"/uploads/{safe_name}",
        file_name=file.filename,
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@router.patch("/submissions/{submission_id}", response_model=SubmissionOut)
async def grade_submission(submission_id: int, data: SubmissionGrade, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(404, "提交记录不存在")
    if data.score is not None:
        s.score = data.score
    if data.teacher_comment is not None:
        s.teacher_comment = data.teacher_comment
    s.graded_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(s)
    return s


# ── 全班讨论 ──────────────────────────────────────────────────────────────────

@router.get("/classes/{class_id}/threads", response_model=List[ThreadListItem])
async def list_threads(class_id: int, db: AsyncSession = Depends(get_db)):
    threads = (await db.execute(
        select(DiscussionThread).where(DiscussionThread.class_id == class_id)
        .order_by(DiscussionThread.pinned.desc(), DiscussionThread.created_at.desc())
    )).scalars().all()
    if not threads:
        return []
    ids = [t.id for t in threads]
    reply_counts = {
        r.thread_id: r.cnt
        for r in (await db.execute(
            select(DiscussionReply.thread_id, func.count().label("cnt"))
            .where(DiscussionReply.thread_id.in_(ids))
            .group_by(DiscussionReply.thread_id)
        )).all()
    }
    out = []
    for t in threads:
        item = ThreadListItem.model_validate(t)
        item.reply_count = reply_counts.get(t.id, 0)
        out.append(item)
    return out


@router.post("/classes/{class_id}/threads", response_model=ThreadOut)
async def create_thread(class_id: int, data: ThreadCreate, db: AsyncSession = Depends(get_db)):
    t = DiscussionThread(class_id=class_id, **data.model_dump())
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


@router.get("/threads/{thread_id}", response_model=ThreadWithReplies)
async def get_thread(thread_id: int, db: AsyncSession = Depends(get_db)):
    t = (await db.execute(select(DiscussionThread).where(DiscussionThread.id == thread_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "讨论不存在")
    replies = (await db.execute(
        select(DiscussionReply).where(DiscussionReply.thread_id == thread_id).order_by(DiscussionReply.created_at)
    )).scalars().all()
    out = ThreadWithReplies.model_validate(t)
    out.replies = list(replies)
    return out


@router.post("/threads/{thread_id}/replies", response_model=ReplyOut)
async def add_reply(thread_id: int, data: ReplyCreate, db: AsyncSession = Depends(get_db)):
    if not (await db.execute(select(DiscussionThread).where(DiscussionThread.id == thread_id))).scalar_one_or_none():
        raise HTTPException(404, "讨论不存在")
    r = DiscussionReply(thread_id=thread_id, **data.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: int, db: AsyncSession = Depends(get_db)):
    t = (await db.execute(select(DiscussionThread).where(DiscussionThread.id == thread_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "讨论不存在")
    await db.delete(t)
    await db.commit()
    return {"ok": True}


@router.delete("/replies/{reply_id}")
async def delete_reply(reply_id: int, db: AsyncSession = Depends(get_db)):
    r = (await db.execute(select(DiscussionReply).where(DiscussionReply.id == reply_id))).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "回复不存在")
    await db.delete(r)
    await db.commit()
    return {"ok": True}


@router.patch("/threads/{thread_id}/pin", response_model=ThreadOut)
async def pin_thread(thread_id: int, db: AsyncSession = Depends(get_db)):
    t = (await db.execute(select(DiscussionThread).where(DiscussionThread.id == thread_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "讨论不存在")
    t.pinned = not t.pinned
    await db.commit()
    await db.refresh(t)
    return t


# ── 小组讨论 ──────────────────────────────────────────────────────────────────

@router.get("/classes/{class_id}/groups", response_model=List[CourseGroupOut])
async def list_groups(class_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CourseGroup).where(CourseGroup.class_id == class_id).order_by(CourseGroup.created_at)
    )
    return result.scalars().all()


@router.post("/classes/{class_id}/groups", response_model=CourseGroupOut)
async def create_group(class_id: int, data: CourseGroupCreate, db: AsyncSession = Depends(get_db)):
    g = CourseGroup(class_id=class_id, **data.model_dump())
    db.add(g)
    await db.commit()
    await db.refresh(g)
    return g


@router.patch("/groups/{group_id}", response_model=CourseGroupOut)
async def update_group(group_id: int, data: CourseGroupCreate, db: AsyncSession = Depends(get_db)):
    g = (await db.execute(select(CourseGroup).where(CourseGroup.id == group_id))).scalar_one_or_none()
    if not g:
        raise HTTPException(404, "小组不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(g, k, v)
    await db.commit()
    await db.refresh(g)
    return g


@router.delete("/groups/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    g = (await db.execute(select(CourseGroup).where(CourseGroup.id == group_id))).scalar_one_or_none()
    if not g:
        raise HTTPException(404, "小组不存在")
    await db.delete(g)
    await db.commit()
    return {"ok": True}


@router.get("/my-group", response_model=Optional[CourseGroupOut])
async def my_group(class_id: int = Query(...), student_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CourseGroup).where(CourseGroup.class_id == class_id))
    for g in result.scalars().all():
        if student_id in (g.member_ids or []):
            return g
    return None


@router.get("/groups/{group_id}", response_model=CourseGroupOut)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    g = (await db.execute(select(CourseGroup).where(CourseGroup.id == group_id))).scalar_one_or_none()
    if not g:
        raise HTTPException(404, "小组不存在")
    return g


@router.get("/groups/{group_id}/messages", response_model=List[GroupMessageOut])
async def get_messages(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(GroupMessage).where(GroupMessage.group_id == group_id).order_by(GroupMessage.created_at)
    )
    return result.scalars().all()


@router.post("/groups/{group_id}/messages", response_model=GroupMessageOut)
async def send_message(group_id: int, data: GroupMessageCreate, db: AsyncSession = Depends(get_db)):
    if not (await db.execute(select(CourseGroup).where(CourseGroup.id == group_id))).scalar_one_or_none():
        raise HTTPException(404, "小组不存在")
    msg = GroupMessage(group_id=group_id, **data.model_dump())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.delete("/groups/{group_id}/messages/{message_id}")
async def delete_message(group_id: int, message_id: int, db: AsyncSession = Depends(get_db)):
    m = (await db.execute(
        select(GroupMessage).where(GroupMessage.id == message_id, GroupMessage.group_id == group_id)
    )).scalar_one_or_none()
    if not m:
        raise HTTPException(404, "消息不存在")
    await db.delete(m)
    await db.commit()
    return {"ok": True}


# ── 小组结论 ──────────────────────────────────────────────────────────────────

@router.get("/groups/{group_id}/conclusion", response_model=Optional[GroupConclusionOut])
async def get_conclusion(group_id: int, db: AsyncSession = Depends(get_db)):
    return (await db.execute(
        select(GroupConclusion).where(GroupConclusion.group_id == group_id)
    )).scalar_one_or_none()


@router.put("/groups/{group_id}/conclusion", response_model=GroupConclusionOut)
async def set_conclusion(group_id: int, data: GroupConclusionUpdate, db: AsyncSession = Depends(get_db)):
    if not (await db.execute(select(CourseGroup).where(CourseGroup.id == group_id))).scalar_one_or_none():
        raise HTTPException(404, "小组不存在")
    c = (await db.execute(
        select(GroupConclusion).where(GroupConclusion.group_id == group_id)
    )).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if c:
        c.content         = data.content
        c.updated_by_id   = data.updated_by_id
        c.updated_by_name = data.updated_by_name
        c.updated_at      = now
    else:
        c = GroupConclusion(group_id=group_id, updated_at=now, **data.model_dump())
        db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@router.get("/classes/{class_id}/groups/overview", response_model=List[CourseGroupSummary])
async def groups_overview(class_id: int, db: AsyncSession = Depends(get_db)):
    groups = (await db.execute(
        select(CourseGroup).where(CourseGroup.class_id == class_id).order_by(CourseGroup.created_at)
    )).scalars().all()
    if not groups:
        return []
    group_ids = [g.id for g in groups]

    msg_counts = {
        r.group_id: r.cnt
        for r in (await db.execute(
            select(GroupMessage.group_id, func.count().label("cnt"))
            .where(GroupMessage.group_id.in_(group_ids))
            .group_by(GroupMessage.group_id)
        )).all()
    }
    conclusions = {
        c.group_id: c
        for c in (await db.execute(
            select(GroupConclusion).where(GroupConclusion.group_id.in_(group_ids))
        )).scalars().all()
    }

    out = []
    for g in groups:
        item = CourseGroupSummary.model_validate(g)
        item.message_count = msg_counts.get(g.id, 0)
        item.conclusion    = conclusions.get(g.id)
        out.append(item)
    return out
