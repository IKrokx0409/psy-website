<template>
  <div class="dd-page">

    <div class="dd-header">
      <div class="dd-header-inner">
        <router-link :to="`/course/${classId}`" class="dd-back">
          <ChevronLeft :size="16" :stroke-width="2" /> 返回班级
        </router-link>
        <h1 v-if="thread" class="dd-title">{{ thread.title }}</h1>
      </div>
    </div>

    <div v-if="loading" class="dd-state"><Loader2 :size="28" class="spin" /><span>加载中…</span></div>
    <div v-else-if="error" class="dd-state dd-state-err"><AlertCircle :size="18" /><span>{{ error }}</span></div>

    <div v-else class="dd-body">

      <!-- 原帖 -->
      <div class="post-card post-card--origin">
        <div class="post-head">
          <div class="post-author">
            <UserCircle :size="32" :stroke-width="1.5" class="avatar" />
            <div>
              <div class="author-name">{{ thread.author_name }}</div>
              <div class="post-time">{{ fmtDate(thread.created_at) }}</div>
            </div>
          </div>
          <div v-if="isTeacher" class="post-teacher-actions">
            <button class="btn-icon" :class="{ 'icon-pinned': thread.pinned }" @click="doPin" :title="thread.pinned ? '取消置顶' : '置顶'">
              <Pin :size="14" />
            </button>
            <button class="btn-icon btn-icon-danger" @click="doDeleteThread">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
        <div v-if="thread.content" class="post-content">{{ thread.content }}</div>
        <div v-if="thread.pinned" class="pin-indicator"><Pin :size="11" /> 已置顶</div>
      </div>

      <!-- 回复列表 -->
      <div class="replies-section">
        <div class="replies-label">{{ thread.replies.length }} 条回复</div>

        <div v-for="r in thread.replies" :key="r.id" class="post-card">
          <div class="post-head">
            <div class="post-author">
              <UserCircle :size="28" :stroke-width="1.5" class="avatar avatar--sm" />
              <div>
                <div class="author-name">{{ r.author_name }}</div>
                <div class="post-time">{{ fmtDate(r.created_at) }}</div>
              </div>
            </div>
            <button
              v-if="isTeacher || r.author_id === userId"
              class="btn-icon btn-icon-danger"
              @click="doDeleteReply(r)"
            >
              <Trash2 :size="13" />
            </button>
          </div>
          <div class="post-content">{{ r.content }}</div>
        </div>

        <div v-if="thread.replies.length === 0" class="no-replies">
          <MessageSquare :size="28" :stroke-width="1" style="opacity:.25" />
          <span>暂无回复，发表第一条吧</span>
        </div>
      </div>

      <!-- 回复框 -->
      <div class="reply-form">
        <div class="reply-form-label">发表回复</div>
        <textarea
          v-model="replyContent"
          class="reply-textarea"
          rows="4"
          placeholder="写下你的想法…"
          :disabled="submitting"
        />
        <div class="reply-actions">
          <button
            class="btn-primary"
            :disabled="submitting || !replyContent.trim()"
            @click="doReply"
          >
            {{ submitting ? '发表中…' : '发表回复' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronLeft, UserCircle, Pin, Trash2, MessageSquare, Loader2, AlertCircle,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useUserId } from '@/composables/useUserId'
import { getThread, addReply, deleteThread, deleteReply, pinThread } from '@/api/courses'

const route    = useRoute()
const router   = useRouter()
const classId  = Number(route.params.classId)
const threadId = Number(route.params.threadId)
const { isTeacher } = useAuth()
const userId   = useUserId()

const loading  = ref(true)
const error    = ref('')
const thread   = ref(null)
const replyContent = ref('')
const submitting   = ref(false)

onMounted(async () => {
  try {
    thread.value = await getThread(threadId)
  } catch {
    error.value = '加载失败，请检查后端服务'
  } finally {
    loading.value = false
  }
})

const fmtDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const doPin = async () => {
  const updated = await pinThread(threadId)
  Object.assign(thread.value, updated)
}

const doDeleteThread = async () => {
  if (!confirm('确认删除此讨论及所有回复？')) return
  await deleteThread(threadId)
  router.push(`/course/${classId}`)
}

const doDeleteReply = async (r) => {
  if (!confirm('确认删除此回复？')) return
  await deleteReply(r.id)
  thread.value.replies = thread.value.replies.filter(x => x.id !== r.id)
}

const doReply = async () => {
  if (!replyContent.value.trim()) return
  submitting.value = true
  try {
    const r = await addReply(threadId, {
      author_id:   userId,
      author_name: isTeacher.value ? '教师' : '我',
      content:     replyContent.value.trim(),
    })
    thread.value.replies.push(r)
    replyContent.value = ''
  } finally { submitting.value = false }
}
</script>

<style scoped>
.dd-page { background: #f6f2ec; min-height: 100vh; }
.dd-header { background: linear-gradient(160deg, #2d5a42 0%, #4a8763 100%); padding: 16px 0; color: white; }
.dd-header-inner { max-width: 780px; margin: 0 auto; padding: 0 24px; }
.dd-back { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; color: rgba(255,255,255,0.75); text-decoration: none; margin-bottom: 8px; }
.dd-back:hover { color: white; }
.dd-title { font-size: 22px; font-weight: 700; color: white; margin: 0; font-family: var(--f-serif, serif); letter-spacing: 1px; word-break: break-word; }

.dd-state { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 0; color: #94a3b8; font-size: 14px; }
.dd-state-err { color: #b84545; }

.dd-body { max-width: 780px; margin: 0 auto; padding: 24px; }

.post-card {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  padding: 16px 18px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-xs);
}
.post-card--origin {
  border-left: 4px solid #4a8763;
  margin-bottom: 24px;
}
.post-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 10px; }
.post-author { display: flex; align-items: center; gap: 10px; }
.avatar { color: #4a8763; }
.avatar--sm { color: #7a9080; }
.author-name { font-size: 14px; font-weight: 600; color: #1c2b22; }
.post-time { font-size: 12px; color: #94a3b8; }
.post-content { font-size: 14px; line-height: 1.75; color: #374151; white-space: pre-wrap; }
.pin-indicator { margin-top: 10px; font-size: 11.5px; color: #c9a96e; display: flex; align-items: center; gap: 4px; }

.post-teacher-actions { display: flex; gap: 4px; }

.replies-section { margin-bottom: 24px; }
.replies-label { font-size: 12.5px; font-weight: 600; color: #4a8763; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 12px; }
.no-replies { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 32px 0; color: #94a3b8; font-size: 13.5px; }

.reply-form { background: white; border: 1px solid var(--c-beige-border); border-radius: var(--r-lg); padding: 18px; box-shadow: var(--shadow-xs); }
.reply-form-label { font-size: 13px; font-weight: 600; color: #3d6e52; margin-bottom: 10px; }
.reply-textarea { width: 100%; border: 1px solid #ddd6cc; border-radius: var(--r-sm); padding: 10px 12px; font-size: 14px; line-height: 1.75; color: #1c2b22; background: var(--c-beige-card); font-family: inherit; resize: vertical; outline: none; box-sizing: border-box; min-height: 100px; }
.reply-textarea:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.1); }
.reply-textarea:disabled { opacity: 0.6; }
.reply-actions { display: flex; justify-content: flex-end; margin-top: 10px; }

.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 8px 18px; background: var(--c-green-deep); color: white; border: none; border-radius: var(--r-sm); font-size: 13.5px; font-weight: 600; cursor: pointer; transition: background var(--t-base); }
.btn-primary:hover:not(:disabled) { background: #2d5a42; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-icon { background: none; border: none; cursor: pointer; color: #7a9080; padding: 4px; display: flex; border-radius: var(--r-xs); transition: background var(--t-fast), color var(--t-fast); }
.btn-icon:hover { background: #f0fbf4; color: #3d6e52; }
.btn-icon-danger { color: #b84545; }
.btn-icon-danger:hover { background: #fdf2f2; }
.icon-pinned { color: #c9a96e; }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
