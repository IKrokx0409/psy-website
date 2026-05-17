<template>
  <div class="ad-page">

    <div class="ad-header">
      <div class="ad-header-inner">
        <router-link :to="`/course/${classId}`" class="ad-back">
          <ChevronLeft :size="16" :stroke-width="2" /> 返回班级
        </router-link>
        <h1 v-if="assignment" class="ad-title">{{ assignment.title }}</h1>
      </div>
    </div>

    <div v-if="loading" class="ad-state"><Loader2 :size="28" class="spin" /><span>加载中…</span></div>
    <div v-else-if="error" class="ad-state ad-state-err"><AlertCircle :size="18" /><span>{{ error }}</span></div>

    <div v-else class="ad-body">

      <!-- 作业信息 -->
      <div class="ad-info-card">
        <div class="ad-info-row">
          <span class="ad-info-label">类型</span>
          <span class="type-badge">{{ TYPE_LABEL[assignment.type] }}</span>
        </div>
        <div v-if="assignment.due_date" class="ad-info-row">
          <span class="ad-info-label">截止日期</span>
          <span :class="['due-badge', isOverdue(assignment.due_date) ? 'due-overdue' : 'due-ok']">
            <CalendarDays :size="13" /> {{ assignment.due_date }}
            <span v-if="isOverdue(assignment.due_date)">（已截止）</span>
          </span>
        </div>
        <div v-if="assignment.description" class="ad-desc" v-html="renderMd(assignment.description)" />
      </div>

      <!-- ══ 情绪打卡 ══════════════════════════════════════════════════════════ -->
      <template v-if="assignment.type === 'checkin'">
        <!-- 教师视图：全班统计 -->
        <template v-if="isTeacher">
          <div class="section-title">
            全班打卡统计
            <span class="section-badge">{{ checkinStats.length }} 人</span>
          </div>
          <div v-if="checkinStats.length === 0" class="ad-state" style="padding:40px 0">
            <Users :size="36" :stroke-width="1" style="opacity:.25" /><span>班级暂无成员</span>
          </div>
          <div v-for="s in checkinStats" :key="s.student_id" class="stat-card">
            <div class="stat-head">
              <span class="stat-name"><User :size="13" /> {{ s.student_name }}</span>
              <span :class="['stat-badge', s.completed_days >= s.required_days ? 'badge-done' : 'badge-pending']">
                {{ s.completed_days >= s.required_days ? '已达标' : '未达标' }}
              </span>
            </div>
            <div class="prog-wrap">
              <div class="prog-bar">
                <div class="prog-fill" :style="{ width: pct(s.completed_days, s.required_days) + '%' }"></div>
              </div>
              <span class="prog-label">{{ s.completed_days }} / {{ s.required_days }} 天</span>
            </div>
          </div>
        </template>
        <!-- 学生视图：我的进度 -->
        <template v-else>
          <div class="section-title">我的打卡进度</div>
          <div class="progress-card">
            <div class="prog-nums">
              <span class="prog-big">{{ checkinProgress.completed_days }}</span>
              <span class="prog-sep">/</span>
              <span class="prog-total">{{ checkinProgress.required_days }} 天</span>
            </div>
            <div class="prog-bar prog-bar-lg">
              <div class="prog-fill" :style="{ width: pct(checkinProgress.completed_days, checkinProgress.required_days) + '%' }"></div>
            </div>
            <div v-if="checkinProgress.completed_days >= checkinProgress.required_days" class="done-tip">
              <CheckCircle2 :size="15" /> 已达到要求天数，作业自动完成！
            </div>
            <div v-else class="hint-tip">
              <BookOpen :size="14" /> 前往<router-link to="/diary" class="hint-link">情绪日记</router-link>记录今日心情，即可累计天数
            </div>
          </div>
        </template>
      </template>

      <!-- ══ AI对话 ═══════════════════════════════════════════════════════════ -->
      <template v-else-if="assignment.type === 'chat'">
        <!-- 教师视图：全班统计 -->
        <template v-if="isTeacher">
          <div class="section-title">
            全班对话统计
            <span class="section-badge">{{ chatStats.length }} 人</span>
          </div>
          <div v-if="chatStats.length === 0" class="ad-state" style="padding:40px 0">
            <Users :size="36" :stroke-width="1" style="opacity:.25" /><span>班级暂无成员</span>
          </div>
          <div v-for="s in chatStats" :key="s.student_id" class="stat-card">
            <div class="stat-head">
              <span class="stat-name"><User :size="13" /> {{ s.student_name }}</span>
              <span :class="['stat-badge', s.completed_rounds >= s.required_rounds ? 'badge-done' : 'badge-pending']">
                {{ s.completed_rounds >= s.required_rounds ? '已达标' : '未达标' }}
              </span>
            </div>
            <div class="prog-wrap">
              <div class="prog-bar">
                <div class="prog-fill prog-fill-chat" :style="{ width: pct(s.completed_rounds, s.required_rounds) + '%' }"></div>
              </div>
              <span class="prog-label">{{ s.completed_rounds }} / {{ s.required_rounds }} 轮</span>
            </div>
          </div>
        </template>
        <!-- 学生视图：我的进度 -->
        <template v-else>
          <div class="section-title">我的对话进度</div>
          <div class="progress-card">
            <div class="prog-nums">
              <span class="prog-big">{{ chatProgress.completed_rounds }}</span>
              <span class="prog-sep">/</span>
              <span class="prog-total">{{ chatProgress.required_rounds }} 轮</span>
            </div>
            <div class="prog-bar prog-bar-lg">
              <div class="prog-fill prog-fill-chat" :style="{ width: pct(chatProgress.completed_rounds, chatProgress.required_rounds) + '%' }"></div>
            </div>
            <div v-if="chatProgress.completed_rounds >= chatProgress.required_rounds" class="done-tip">
              <CheckCircle2 :size="15" /> 对话轮数已达标，作业自动完成！
            </div>
            <div v-else class="hint-tip">
              <MessageCircle :size="14" /> 前往<router-link to="/chat" class="hint-link">AI对话</router-link>与心理智能体交流，即可累计轮数
            </div>
          </div>
        </template>
      </template>

      <!-- ══ 教师视图（qa/paper）：提交列表 ════════════════════════════════════ -->
      <template v-else-if="isTeacher">
        <div class="section-title">
          提交情况
          <span class="section-badge">{{ submissions.length }} 份</span>
        </div>

        <div v-if="submissions.length === 0" class="ad-state" style="padding:40px 0">
          <FileText :size="36" :stroke-width="1" style="opacity:.25" /><span>暂无提交</span>
        </div>

        <div v-for="s in submissions" :key="s.id" class="submission-card">
          <div class="sub-head">
            <div class="sub-student">
              <User :size="14" /> {{ s.student_name }}
              <span class="sub-time">{{ fmtDate(s.submitted_at) }}</span>
            </div>
            <div class="sub-grade-info">
              <span v-if="s.score !== null" class="score-badge">{{ s.score }} 分</span>
              <span v-else class="score-pending">未批改</span>
              <button class="btn-grade" @click="openGrade(s)">
                <Edit3 :size="13" /> {{ s.score !== null ? '修改' : '批改' }}
              </button>
            </div>
          </div>
          <div class="sub-content" v-if="s.content">{{ s.content }}</div>
          <div v-if="s.teacher_comment" class="sub-comment">
            <MessageCircle :size="13" /> {{ s.teacher_comment }}
          </div>
        </div>
      </template>

      <!-- ══ 学生视图（qa/paper）：提交/查看 ═══════════════════════════════════ -->
      <template v-else>
        <template v-if="mySubmission">
          <div class="section-title">我的提交</div>
          <div class="my-submission-card">
            <div class="sub-time-row">
              <span>提交于 {{ fmtDate(mySubmission.submitted_at) }}</span>
              <span v-if="mySubmission.score !== null" class="score-badge-lg">{{ mySubmission.score }} 分</span>
              <span v-else class="score-pending">等待批改</span>
            </div>
            <div class="sub-content my-content">{{ mySubmission.content }}</div>
            <div v-if="mySubmission.teacher_comment" class="my-comment">
              <div class="my-comment-label"><MessageCircle :size="13" /> 教师评语</div>
              <div class="my-comment-text">{{ mySubmission.teacher_comment }}</div>
            </div>
            <button class="btn-resubmit" @click="editMode = true">重新提交</button>
          </div>
        </template>

        <template v-if="!mySubmission || editMode">
          <div class="section-title">{{ mySubmission ? '重新提交' : '提交作业' }}</div>
          <div class="submit-form">
            <textarea
              v-model="submitContent"
              class="submit-textarea"
              rows="8"
              placeholder="在此输入你的作业内容…"
            />
            <div class="submit-actions">
              <button v-if="editMode" class="btn-cancel" @click="editMode = false">取消</button>
              <button class="btn-primary" :disabled="submitting || !submitContent.trim()" @click="doSubmit">
                {{ submitting ? '提交中…' : '提交' }}
              </button>
            </div>
          </div>
        </template>
      </template>

    </div>

    <!-- 批改弹窗 -->
    <Transition name="modal">
      <div v-if="gradeFormVisible" class="modal-overlay" @click.self="gradeFormVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>批改 — {{ gradingSubmission?.student_name }}</span>
            <button class="modal-close" @click="gradeFormVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>分数（0–100）</label>
              <input v-model.number="gradeForm.score" type="number" min="0" max="100" class="form-input" placeholder="留空则不评分" />
            </div>
            <div class="form-group">
              <label>评语 <span class="optional">（选填）</span></label>
              <textarea v-model="gradeForm.comment" class="form-textarea" rows="3" placeholder="给学生的反馈…" />
            </div>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="gradeFormVisible = false">取消</button>
            <button class="btn-primary" :disabled="grading" @click="doGrade">
              {{ grading ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  ChevronLeft, CalendarDays, FileText, User, Users, Edit3, MessageCircle,
  Loader2, AlertCircle, X, CheckCircle2, BookOpen,
} from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'
import { useAuth } from '@/composables/useAuth'
import { useUserId } from '@/composables/useUserId'
import {
  getAssignment, getSubmissions, getMySubmission,
  submitAssignment, gradeSubmission,
  getCheckinProgress, getCheckinStats,
  getChatProgress, getChatStats,
} from '@/api/courses'

const route      = useRoute()
const classId    = Number(route.params.classId)
const assignId   = Number(route.params.assignmentId)
const { isTeacher } = useAuth()
const userId     = useUserId()
const md         = new MarkdownIt({ html: false, linkify: true, typographer: true })
const renderMd   = (s) => md.render(s || '')

const TYPE_LABEL = { checkin: '情绪打卡', qa: '课堂问答', paper: '综合作业', chat: 'AI情绪对话' }

const loading    = ref(true)
const error      = ref('')
const assignment = ref(null)

// qa/paper 用
const submissions  = ref([])
const mySubmission = ref(null)
const submitContent = ref('')
const submitting    = ref(false)
const editMode      = ref(false)

// checkin 用
const checkinProgress = ref({ completed_days: 0, required_days: 0 })
const checkinStats    = ref([])

// chat 用
const chatProgress = ref({ completed_rounds: 0, required_rounds: 0 })
const chatStats    = ref([])

const pct = (done, total) => total > 0 ? Math.min(100, Math.round(done / total * 100)) : 0

onMounted(async () => {
  try {
    assignment.value = await getAssignment(assignId)
    const type = assignment.value.type

    if (type === 'checkin') {
      if (isTeacher.value) {
        checkinStats.value = await getCheckinStats(assignId)
      } else {
        checkinProgress.value = await getCheckinProgress(assignId, userId)
      }
    } else if (type === 'chat') {
      if (isTeacher.value) {
        chatStats.value = await getChatStats(assignId)
      } else {
        chatProgress.value = await getChatProgress(assignId, userId)
      }
    } else {
      if (isTeacher.value) {
        submissions.value = await getSubmissions(assignId)
      } else {
        mySubmission.value = await getMySubmission(assignId, userId)
      }
    }
  } catch {
    error.value = '加载失败，请检查后端服务'
  } finally {
    loading.value = false
  }
})

const fmtDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const isOverdue = (dateStr) => dateStr && new Date(dateStr) < new Date()

const doSubmit = async () => {
  if (!submitContent.value.trim()) return
  submitting.value = true
  try {
    const result = await submitAssignment(assignId, {
      student_id:   userId,
      student_name: '我',
      content:      submitContent.value.trim(),
    })
    mySubmission.value = result
    editMode.value = false
    submitContent.value = ''
  } finally { submitting.value = false }
}

// ── 批改 ──────────────────────────────────────────────────────────────────────
const gradeFormVisible   = ref(false)
const gradingSubmission  = ref(null)
const gradeForm = reactive({ score: null, comment: '' })
const grading   = ref(false)

const openGrade = (s) => {
  gradingSubmission.value = s
  gradeForm.score   = s.score ?? null
  gradeForm.comment = s.teacher_comment || ''
  gradeFormVisible.value = true
}

const doGrade = async () => {
  grading.value = true
  try {
    const updated = await gradeSubmission(gradingSubmission.value.id, {
      score:           gradeForm.score,
      teacher_comment: gradeForm.comment || null,
    })
    Object.assign(gradingSubmission.value, updated)
    gradeFormVisible.value = false
  } finally { grading.value = false }
}
</script>

<style scoped>
.ad-page { background: #f6f2ec; min-height: 100vh; }
.ad-header { background: linear-gradient(160deg, #2d5a42 0%, #4a8763 100%); padding: 16px 0; color: white; }
.ad-header-inner { max-width: 860px; margin: 0 auto; padding: 0 24px; }
.ad-back { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; color: rgba(255,255,255,0.75); text-decoration: none; margin-bottom: 8px; }
.ad-back:hover { color: white; }
.ad-title { font-size: 22px; font-weight: 700; color: white; margin: 0; font-family: var(--f-serif, serif); letter-spacing: 1px; }

.ad-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 0; color: #94a3b8; font-size: 14px; }
.ad-state-err { color: #b84545; }

.ad-body { max-width: 860px; margin: 0 auto; padding: 24px; }

.ad-info-card { background: white; border: 1px solid var(--c-beige-border); border-radius: var(--r-lg); padding: 20px; margin-bottom: 24px; box-shadow: var(--shadow-xs); }
.ad-info-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.ad-info-label { font-size: 12.5px; font-weight: 600; color: #7a9080; width: 72px; flex-shrink: 0; }
.type-badge { font-size: 12.5px; background: #f0ebe2; color: #7a9080; padding: 2px 10px; border-radius: var(--r-pill); }
.due-badge { display: inline-flex; align-items: center; gap: 5px; font-size: 13px; padding: 2px 10px; border-radius: var(--r-pill); }
.due-ok { background: #e8f5ef; color: #3d6e52; }
.due-overdue { background: #fdf2f2; color: #b84545; }
.ad-desc { margin-top: 14px; padding-top: 14px; border-top: 1px solid #f0ebe2; font-size: 14px; line-height: 1.75; color: #374151; }
.ad-desc :deep(p) { margin: 0 0 10px; }
.ad-desc :deep(ul), .ad-desc :deep(ol) { padding-left: 20px; margin: 0 0 10px; }

.section-title { font-size: 14px; font-weight: 700; color: #3d6e52; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; text-transform: uppercase; letter-spacing: 0.06em; }
.section-badge { background: #e8f5ef; color: #3d6e52; font-size: 12px; padding: 1px 8px; border-radius: var(--r-pill); font-weight: 600; }

/* ── 进度条（通用）── */
.prog-wrap { display: flex; align-items: center; gap: 10px; }
.prog-bar { flex: 1; height: 6px; background: #e8e0d4; border-radius: 3px; overflow: hidden; }
.prog-fill { height: 100%; background: #4a8763; border-radius: 3px; transition: width 0.4s ease; }
.prog-fill-chat { background: #5a7ec4; }
.prog-label { font-size: 12.5px; color: #7a9080; white-space: nowrap; min-width: 64px; text-align: right; }

/* ── 统计卡片（教师视图）── */
.stat-card { background: white; border: 1px solid var(--c-beige-border); border-radius: var(--r-lg); padding: 14px 16px; margin-bottom: 8px; box-shadow: var(--shadow-xs); }
.stat-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.stat-name { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: #1c2b22; }
.stat-badge { font-size: 11.5px; font-weight: 600; padding: 2px 10px; border-radius: var(--r-pill); }
.badge-done { background: #e8f5ef; color: #3d6e52; }
.badge-pending { background: #f5f0e8; color: #7a9080; }

/* ── 学生进度卡片── */
.progress-card { background: white; border: 1px solid var(--c-beige-border); border-radius: var(--r-lg); padding: 24px; box-shadow: var(--shadow-xs); }
.prog-nums { display: flex; align-items: baseline; gap: 6px; margin-bottom: 16px; }
.prog-big { font-size: 48px; font-weight: 700; color: #3d6e52; font-family: var(--f-serif, serif); line-height: 1; }
.prog-sep { font-size: 24px; color: #c4bbb0; }
.prog-total { font-size: 20px; color: #7a9080; }
.prog-bar-lg { height: 10px; border-radius: 5px; margin-bottom: 16px; }
.done-tip { display: flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 600; color: #3d6e52; background: #e8f5ef; padding: 10px 14px; border-radius: var(--r-sm); }
.hint-tip { display: flex; align-items: center; gap: 7px; font-size: 13.5px; color: #7a9080; background: #f5f0e8; padding: 10px 14px; border-radius: var(--r-sm); }
.hint-link { color: #4a8763; font-weight: 600; text-decoration: underline; }

/* ── 提交卡片（教师视图）── */
.submission-card { background: white; border: 1px solid var(--c-beige-border); border-radius: var(--r-lg); margin-bottom: 10px; overflow: hidden; box-shadow: var(--shadow-xs); }
.sub-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #f0ebe2; }
.sub-student { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: #1c2b22; }
.sub-time { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 8px; }
.sub-grade-info { display: flex; align-items: center; gap: 10px; }
.score-badge { font-size: 13px; font-weight: 700; color: #3d6e52; background: #e8f5ef; padding: 2px 10px; border-radius: var(--r-pill); }
.score-pending { font-size: 12.5px; color: #94a3b8; }
.btn-grade { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; background: #3d6e52; color: white; border: none; border-radius: var(--r-xs); font-size: 12.5px; cursor: pointer; transition: background var(--t-base); }
.btn-grade:hover { background: #2d5a42; }
.sub-content { padding: 12px 16px; font-size: 13.5px; color: #374151; line-height: 1.7; white-space: pre-wrap; }
.sub-comment { padding: 8px 16px 12px; font-size: 12.5px; color: #7a9080; display: flex; align-items: center; gap: 6px; border-top: 1px solid #f0ebe2; }

/* ── 学生视图 ── */
.my-submission-card { background: white; border: 1px solid var(--c-beige-border); border-radius: var(--r-lg); padding: 16px; margin-bottom: 20px; box-shadow: var(--shadow-xs); }
.sub-time-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; font-size: 13px; color: #7a9080; }
.score-badge-lg { font-size: 16px; font-weight: 700; color: #3d6e52; background: #e8f5ef; padding: 3px 14px; border-radius: var(--r-pill); }
.my-content { font-size: 14px; line-height: 1.75; color: #374151; white-space: pre-wrap; margin-bottom: 14px; }
.my-comment { background: #f5fbf7; border: 1px solid #d4e8db; border-radius: var(--r-sm); padding: 12px 14px; }
.my-comment-label { font-size: 12.5px; font-weight: 600; color: #3d6e52; display: flex; align-items: center; gap: 5px; margin-bottom: 6px; }
.my-comment-text { font-size: 13.5px; color: #374151; line-height: 1.6; }
.btn-resubmit { margin-top: 14px; padding: 7px 16px; background: none; border: 1.5px solid #d4e8db; border-radius: var(--r-sm); color: #3d6e52; font-size: 13px; cursor: pointer; transition: background var(--t-base); }
.btn-resubmit:hover { background: #f0fbf4; }

.submit-form { background: white; border: 1px solid var(--c-beige-border); border-radius: var(--r-lg); padding: 16px; box-shadow: var(--shadow-xs); }
.submit-textarea { width: 100%; border: 1px solid #ddd6cc; border-radius: 4px; padding: 10px 12px; font-size: 14px; line-height: 1.75; color: #1c2b22; background: #fdfaf5; font-family: inherit; resize: vertical; outline: none; box-sizing: border-box; min-height: 160px; }
.submit-textarea:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.1); }
.submit-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px; }

/* ── 通用 ── */
.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 8px 18px; background: var(--c-green-deep); color: white; border: none; border-radius: var(--r-sm); font-size: 13.5px; font-weight: 600; cursor: pointer; transition: background var(--t-base); }
.btn-primary:hover:not(:disabled) { background: #2d5a42; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancel { padding: 8px 18px; border: 1.5px solid #d4e8db; border-radius: var(--r-sm); background: white; color: #3d6e52; font-size: 13.5px; cursor: pointer; transition: background var(--t-base); }
.btn-cancel:hover { background: #f0fbf4; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 24px; }
.modal { background: white; border-radius: var(--r-xl); width: 100%; max-width: 460px; box-shadow: var(--shadow-xl); }
.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #e8e0d4; font-size: 15px; font-weight: 600; color: #1c2b22; }
.modal-close { background: none; border: none; cursor: pointer; color: #94a3b8; display: flex; }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.modal-foot { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 20px; border-top: 1px solid #e8e0d4; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 12.5px; font-weight: 600; color: #4a8763; letter-spacing: 0.04em; text-transform: uppercase; }
.optional { font-weight: 400; color: #94a3b8; text-transform: none; }
.form-input, .form-textarea { border: 1px solid #ddd6cc; border-radius: var(--r-sm); padding: 8px 10px; font-size: 13.5px; color: #1c2b22; background: var(--c-beige-card); font-family: inherit; outline: none; width: 100%; box-sizing: border-box; }
.form-input:focus, .form-textarea:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.12); }
.form-textarea { resize: vertical; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: translateY(12px); }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
