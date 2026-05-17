<template>
  <div class="cp-wrap">

    <!-- 侧边栏 -->
    <aside class="cp-sidebar">
      <router-link to="/course" class="cp-back">
        <ChevronLeft :size="15" /> 返回
      </router-link>
      <div v-if="classInfo" class="cp-course-name">{{ classInfo.name }}</div>

      <nav class="cp-nav">
        <button
          v-for="t in TABS" :key="t.key"
          :class="['cp-nav-item', { active: activeTab === t.key }]"
          @click="activeTab = t.key"
        >
          <component :is="t.icon" :size="16" :stroke-width="1.5" />
          <span>{{ t.label }}</span>
          <span v-if="t.badge" class="nav-badge">{{ t.badge }}</span>
        </button>
      </nav>

      <!-- 教师：成员管理入口 -->
      <div v-if="isTeacher" class="cp-sidebar-footer">
        <button class="sidebar-manage-btn" @click="activeTab = 'members'">
          <Users :size="14" /> 成员管理
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="cp-main">
      <div v-if="loading" class="cp-state"><Loader2 :size="28" class="spin" /><span>加载中…</span></div>
      <div v-else-if="error" class="cp-state cp-state-err"><AlertCircle :size="18" /><span>{{ error }}</span></div>

      <template v-else>

        <!-- ══ 作业 ══════════════════════════════════════════════════════════ -->
        <div v-show="activeTab === 'assignments'" class="cp-panel">
          <div class="panel-header">
            <span class="panel-title">作业</span>
            <button v-if="isTeacher" class="btn-primary btn-sm" @click="openAssignForm()">
              <Plus :size="13" /> 发布作业
            </button>
          </div>

          <div v-if="assignments.length === 0" class="cp-empty">
            <FileText :size="36" :stroke-width="1" /><span>暂无作业</span>
          </div>

          <div
            v-for="a in assignments" :key="a.id"
            class="assign-row"
            @click="goAssignment(a)"
          >
            <div class="assign-type-dot" :class="`type-${a.type}`"></div>
            <div class="assign-body">
              <div class="assign-title">{{ a.title }}</div>
              <div class="assign-meta">
                <span class="type-chip type-chip--{{ a.type }}">{{ TYPE_LABEL[a.type] }}</span>
                <span v-if="a.due_date" :class="['due-chip', isOverdue(a.due_date) ? 'due-over' : 'due-ok']">
                  <CalendarDays :size="11" /> {{ a.due_date }}
                </span>
              </div>
            </div>
            <div v-if="isTeacher" class="assign-stats">
              <span>{{ a.submission_count }} 提交</span>
              <span>{{ a.graded_count }} 已评</span>
            </div>
            <div v-else-if="a.type === 'checkin' && checkinMap[a.id]" class="checkin-progress-mini">
              <div class="cp-bar-wrap">
                <div class="cp-bar-fill" :style="{ width: checkinPct(a.id) + '%' }"></div>
              </div>
              <span>{{ checkinMap[a.id].completed_days }}/{{ checkinMap[a.id].required_days }}天</span>
            </div>
            <div v-else-if="a.type === 'chat' && chatMap[a.id]" class="checkin-progress-mini">
              <div class="cp-bar-wrap">
                <div class="cp-bar-fill cp-bar-fill-chat" :style="{ width: chatPct(a.id) + '%' }"></div>
              </div>
              <span>{{ chatMap[a.id].completed_rounds }}/{{ chatMap[a.id].required_rounds }}轮</span>
            </div>
            <div v-if="isTeacher" class="assign-del" @click.stop="doDeleteAssignment(a)">
              <Trash2 :size="13" />
            </div>
          </div>
        </div>

        <!-- ══ 全班讨论 ════════════════════════════════════════════════════ -->
        <div v-show="activeTab === 'discuss'" class="cp-panel discuss-panel">
          <div class="panel-header">
            <span class="panel-title">全班讨论</span>
            <button v-if="isTeacher" class="btn-primary btn-sm" @click="threadFormVisible = true">
              <Plus :size="13" /> 发起话题
            </button>
          </div>

          <div v-if="threads.length === 0" class="cp-empty">
            <MessageSquare :size="36" :stroke-width="1" /><span>暂无讨论，发起第一个话题</span>
          </div>

          <div
            v-for="t in threads" :key="t.id"
            class="thread-row"
            @click="goThread(t)"
          >
            <div class="thread-row-left">
              <span v-if="t.pinned" class="pin-chip"><Pin :size="10" /> 置顶</span>
              <div class="thread-row-title">{{ t.title }}</div>
              <div class="thread-row-meta">{{ t.author_name }} · {{ fmtDate(t.created_at) }}</div>
            </div>
            <div class="thread-row-right">
              <span class="reply-count"><MessageSquare :size="12" /> {{ t.reply_count }}</span>
              <div v-if="isTeacher" class="thread-actions" @click.stop>
                <button class="icon-btn" @click="doPin(t)"><Pin :size="13" :class="t.pinned ? 'pinned' : ''" /></button>
                <button class="icon-btn icon-btn-danger" @click="doDeleteThread(t)"><Trash2 :size="13" /></button>
              </div>
            </div>
          </div>
        </div>

        <!-- ══ 小组讨论 ════════════════════════════════════════════════════ -->
        <div v-show="activeTab === 'groups'" class="cp-panel">
          <div class="panel-header">
            <span class="panel-title">小组讨论</span>
            <button v-if="isTeacher" class="btn-primary btn-sm" @click="randomGroupVisible = true">
              <Shuffle :size="13" /> 随机分组
            </button>
          </div>

          <!-- 教师：所有小组列表 -->
          <template v-if="isTeacher">
            <div v-if="groups.length === 0" class="cp-empty">
              <Users :size="36" :stroke-width="1" /><span>暂无小组</span>
            </div>
            <div
              v-for="g in groups" :key="g.id"
              class="group-card"
              @click="goGroup(g)"
            >
              <div class="group-card-left">
                <div class="group-name">{{ g.name }}</div>
                <div class="group-meta">{{ g.member_ids.length }} 名成员</div>
              </div>
              <div class="group-card-actions" @click.stop>
                <button class="icon-btn" @click="openGroupForm(g)"><Edit3 :size="13" /></button>
                <button class="icon-btn icon-btn-danger" @click="doDeleteGroup(g)"><Trash2 :size="13" /></button>
              </div>
              <ChevronRight :size="15" class="group-chevron" />
            </div>
          </template>

          <!-- 学生：我的小组 -->
          <template v-else>
            <div v-if="!myGroup" class="cp-empty">
              <Users :size="36" :stroke-width="1" /><span>你还没有被分配到任何小组</span>
            </div>
            <div v-else class="my-group-card" @click="goGroup(myGroup)">
              <div class="my-group-icon"><Users :size="28" :stroke-width="1.5" /></div>
              <div>
                <div class="group-name">{{ myGroup.name }}</div>
                <div class="group-meta">{{ myGroup.member_ids.length }} 名成员 · 点击进入讨论</div>
              </div>
              <ChevronRight :size="18" class="group-chevron" />
            </div>
          </template>
        </div>

        <!-- ══ 成员管理（仅教师）════════════════════════════════════════════ -->
        <div v-show="activeTab === 'members' && isTeacher" class="cp-panel">
          <div class="panel-header">
            <span class="panel-title">成员管理</span>
            <button class="btn-primary btn-sm" @click="memberFormVisible = true">
              <UserPlus :size="13" /> 添加成员
            </button>
          </div>
          <div v-if="members.length === 0" class="cp-empty">
            <Users :size="36" :stroke-width="1" /><span>暂无成员</span>
          </div>
          <table v-else class="member-table">
            <thead><tr><th>姓名</th><th>学生 ID</th><th>加入时间</th><th></th></tr></thead>
            <tbody>
              <tr v-for="m in members" :key="m.id">
                <td>{{ m.student_name }}</td>
                <td><code>{{ m.student_id }}</code></td>
                <td>{{ fmtDate(m.added_at) }}</td>
                <td><button class="icon-btn icon-btn-danger" @click="doRemoveMember(m)"><Trash2 :size="13" /></button></td>
              </tr>
            </tbody>
          </table>
        </div>

      </template>
    </main>

    <!-- ── 弹窗集合 ─────────────────────────────────────────────────────────── -->

    <!-- 发布作业弹窗 -->
    <Transition name="modal">
      <div v-if="assignFormVisible" class="modal-overlay" @click.self="assignFormVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>发布作业</span>
            <button class="modal-close" @click="assignFormVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>作业类型</label>
              <div class="type-selector">
                <button
                  v-for="t in ASSIGN_TYPES" :key="t.value"
                  :class="['type-opt', { active: assignForm.type === t.value }]"
                  @click="assignForm.type = t.value"
                >
                  <component :is="t.icon" :size="16" :stroke-width="1.5" />
                  <span class="type-opt-name">{{ t.label }}</span>
                  <span class="type-opt-desc">{{ t.desc }}</span>
                </button>
              </div>
            </div>
            <div class="form-group">
              <label>标题</label>
              <input v-model="assignForm.title" class="form-input" placeholder="作业标题…" maxlength="200" />
            </div>
            <div class="form-group">
              <label>说明 <span class="opt">（Markdown，选填）</span></label>
              <textarea v-model="assignForm.description" class="form-textarea" rows="3" />
            </div>
            <template v-if="assignForm.type === 'checkin'">
              <div class="form-group">
                <label>统计起始日期 <span class="opt">（选填，默认从发布日起）</span></label>
                <input v-model="assignForm.start_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>要求天数</label>
                <input v-model.number="assignForm.required_days" type="number" min="1" class="form-input" placeholder="如：14" />
              </div>
            </template>
            <template v-if="assignForm.type === 'chat'">
              <div class="form-group">
                <label>统计起始日期 <span class="opt">（选填，默认从发布日起）</span></label>
                <input v-model="assignForm.start_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label>要求对话轮数</label>
                <input v-model.number="assignForm.required_rounds" type="number" min="1" class="form-input" placeholder="如：20" />
              </div>
            </template>
            <template v-if="assignForm.type === 'qa'">
              <div class="form-group">
                <div class="qa-label-row">
                  <label>问题列表</label>
                  <button class="add-q-btn" @click="addQuestion"><Plus :size="13" /> 添加问题</button>
                </div>
                <div v-for="(q, i) in questions" :key="i" class="q-block">
                  <div class="q-header">
                    <span class="q-num">Q{{ i + 1 }}</span>
                    <button class="icon-btn icon-btn-danger" @click="questions.splice(i, 1)"><X :size="13" /></button>
                  </div>
                  <input v-model="q.text" class="form-input" :placeholder="`问题 ${i + 1}…`" />
                  <textarea v-model="q.description" class="form-textarea q-desc" rows="2" placeholder="补充说明（选填）…" />
                </div>
              </div>
            </template>
            <template v-if="assignForm.type === 'paper'">
              <div class="form-group">
                <label>提交方式</label>
                <div class="radio-group">
                  <label v-for="m in SUBMIT_MODES" :key="m.value" class="radio-opt">
                    <input type="radio" v-model="assignForm.submission_mode" :value="m.value" />
                    {{ m.label }}
                  </label>
                </div>
              </div>
            </template>
            <div class="form-group">
              <label>截止日期 <span class="opt">（选填）</span></label>
              <input v-model="assignForm.due_date" type="date" class="form-input" />
            </div>
            <p v-if="assignDateError" class="date-error-msg">截止日期不能早于统计起始日期</p>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="assignFormVisible = false">取消</button>
            <button class="btn-primary" :disabled="saving || assignDateError" @click="saveAssignment">{{ saving ? '发布中…' : '发布' }}</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 发起话题弹窗 -->
    <Transition name="modal">
      <div v-if="threadFormVisible" class="modal-overlay" @click.self="threadFormVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>发起话题</span>
            <button class="modal-close" @click="threadFormVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>话题标题</label>
              <input v-model="threadForm.title" class="form-input" placeholder="…" maxlength="200" />
            </div>
            <div class="form-group">
              <label>内容 <span class="opt">（选填）</span></label>
              <textarea v-model="threadForm.content" class="form-textarea" rows="4" />
            </div>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="threadFormVisible = false">取消</button>
            <button class="btn-primary" :disabled="saving" @click="saveThread">{{ saving ? '…' : '发起' }}</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 小组编辑弹窗（仅编辑已有小组） -->
    <Transition name="modal">
      <div v-if="groupFormVisible" class="modal-overlay" @click.self="groupFormVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>编辑小组</span>
            <button class="modal-close" @click="groupFormVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>小组名称</label>
              <input v-model="groupForm.name" class="form-input" placeholder="如：第一组" maxlength="100" />
            </div>
            <div class="form-group">
              <div class="qa-label-row">
                <label>成员（学生 ID）</label>
                <button class="add-q-btn" @click="groupForm.member_ids.push('')"><Plus :size="13" /> 添加</button>
              </div>
              <div v-for="(id, i) in groupForm.member_ids" :key="i" class="member-id-row">
                <input v-model="groupForm.member_ids[i]" class="form-input" placeholder="学生 ID…" />
                <button class="icon-btn icon-btn-danger" @click="groupForm.member_ids.splice(i, 1)"><X :size="13" /></button>
              </div>
            </div>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="groupFormVisible = false">取消</button>
            <button class="btn-primary" :disabled="saving" @click="saveGroup">{{ saving ? '…' : '保存' }}</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 随机分组弹窗 -->
    <Transition name="modal">
      <div v-if="randomGroupVisible" class="modal-overlay" @click.self="randomGroupVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>随机分组</span>
            <button class="modal-close" @click="randomGroupVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>每组人数</label>
              <input v-model.number="randomGroupSize" type="number" min="1" :max="members.length || 99" class="form-input" placeholder="如：4" />
            </div>
            <p class="random-hint">
              共 {{ members.length }} 名成员，将分为
              <strong>{{ computeGroupSizes(members.length, randomGroupSize || 4).length }}</strong> 组。
              <span v-if="groups.length > 0" class="form-error">现有 {{ groups.length }} 个小组将被清除。</span>
            </p>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="randomGroupVisible = false">取消</button>
            <button class="btn-primary" :disabled="saving || !randomGroupSize || randomGroupSize < 1" @click="doRandomGroup">
              {{ saving ? '分组中…' : '开始分组' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 添加成员弹窗 -->
    <Transition name="modal">
      <div v-if="memberFormVisible" class="modal-overlay" @click.self="memberFormVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>添加成员</span>
            <button class="modal-close" @click="memberFormVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>学生姓名</label>
              <input v-model="memberForm.student_name" class="form-input" placeholder="真实姓名" />
            </div>
            <div class="form-group">
              <label>学生 ID</label>
              <input v-model="memberForm.student_id" class="form-input" placeholder="学生在「心理课」显示的 ID" />
            </div>
            <p v-if="memberError" class="form-error">{{ memberError }}</p>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="memberFormVisible = false">取消</button>
            <button class="btn-primary" :disabled="saving" @click="doAddMember">{{ saving ? '…' : '添加' }}</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronLeft, ChevronRight, Plus, Trash2, X, Loader2, AlertCircle,
  FileText, MessageSquare, Users, CalendarDays, Pin, UserPlus,
  Edit3, BookOpen, ClipboardList, Upload, Shuffle, BotMessageSquare,
} from 'lucide-vue-next'
import { useAuth }   from '@/composables/useAuth'
import { useUserId } from '@/composables/useUserId'
import {
  getClass, getAssignments, createAssignment, deleteAssignment,
  getThreads, createThread, deleteThread, pinThread,
  getMembers, addMember, removeMember,
  getGroups, createGroup, updateGroup, deleteGroup, getMyGroup,
  getCheckinProgress, getChatProgress,
} from '@/api/courses'


const route   = useRoute()
const router  = useRouter()
const classId = Number(route.params.classId)
const { isTeacher } = useAuth()
const userId  = useUserId()

const TYPE_LABEL = { checkin: '情绪打卡', qa: '课堂问答', paper: '综合作业', chat: 'AI情绪对话' }
const ASSIGN_TYPES = [
  { value: 'checkin', label: '情绪打卡',   icon: CalendarDays,    desc: '按天数统计日记完成情况' },
  { value: 'chat',    label: 'AI情绪对话', icon: BotMessageSquare, desc: '按对话轮数统计AI沟通完成情况' },
  { value: 'qa',      label: '课堂问答',   icon: ClipboardList,   desc: '多题问答，Markdown 作答' },
  { value: 'paper',   label: '综合作业',   icon: Upload,          desc: '报告/论文，支持文件或 Markdown' },
]
const SUBMIT_MODES = [
  { value: 'markdown', label: 'Markdown 在线撰写' },
  { value: 'file',     label: '文件上传（PDF/DOCX/ZIP…）' },
  { value: 'both',     label: '两种方式均可' },
]
const TABS = computed(() => {
  const t = [
    { key: 'assignments', label: '作业',     icon: FileText     },
    { key: 'discuss',     label: '全班讨论', icon: MessageSquare },
    { key: 'groups',      label: '小组讨论', icon: Users        },
  ]
  if (isTeacher.value) t.push({ key: 'members', label: '成员', icon: Users })
  return t
})

const loading    = ref(true)
const error      = ref('')
const activeTab  = ref('assignments')
const classInfo  = ref(null)
const assignments = ref([])
const threads    = ref([])
const groups     = ref([])
const myGroup    = ref(null)
const members    = ref([])
const saving     = ref(false)
const checkinMap = reactive({})  // assignment_id → CheckinProgress
const chatMap    = reactive({})  // assignment_id → ChatProgress

onMounted(async () => {
  try {
    const [ci, as_, th] = await Promise.all([
      getClass(classId),
      getAssignments(classId),
      getThreads(classId),
    ])
    classInfo.value   = ci
    assignments.value = as_
    threads.value     = th

    if (isTeacher.value) {
      const [grps, mems] = await Promise.all([getGroups(classId), getMembers(classId)])
      groups.value  = grps
      members.value = mems
    } else {
      myGroup.value = await getMyGroup(classId, userId)
      await Promise.all([
        ...as_.filter(x => x.type === 'checkin').map(async a => {
          checkinMap[a.id] = await getCheckinProgress(a.id, userId)
        }),
        ...as_.filter(x => x.type === 'chat').map(async a => {
          chatMap[a.id] = await getChatProgress(a.id, userId)
        }),
      ])
    }
  } catch {
    error.value = '加载失败，请检查后端服务'
  } finally {
    loading.value = false
  }
})

const fmtDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}
const isOverdue  = (d) => d && new Date(d) < new Date()
const checkinPct = (id) => {
  const p = checkinMap[id]
  if (!p || !p.required_days) return 0
  return Math.min(100, Math.round(p.completed_days / p.required_days * 100))
}
const chatPct = (id) => {
  const p = chatMap[id]
  if (!p || !p.required_rounds) return 0
  return Math.min(100, Math.round(p.completed_rounds / p.required_rounds * 100))
}

const goAssignment = (a) => router.push(`/course/${classId}/assignment/${a.id}`)
const goThread     = (t) => router.push(`/course/${classId}/discuss/${t.id}`)
const goGroup      = (g) => router.push(`/course/${classId}/group/${g.id}`)

// ── 作业 ─────────────────────────────────────────────────────────────────────
const assignFormVisible = ref(false)
const questions = ref([{ text: '', description: '' }])
const assignForm = reactive({
  title: '', description: '', due_date: '', type: 'qa',
  required_days: null, start_date: '', required_rounds: null, submission_mode: 'both',
})
const assignDateError = computed(() =>
  ['checkin', 'chat'].includes(assignForm.type) &&
  assignForm.start_date && assignForm.due_date && assignForm.due_date < assignForm.start_date
)

const openAssignForm = () => {
  Object.assign(assignForm, { title: '', description: '', due_date: '', type: 'qa', required_days: null, start_date: '', required_rounds: null, submission_mode: 'both' })
  questions.value = [{ text: '', description: '' }]
  assignFormVisible.value = true
}
const addQuestion = () => questions.value.push({ text: '', description: '' })

const saveAssignment = async () => {
  if (!assignForm.title.trim()) return
  saving.value = true
  try {
    const payload = {
      title:           assignForm.title.trim(),
      description:     assignForm.description.trim() || null,
      due_date:        assignForm.due_date || null,
      type:            assignForm.type,
      required_days:   assignForm.type === 'checkin' ? (assignForm.required_days || null) : null,
      start_date:      ['checkin', 'chat'].includes(assignForm.type) ? (assignForm.start_date || null) : null,
      required_rounds: assignForm.type === 'chat' ? (assignForm.required_rounds || null) : null,
      questions_json:  assignForm.type === 'qa' ? JSON.stringify(questions.value.filter(q => q.text.trim())) : null,
      submission_mode: assignForm.type === 'paper' ? assignForm.submission_mode : null,
    }
    const a = await createAssignment(classId, payload)
    assignments.value.unshift({ ...a, submission_count: 0, graded_count: 0 })
    assignFormVisible.value = false
  } finally { saving.value = false }
}

const doDeleteAssignment = async (a) => {
  if (!confirm(`确认删除「${a.title}」？`)) return
  await deleteAssignment(a.id)
  assignments.value = assignments.value.filter(x => x.id !== a.id)
}

// ── 全班讨论 ─────────────────────────────────────────────────────────────────
const threadFormVisible = ref(false)
const threadForm = reactive({ title: '', content: '' })

const saveThread = async () => {
  if (!threadForm.title.trim()) return
  saving.value = true
  try {
    const t = await createThread(classId, {
      title: threadForm.title.trim(), content: threadForm.content.trim() || null,
      author_id: userId, author_name: isTeacher.value ? '教师' : '同学',
    })
    threads.value.unshift({ ...t, reply_count: 0 })
    threadFormVisible.value = false
  } finally { saving.value = false }
}
const doPin = async (t) => {
  Object.assign(t, await pinThread(t.id))
  threads.value.sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0))
}
const doDeleteThread = async (t) => {
  if (!confirm(`确认删除「${t.title}」？`)) return
  await deleteThread(t.id)
  threads.value = threads.value.filter(x => x.id !== t.id)
}

// ── 小组 ─────────────────────────────────────────────────────────────────────
const groupFormVisible = ref(false)
const groupFormEditing = ref(null)
const groupForm = reactive({ name: '', member_ids: [] })

const openGroupForm = (g = null) => {
  groupFormEditing.value = g
  if (g) {
    groupForm.name = g.name
    groupForm.member_ids = [...(g.member_ids || [])]
  } else {
    groupForm.name = ''
    groupForm.member_ids = []
  }
  groupFormVisible.value = true
}
const saveGroup = async () => {
  if (!groupForm.name.trim()) return
  saving.value = true
  try {
    const payload = { name: groupForm.name.trim(), member_ids: groupForm.member_ids.filter(Boolean) }
    if (groupFormEditing.value) {
      const updated = await updateGroup(groupFormEditing.value.id, payload)
      Object.assign(groupFormEditing.value, updated)
    } else {
      groups.value.push(await createGroup(classId, payload))
    }
    groupFormVisible.value = false
  } finally { saving.value = false }
}
const doDeleteGroup = async (g) => {
  if (!confirm(`确认删除小组「${g.name}」？`)) return
  await deleteGroup(g.id)
  groups.value = groups.value.filter(x => x.id !== g.id)
}

// ── 成员 ─────────────────────────────────────────────────────────────────────
const memberFormVisible = ref(false)
const memberForm = reactive({ student_name: '', student_id: '' })
const memberError = ref('')

const doAddMember = async () => {
  memberError.value = ''
  if (!memberForm.student_name.trim() || !memberForm.student_id.trim()) return
  saving.value = true
  try {
    members.value.push(await addMember(classId, { student_name: memberForm.student_name.trim(), student_id: memberForm.student_id.trim() }))
    memberFormVisible.value = false
  } catch (e) {
    memberError.value = e?.response?.data?.detail || '添加失败'
  } finally { saving.value = false }
}
const doRemoveMember = async (m) => {
  if (!confirm(`确认移除「${m.student_name}」？`)) return
  await removeMember(classId, m.student_id)
  members.value = members.value.filter(x => x.id !== m.id)
}

// ── 随机分组 ──────────────────────────────────────────────────────────────────
const randomGroupVisible = ref(false)
const randomGroupSize    = ref(4)

function computeGroupSizes(n, G) {
  if (n === 0 || G <= 0) return []
  const base = Math.floor(n / G)
  const rem  = n % G
  if (base === 0) return [n]
  if (rem  === 0) return Array(base).fill(G)
  if (rem * 2 <= G && rem <= base) {
    return [...Array(rem).fill(G + 1), ...Array(base - rem).fill(G)]
  }
  return [...Array(base).fill(G), rem]
}

const doRandomGroup = async () => {
  const G = Number(randomGroupSize.value)
  if (!G || G < 1) return
  if (members.value.length === 0) {
    alert('班级暂无成员，请先在「成员管理」中添加学生')
    return
  }
  if (groups.value.length > 0 && !confirm('确认清除现有所有小组并重新随机分组？')) return

  saving.value = true
  try {
    for (const g of groups.value) await deleteGroup(g.id)
    groups.value = []

    const shuffled = [...members.value].sort(() => Math.random() - 0.5)
    const sizes    = computeGroupSizes(shuffled.length, G)
    let idx = 0
    for (let i = 0; i < sizes.length; i++) {
      const slice = shuffled.slice(idx, idx + sizes[i])
      idx += sizes[i]
      groups.value.push(await createGroup(classId, {
        name:       `第${i + 1}组`,
        member_ids: slice.map(m => m.student_id),
      }))
    }
    randomGroupVisible.value = false
  } finally { saving.value = false }
}
</script>

<style scoped>
/* ── 全屏布局 ── */
.cp-wrap {
  display: flex;
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: #f6f2ec;
}

/* ── 侧边栏 ── */
.cp-sidebar {
  width: 220px;
  min-width: 220px;
  background: linear-gradient(180deg, #2d5a42 0%, #3d6e52 100%);
  display: flex;
  flex-direction: column;
  padding: 16px 0 0;
  overflow-y: auto;
}
.cp-back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12.5px;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  padding: 0 16px 12px;
  transition: color 0.15s;
}
.cp-back:hover { color: rgba(255,255,255,0.9); }
.cp-course-name {
  font-size: 15px;
  font-weight: 700;
  color: white;
  padding: 0 16px 20px;
  line-height: 1.4;
  font-family: var(--f-serif, serif);
  letter-spacing: 0.5px;
}
.cp-nav { display: flex; flex-direction: column; gap: 2px; padding: 0 8px; flex: 1; }
.cp-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: none;
  border-radius: var(--r-md);
  background: none;
  color: rgba(255,255,255,0.65);
  font-size: 14px;
  cursor: pointer;
  transition: background var(--t-base), color var(--t-base);
  text-align: left;
}
.cp-nav-item:hover { background: rgba(255,255,255,0.1); color: white; }
.cp-nav-item.active { background: rgba(255,255,255,0.18); color: white; font-weight: 600; }
.nav-badge { margin-left: auto; background: #c9a96e; color: white; font-size: 11px; padding: 1px 7px; border-radius: var(--r-pill); }
.cp-sidebar-footer { padding: 12px 8px 16px; }
.sidebar-manage-btn {
  display: flex; align-items: center; gap: 6px;
  width: 100%; padding: 9px 12px;
  background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
  border-radius: 6px; color: rgba(255,255,255,0.75); font-size: 13px; cursor: pointer;
  transition: background 0.15s;
}
.sidebar-manage-btn:hover { background: rgba(255,255,255,0.18); color: white; }

/* ── 主内容区 ── */
.cp-main {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.cp-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; padding: 60px 0; color: #94a3b8; font-size: 14px;
}
.cp-state-err { color: #b84545; }

.cp-panel { padding: 24px; flex: 1; }
.discuss-panel { display: flex; flex-direction: column; }
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px; padding-bottom: 12px;
  border-bottom: 2px solid #e8e0d4;
}
.panel-title { font-size: 16px; font-weight: 700; color: #1c2b22; }
.cp-empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 48px 0; color: #b0bec5; font-size: 14px; }

/* ── 作业列表 ── */
.assign-row {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; background: white;
  border: 1px solid var(--c-beige-border); border-radius: var(--r-md);
  margin-bottom: 8px; cursor: pointer;
  transition: border-color var(--t-base), background var(--t-base);
}
.assign-row:hover { border-color: #4a8763; background: #f5fbf7; }
.assign-type-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.type-checkin { background: #c9a96e; }
.type-chat    { background: #5a7ec4; }
.type-qa      { background: #4a8763; }
.type-paper   { background: #7c6e8a; }
.assign-body { flex: 1; }
.assign-title { font-size: 14.5px; font-weight: 600; color: #1c2b22; margin-bottom: 5px; }
.assign-meta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.type-chip { font-size: 11.5px; padding: 1px 8px; border-radius: var(--r-pill); background: #f0ebe2; color: #7a9080; }
.due-chip { display: inline-flex; align-items: center; gap: 3px; font-size: 11.5px; padding: 1px 8px; border-radius: var(--r-pill); }
.due-ok   { background: #e8f5ef; color: #3d6e52; }
.due-over { background: #fdf2f2; color: #b84545; }
.assign-stats { display: flex; gap: 12px; font-size: 12px; color: #94a3b8; flex-shrink: 0; }
.assign-del {
  padding: 6px; color: #b84545; opacity: 0.5; cursor: pointer;
  border-radius: 3px; transition: opacity 0.15s, background 0.15s;
}
.assign-del:hover { opacity: 1; background: #fdf2f2; }
.checkin-progress-mini { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #7a9080; flex-shrink: 0; }
.cp-bar-wrap { width: 60px; height: 5px; background: #e8e0d4; border-radius: 3px; overflow: hidden; }
.cp-bar-fill { height: 100%; background: #c9a96e; border-radius: 3px; transition: width 0.3s; }
.cp-bar-fill-chat { background: #5a7ec4; }

/* ── 讨论列表 ── */
.thread-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; background: white;
  border: 1px solid var(--c-beige-border); border-radius: var(--r-md);
  margin-bottom: 8px; cursor: pointer;
  transition: border-color var(--t-base);
}
.thread-row:hover { border-color: #4a8763; }
.thread-row-left { flex: 1; }
.pin-chip { display: inline-flex; align-items: center; gap: 3px; font-size: 11px; color: #c9a96e; background: #f5ead8; padding: 1px 6px; border-radius: var(--r-pill); margin-bottom: 4px; }
.thread-row-title { font-size: 14.5px; font-weight: 600; color: #1c2b22; margin-bottom: 4px; }
.thread-row-meta  { font-size: 12px; color: #94a3b8; }
.thread-row-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.reply-count { display: flex; align-items: center; gap: 4px; font-size: 12.5px; color: #94a3b8; }
.thread-actions { display: flex; gap: 2px; }
.pinned { color: #c9a96e; }

/* ── 小组 ── */
.group-card {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; background: white;
  border: 1px solid var(--c-beige-border); border-radius: var(--r-md);
  margin-bottom: 8px; cursor: pointer;
  transition: border-color var(--t-base);
}
.group-card:hover { border-color: #4a8763; }
.group-card-left { flex: 1; }
.group-name { font-size: 14.5px; font-weight: 600; color: #1c2b22; margin-bottom: 3px; }
.group-meta { font-size: 12px; color: #94a3b8; }
.group-card-actions { display: flex; gap: 4px; }
.group-chevron { color: #b0bec5; }
.my-group-card {
  display: flex; align-items: center; gap: 16px;
  padding: 20px; background: white;
  border: 2px solid #4a8763; border-radius: var(--r-lg);
  cursor: pointer; transition: background var(--t-base), box-shadow var(--t-base);
  box-shadow: var(--shadow-xs);
}
.my-group-card:hover { background: #f5fbf7; }
.my-group-icon { color: #4a8763; }

/* ── 成员表格 ── */
.member-table { width: 100%; border-collapse: collapse; border: 1px solid #e8e0d4; border-radius: 5px; overflow: hidden; background: white; }
.member-table th { background: #fdfaf5; padding: 9px 14px; font-size: 12px; font-weight: 600; color: #4a8763; text-align: left; border-bottom: 1px solid #e8e0d4; text-transform: uppercase; letter-spacing: 0.05em; }
.member-table td { padding: 10px 14px; font-size: 13.5px; color: #374151; border-bottom: 1px solid #f0ebe2; }
.member-table tr:last-child td { border-bottom: none; }
.member-table code { font-family: monospace; font-size: 12px; background: #f0ebe2; padding: 2px 7px; border-radius: 3px; }

/* ── 通用按钮 ── */
.btn-primary {
  display: inline-flex; align-items: center; gap: 5px;
  background: var(--c-green-deep); color: white; border: none;
  border-radius: var(--r-sm); font-size: 13px; font-weight: 600; cursor: pointer;
  transition: background var(--t-base);
}
.btn-primary:hover:not(:disabled) { background: #2d5a42; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sm { padding: 6px 14px; }
.btn-cancel { padding: 7px 16px; border: 1.5px solid #d4e8db; border-radius: var(--r-sm); background: white; color: #3d6e52; font-size: 13px; cursor: pointer; }
.btn-cancel:hover { background: #f0fbf4; }
.icon-btn { background: none; border: none; cursor: pointer; color: #7a9080; padding: 4px; display: flex; border-radius: var(--r-xs); transition: background var(--t-fast), color var(--t-fast); }
.icon-btn:hover { background: #f0fbf4; color: #3d6e52; }
.icon-btn-danger { color: #b84545; }
.icon-btn-danger:hover { background: #fdf2f2; }

/* ── 弹窗 ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 24px; }
.modal { background: white; border-radius: var(--r-xl); width: 100%; max-width: 520px; max-height: 85vh; overflow-y: auto; box-shadow: var(--shadow-xl); }
.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #e8e0d4; font-size: 15px; font-weight: 600; color: #1c2b22; position: sticky; top: 0; background: white; z-index: 1; }
.modal-close { background: none; border: none; cursor: pointer; font-size: 16px; color: #94a3b8; line-height: 1; }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.modal-foot { display: flex; justify-content: flex-end; gap: 10px; padding: 14px 20px; border-top: 1px solid #e8e0d4; position: sticky; bottom: 0; background: white; }

/* ── 表单 ── */
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 12px; font-weight: 600; color: #4a8763; text-transform: uppercase; letter-spacing: 0.06em; }
.opt { font-weight: 400; color: #94a3b8; text-transform: none; }
.date-error-msg { font-size: 12px; color: #b84545; margin: -4px 0 0; display: flex; align-items: center; gap: 4px; }
.form-input, .form-textarea {
  border: 1px solid #ddd6cc; border-radius: 4px; padding: 8px 10px;
  font-size: 13.5px; color: #1c2b22; background: #fdfaf5; font-family: inherit;
  outline: none; width: 100%; box-sizing: border-box;
}
.form-input:focus, .form-textarea:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.12); }
.form-textarea { resize: vertical; }
.form-error { font-size: 12.5px; color: #b84545; margin: 0; }

/* 作业类型选择器 */
.type-selector { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.type-opt {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 12px 8px; border: 2px solid var(--c-beige-border); border-radius: var(--r-md);
  background: var(--c-beige-card); cursor: pointer; transition: border-color var(--t-base), background var(--t-base);
  text-align: center;
}
.type-opt:hover { border-color: #4a8763; }
.type-opt.active { border-color: #3d6e52; background: #edf7f2; }
.type-opt-name { font-size: 13px; font-weight: 600; color: #1c2b22; }
.type-opt-desc { font-size: 11px; color: #94a3b8; line-height: 1.4; }

/* 问答题目 */
.qa-label-row { display: flex; align-items: center; justify-content: space-between; }
.add-q-btn {
  display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px;
  border: 1px solid #d4e8db; border-radius: var(--r-xs); background: none; color: #3d6e52;
  font-size: 12px; cursor: pointer; transition: background var(--t-base);
}
.add-q-btn:hover { background: #f0fbf4; }
.q-block { background: #f5fbf7; border: 1px solid #d4e8db; border-radius: var(--r-sm); padding: 12px; }
.q-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.q-num { font-size: 12px; font-weight: 700; color: #3d6e52; }
.q-desc { margin-top: 6px; min-height: 0; }

/* 综合作业提交方式 */
.radio-group { display: flex; flex-direction: column; gap: 8px; }
.radio-opt { display: flex; align-items: center; gap: 8px; font-size: 13.5px; color: #374151; cursor: pointer; }

/* 小组成员 ID 行 */
.member-id-row { display: flex; gap: 8px; margin-bottom: 6px; }
.member-id-row .form-input { margin: 0; }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 随机分组提示 */
.random-hint { font-size: 13px; color: #374151; margin: 0; line-height: 1.6; }

/* 弹窗动画 */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: translateY(12px); }
</style>
