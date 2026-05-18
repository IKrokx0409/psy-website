<template>
  <div class="gd-wrap">

    <!-- ── 顶栏 ── -->
    <div class="gd-header">
      <div class="gd-header-inner">
        <router-link :to="`/course/${classId}`" class="gd-back">
          <ChevronLeft :size="16" :stroke-width="2" /> 返回班级
        </router-link>
        <div class="gd-title-block">
          <div class="gd-group-name">{{ group?.name ?? '小组讨论' }}</div>
          <div class="gd-members-row">
            <Users :size="13" :stroke-width="1.5" />
            <span v-if="memberNames">{{ memberNames }}</span>
            <span v-else class="gd-no-members">暂无成员</span>
          </div>
        </div>
        <div v-if="isTeacher" class="gd-teacher-badge">
          <ShieldCheck :size="13" :stroke-width="1.5" /> 教师视图 · 只读
        </div>
      </div>
    </div>

    <!-- ── 主体 ── -->
    <div v-if="loading" class="gd-state">
      <Loader2 :size="28" :stroke-width="1.5" class="spin" /><span>加载中…</span>
    </div>
    <div v-else-if="error" class="gd-state gd-state-err">
      <AlertCircle :size="20" /><span>{{ error }}</span>
    </div>

    <div v-else class="gd-body">

      <!-- ── 左：聊天区 ── -->
      <div class="gd-chat">

        <!-- 消息列表 -->
        <div class="gd-messages" ref="msgEl">
          <div v-if="messages.length === 0" class="gd-empty">
            <MessageSquare :size="36" :stroke-width="1" style="opacity:.2" />
            <span>还没有消息，开始讨论吧</span>
          </div>

          <template v-else>
            <div
              v-for="m in messages" :key="m.id"
              :class="['gd-msg', { 'gd-msg--mine': !isTeacher && m.author_id === userId }]"
            >
              <div class="gd-msg-meta">
                <span class="gd-msg-author">
                  {{ !isTeacher && m.author_id === userId ? '我' : m.author_name }}
                </span>
                <span class="gd-msg-time">{{ fmtTime(m.created_at) }}</span>
                <button
                  v-if="isTeacher || m.author_id === userId"
                  class="gd-msg-del"
                  @click="doDeleteMsg(m)"
                  title="删除"
                >
                  <Trash2 :size="11" :stroke-width="1.5" />
                </button>
              </div>
              <div class="gd-msg-bubble">{{ m.content }}</div>
            </div>
          </template>
        </div>

        <!-- 输入框（非教师） -->
        <div v-if="!isTeacher" class="gd-input-row">
          <textarea
            v-model="newMsg"
            class="gd-input"
            placeholder="说点什么… （Enter 发送，Shift+Enter 换行）"
            rows="2"
            @keydown.enter.exact.prevent="doSend"
          />
          <button
            class="gd-send-btn"
            @click="doSend"
            :disabled="!newMsg.trim() || sending"
          >
            <Send :size="15" :stroke-width="2" />
          </button>
        </div>
        <div v-else class="gd-readonly-hint">
          <Eye :size="13" :stroke-width="1.5" /> 教师只读 · 每 5 秒自动刷新
        </div>

      </div>

      <!-- ── 右：结论面板 ── -->
      <div class="gd-side">

        <!-- 成员卡 -->
        <div class="gd-panel">
          <div class="gd-panel-title"><Users :size="14" /> 小组成员</div>
          <div v-if="group?.member_ids?.length" class="gd-member-list">
            <div v-for="id in group.member_ids" :key="id" class="gd-member-item">
              <UserCircle :size="16" :stroke-width="1.5" class="gd-member-icon" />
              <span>{{ memberNameMap[id] ?? id }}</span>
            </div>
          </div>
          <div v-else class="gd-panel-empty">暂无成员</div>
        </div>

        <!-- 结论卡 -->
        <div class="gd-panel gd-conclusion-panel">
          <div class="gd-panel-title">
            <FileText :size="14" /> 小组结论
            <span v-if="conclusion" class="gd-submitted-chip">
              <CheckCircle2 :size="11" /> 已提交
            </span>
          </div>

          <!-- 学生可编辑 -->
          <textarea
            v-if="!isTeacher"
            v-model="conclusionText"
            class="gd-conclusion-textarea"
            placeholder="在此填写本组的讨论结论……（所有成员均可修改）"
          />
          <!-- 教师只读 -->
          <div v-else class="gd-conclusion-readonly">
            <span v-if="conclusion?.content">{{ conclusion.content }}</span>
            <span v-else class="gd-panel-empty">（本组尚未提交结论）</span>
          </div>

          <div v-if="conclusion?.updated_by_name" class="gd-conclusion-meta">
            <Clock :size="12" />
            由 <strong>{{ conclusion.updated_by_name }}</strong> 于 {{ fmtTime(conclusion.updated_at) }} 更新
          </div>

          <div v-if="saveMsg" :class="['gd-save-msg', saveMsg.type === 'ok' ? 'gd-save-ok' : 'gd-save-err']">
            {{ saveMsg.text }}
          </div>

          <button
            v-if="!isTeacher"
            class="gd-save-btn"
            @click="doSaveConclusion"
            :disabled="saving"
          >
            {{ saving ? '保存中…' : '保存结论' }}
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronLeft, Users, MessageSquare, Send, Trash2,
  FileText, CheckCircle2, UserCircle, Clock, Eye,
  Loader2, AlertCircle, ShieldCheck,
} from 'lucide-vue-next'
import { useAuth }   from '@/composables/useAuth'
import { useUserId } from '@/composables/useUserId'
import {
  getGroup, getMessages, sendMessage, deleteMessage,
  getConclusion, setConclusion,
  getMembers,
} from '@/api/courses'

const route   = useRoute()
const router  = useRouter()
const classId = Number(route.params.classId)
const groupId = Number(route.params.groupId)

const { isTeacher } = useAuth()
const userId = useUserId()

// ── 状态 ─────────────────────────────────────────────────────────────────────
const loading  = ref(true)
const error    = ref('')
const group    = ref(null)
const messages = ref([])
const conclusion     = ref(null)
const conclusionText = ref('')
const newMsg   = ref('')
const sending  = ref(false)
const saving   = ref(false)
const saveMsg  = ref(null)
const msgEl    = ref(null)

// member_id → name 映射（供教师视图显示真实姓名）
const memberNameMap = ref({})

const memberNames = computed(() => {
  if (!group.value?.member_ids?.length) return ''
  return group.value.member_ids
    .map(id => memberNameMap.value[id] ?? id)
    .join('、')
})

// ── 加载 ──────────────────────────────────────────────────────────────────────
const loadAll = async () => {
  const [g, msgs, conc] = await Promise.all([
    getGroup(groupId),
    getMessages(groupId),
    getConclusion(groupId),
  ])
  group.value      = g
  messages.value   = msgs
  conclusion.value = conc
  if (conc && !saving.value) conclusionText.value = conc.content ?? ''
}

// 仅刷新消息+结论（轮询用）
const refreshLive = async () => {
  const [msgs, conc] = await Promise.all([
    getMessages(groupId),
    getConclusion(groupId),
  ])
  const wasAtBottom = isAtBottom()
  messages.value   = msgs
  conclusion.value = conc
  if (!saving.value) conclusionText.value = conc?.content ?? ''
  if (wasAtBottom) await scrollBottom()
}

onMounted(async () => {
  try {
    await loadAll()
    // 加载班级成员以建立 id→name 映射
    try {
      const members = await getMembers(classId)
      members.forEach(m => { memberNameMap.value[m.student_id] = m.student_name })
    } catch {}
    await scrollBottom()
  } catch {
    error.value = '加载失败，请检查后端服务'
  } finally {
    loading.value = false
  }
  startPoll()
})

// ── 轮询 ──────────────────────────────────────────────────────────────────────
let pollTimer = null
const startPoll = () => {
  pollTimer = setInterval(refreshLive, 5000)
}
onUnmounted(() => clearInterval(pollTimer))

// ── 滚动 ──────────────────────────────────────────────────────────────────────
const isAtBottom = () => {
  const el = msgEl.value
  if (!el) return true
  return el.scrollHeight - el.scrollTop - el.clientHeight < 60
}
const scrollBottom = async () => {
  await nextTick()
  if (msgEl.value) msgEl.value.scrollTop = msgEl.value.scrollHeight
}

// ── 发送消息 ──────────────────────────────────────────────────────────────────
const doSend = async () => {
  const text = newMsg.value.trim()
  if (!text || sending.value) return
  sending.value = true
  try {
    const msg = await sendMessage(groupId, {
      author_id:   userId,
      author_name: userId,
      content:     text,
    })
    messages.value.push(msg)
    newMsg.value = ''
    await scrollBottom()
  } finally {
    sending.value = false
  }
}

// ── 删除消息 ──────────────────────────────────────────────────────────────────
const doDeleteMsg = async (m) => {
  if (!confirm('确认删除这条消息？')) return
  await deleteMessage(groupId, m.id)
  messages.value = messages.value.filter(x => x.id !== m.id)
}

// ── 保存结论 ──────────────────────────────────────────────────────────────────
const doSaveConclusion = async () => {
  if (saving.value) return
  saving.value = true
  saveMsg.value = null
  try {
    conclusion.value = await setConclusion(groupId, {
      content:         conclusionText.value,
      updated_by_id:   userId,
      updated_by_name: userId,
    })
    saveMsg.value = { type: 'ok', text: '结论已保存' }
  } catch {
    saveMsg.value = { type: 'err', text: '保存失败，请重试' }
  } finally {
    saving.value = false
    setTimeout(() => { saveMsg.value = null }, 3000)
  }
}

// ── 时间格式化 ────────────────────────────────────────────────────────────────
const fmtTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (d.toDateString() === now.toDateString()) {
    return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  }
  return `${d.getMonth()+1}月${d.getDate()}日 ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
</script>

<style scoped>
/* ── 整体布局 ── */
.gd-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #f6f2ec;
  font-family: var(--f-sans);
}

/* ── 顶栏 ── */
.gd-header {
  background: linear-gradient(160deg, #2d5a42 0%, #4a8763 100%);
  flex-shrink: 0;
  padding: 0;
}
.gd-header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.gd-back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12.5px;
  color: rgba(255,255,255,0.65);
  text-decoration: none;
  white-space: nowrap;
  transition: color 0.15s;
}
.gd-back:hover { color: white; }
.gd-title-block { flex: 1; min-width: 0; }
.gd-group-name {
  font-size: 16px;
  font-weight: 700;
  color: white;
  font-family: var(--f-serif, serif);
  letter-spacing: 0.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.gd-members-row {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  margin-top: 2px;
}
.gd-no-members { font-style: italic; }
.gd-teacher-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  padding: 4px 10px;
  border-radius: 20px;
  white-space: nowrap;
}

/* ── 加载/错误状态 ── */
.gd-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #94a3b8;
  font-size: 14px;
}
.gd-state-err { color: #b84545; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 主体双栏 ── */
.gd-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  gap: 0;
}

/* ── 左：聊天区 ── */
.gd-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #e0d9cf;
}

.gd-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.gd-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #b0bec5;
  font-size: 13px;
  padding: 48px 0;
}

/* 消息气泡 */
.gd-msg {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 72%;
}
.gd-msg--mine {
  align-self: flex-end;
  align-items: flex-end;
}
.gd-msg-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.gd-msg--mine .gd-msg-meta { flex-direction: row-reverse; }
.gd-msg-author {
  font-size: 12px;
  font-weight: 600;
  color: #4a8763;
}
.gd-msg--mine .gd-msg-author { color: #7a9080; }
.gd-msg-time { font-size: 11px; color: #b0bec5; }
.gd-msg-del {
  background: none;
  border: none;
  cursor: pointer;
  color: #c0b8ac;
  padding: 0 2px;
  display: flex;
  border-radius: 3px;
  transition: color 0.15s, background 0.15s;
  opacity: 0;
}
.gd-msg:hover .gd-msg-del { opacity: 1; }
.gd-msg-del:hover { color: #b84545; background: #fdf2f2; }
.gd-msg-bubble {
  background: white;
  border: 1px solid #e0d9cf;
  border-radius: 12px 12px 12px 2px;
  padding: 10px 14px;
  font-size: 14px;
  color: #1c2b22;
  line-height: 1.6;
  word-break: break-word;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.gd-msg--mine .gd-msg-bubble {
  background: #3d6e52;
  border-color: #3d6e52;
  color: white;
  border-radius: 12px 12px 2px 12px;
}

/* 输入区 */
.gd-input-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid #e0d9cf;
  background: white;
  flex-shrink: 0;
}
.gd-input {
  flex: 1;
  border: 1px solid #d8d2c8;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  color: #1c2b22;
  font-family: inherit;
  resize: none;
  outline: none;
  background: #fdfaf5;
  transition: border-color 0.15s;
  line-height: 1.5;
}
.gd-input:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.12); }
.gd-send-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3d6e52;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s;
}
.gd-send-btn:hover:not(:disabled) { background: #2d5a42; }
.gd-send-btn:disabled { opacity: 0.45; cursor: not-allowed; }

.gd-readonly-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 12px;
  color: #94a3b8;
  background: #fdfaf5;
  border-top: 1px solid #e0d9cf;
  flex-shrink: 0;
}

/* ── 右：侧边面板 ── */
.gd-side {
  width: 300px;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: #f9f5ef;
  padding: 16px;
  gap: 14px;
}

.gd-panel {
  background: white;
  border: 1px solid #e0d9cf;
  border-radius: 10px;
  padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.gd-panel-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12.5px;
  font-weight: 700;
  color: #3d6e52;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 10px;
}
.gd-panel-empty {
  font-size: 13px;
  color: #b0bec5;
  font-style: italic;
}

/* 成员列表 */
.gd-member-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.gd-member-item {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13.5px;
  color: #374151;
}
.gd-member-icon { color: #7a9080; flex-shrink: 0; }

/* 结论面板 */
.gd-conclusion-panel { flex: 1; display: flex; flex-direction: column; }
.gd-submitted-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  background: #edf7f2;
  color: #3d6e52;
  font-size: 10.5px;
  padding: 1px 7px;
  border-radius: 20px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0;
  margin-left: auto;
}

.gd-conclusion-textarea {
  flex: 1;
  min-height: 140px;
  border: 1px solid #d8d2c8;
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 13.5px;
  font-family: inherit;
  color: #1c2b22;
  background: #fdfaf5;
  resize: vertical;
  outline: none;
  line-height: 1.65;
  transition: border-color 0.15s;
  margin-bottom: 10px;
}
.gd-conclusion-textarea:focus {
  border-color: #4a8763;
  box-shadow: 0 0 0 2px rgba(74,135,99,0.12);
}

.gd-conclusion-readonly {
  font-size: 13.5px;
  color: #374151;
  line-height: 1.7;
  white-space: pre-wrap;
  padding: 10px 12px;
  background: #f9f5ef;
  border: 1px solid #e8e0d4;
  border-radius: 6px;
  min-height: 80px;
  margin-bottom: 10px;
  flex: 1;
}

.gd-conclusion-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: #94a3b8;
  margin-bottom: 10px;
}

.gd-save-msg {
  font-size: 12.5px;
  padding: 6px 10px;
  border-radius: 5px;
  margin-bottom: 8px;
}
.gd-save-ok  { background: #edf7f2; color: #3d6e52; }
.gd-save-err { background: #fdf2f2; color: #b84545; }

.gd-save-btn {
  width: 100%;
  padding: 9px;
  background: #3d6e52;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.gd-save-btn:hover:not(:disabled) { background: #2d5a42; }
.gd-save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── 响应式 ── */
@media (max-width: 700px) {
  .gd-body { flex-direction: column; overflow: auto; }
  .gd-chat { min-height: 50vh; border-right: none; border-bottom: 1px solid #e0d9cf; }
  .gd-side { width: 100%; min-width: unset; }
}
</style>
