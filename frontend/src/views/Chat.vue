<template>
  <div class="chat-layout">
    <!-- ============ 侧边栏 ============ -->
    <aside class="sidebar">
      <div class="sidebar-top">
        <button class="new-chat-btn" @click="startNewConversation">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          开启新对话
        </button>
      </div>

      <div class="history-label">历史对话</div>
      <div class="history-list">
        <div
          v-for="conv in conversationHistory"
          :key="conv.id"
          :class="['history-item', { active: currentConvId === conv.id }]"
          @click="loadConversation(conv)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14" class="history-icon">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span class="history-name">{{ conv.name }}</span>
        </div>
        <div v-if="conversationHistory.length === 0" class="history-empty">暂无历史对话</div>
      </div>
    </aside>

    <!-- ============ 主对话区 ============ -->
    <main class="chat-main">
      <!-- 顶部标题栏 -->
      <div class="chat-header">
        <span class="chat-title">大学生心理疗愈智能体</span>
        <span class="chat-subtitle">基于 HITSZ HiAgent 2.0</span>
      </div>

      <!-- 消息区域 -->
      <div class="messages-area" ref="messagesEl">
        <!-- 欢迎屏（无消息时） -->
        <div v-if="messages.length === 0" class="welcome-screen">
          <div class="welcome-icon"><Leaf :size="52" :stroke-width="1" /></div>
          <h2 class="welcome-title">你好，我在这里</h2>
          <p class="welcome-sub">无论学业压力还是生活烦恼，都可以跟我倾诉</p>
          <div class="welcome-hints">
            <div class="hint-chip" @click="fillHint('最近学业压力很大，我不知道怎么办')">学业压力</div>
            <div class="hint-chip" @click="fillHint('我感觉很迷茫，不知道未来在哪里')">迷茫与方向</div>
            <div class="hint-chip" @click="fillHint('我和朋友之间有些矛盾，需要倾诉')">人际关系</div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-for="(msg, index) in messages" :key="index" :class="['message-row', msg.role]">
          <!-- AI 消息 -->
          <template v-if="msg.role === 'assistant'">
            <div class="avatar ai-avatar"><Bot :size="16" :stroke-width="1.5" /></div>
            <div class="message-content">
              <!-- 加载中 -->
              <div v-if="msg.isLoading" class="reply-bubble loading-bubble">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
              </div>
              <template v-else>
                <!-- 推理块（可折叠） -->
                <details v-if="msg.thought" class="thought-block">
                  <summary class="thought-summary">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
                    </svg>
                    推理过程
                  </summary>
                  <div class="thought-content">{{ msg.thought }}</div>
                </details>
                <!-- 正式回复 -->
                <div class="reply-bubble markdown-body" v-html="renderMd(msg.reply)"></div>
              </template>
            </div>
          </template>

          <!-- 用户消息 -->
          <template v-else>
            <div class="message-content user-content">
              <div class="user-bubble">{{ msg.content }}</div>
            </div>
            <div class="avatar user-avatar">你</div>
          </template>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-wrapper">
        <div class="input-box">
          <textarea
            ref="textareaEl"
            v-model="inputText"
            placeholder="有什么心事，都可以跟我说说..."
            @keydown="handleKeydown"
            @input="autoResize"
            :disabled="isSending"
            rows="1"
          ></textarea>
          <button class="send-btn" @click="sendMessage" :disabled="isSending || !inputText.trim()">
            <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
        <div class="input-hint">Enter 发送 · Shift+Enter 换行</div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'
import { Bot, Leaf } from 'lucide-vue-next'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

// DOM refs
const messagesEl = ref(null)
const textareaEl = ref(null)

// 聊天状态
const messages = ref([])
const inputText = ref('')
const isSending = ref(false)

// 会话管理
const conversationHistory = ref([])  // 本地历史列表
const currentConvId = ref(null)       // 当前本地会话 ID
const hiagentConvId = ref(null)       // HiAgent 返回的 AppConversationID

// ===== 初始化：从 localStorage 加载历史 =====
onMounted(() => {
  const saved = localStorage.getItem('wellbeing_conversations')
  if (saved) {
    try {
      conversationHistory.value = JSON.parse(saved)
    } catch {
      conversationHistory.value = []
    }
  }
})

// ===== 工具函数 =====
const saveToStorage = () => {
  localStorage.setItem('wellbeing_conversations', JSON.stringify(conversationHistory.value))
}

const renderMd = (text) => {
  if (!text) return ''
  return md.render(text)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

// 消息变化时自动滚底
watch(messages, scrollToBottom, { deep: true })

// ===== 输入框自适应高度 =====
const autoResize = () => {
  const ta = textareaEl.value
  if (!ta) return
  ta.style.height = 'auto'
  ta.style.height = Math.min(ta.scrollHeight, 200) + 'px'
}

const resetTextarea = () => {
  if (textareaEl.value) {
    textareaEl.value.style.height = 'auto'
  }
}

// Enter 发送 / Shift+Enter 换行
const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// ===== 欢迎界面快捷提示 =====
const fillHint = (text) => {
  inputText.value = text
  nextTick(() => {
    textareaEl.value?.focus()
    autoResize()
  })
}

// ===== 会话管理 =====
const updateCurrentInHistory = () => {
  const idx = conversationHistory.value.findIndex(c => c.id === currentConvId.value)
  if (idx >= 0) {
    conversationHistory.value[idx].messages = [...messages.value]
    conversationHistory.value[idx].hiagentConvId = hiagentConvId.value
    saveToStorage()
  }
}

const startNewConversation = () => {
  if (messages.value.length > 0 && currentConvId.value) {
    updateCurrentInHistory()
  }
  messages.value = []
  inputText.value = ''
  currentConvId.value = null
  hiagentConvId.value = null
  resetTextarea()
}

const loadConversation = (conv) => {
  if (messages.value.length > 0 && currentConvId.value && currentConvId.value !== conv.id) {
    updateCurrentInHistory()
  }
  currentConvId.value = conv.id
  hiagentConvId.value = conv.hiagentConvId
  messages.value = [...conv.messages]
}

// ===== 发送消息 =====
const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isSending.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  resetTextarea()

  isSending.value = true
  messages.value.push({ role: 'assistant', isLoading: true, thought: '', reply: '' })

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/chat', {
      message: text,
      conversation_id: hiagentConvId.value || null
    })

    messages.value.pop()

    if (response.data.conversation_id) {
      hiagentConvId.value = response.data.conversation_id
    }

    messages.value.push({
      role: 'assistant',
      thought: response.data.thought || '',
      reply: response.data.reply || '',
      isLoading: false
    })

    // 首次回复时创建历史条目
    if (!currentConvId.value) {
      const newConv = {
        id: Date.now().toString(),
        name: text.length > 18 ? text.slice(0, 18) + '…' : text,
        hiagentConvId: hiagentConvId.value,
        messages: [...messages.value],
        createdAt: Date.now()
      }
      currentConvId.value = newConv.id
      conversationHistory.value.unshift(newConv)
      saveToStorage()
    } else {
      updateCurrentInHistory()
    }

  } catch (error) {
    messages.value.pop()
    messages.value.push({
      role: 'assistant',
      thought: '',
      reply: '抱歉，我的思绪暂时飘远了（服务器连接断开），请检查后端是否在运行哦。',
      isLoading: false
    })
    console.error(error)
  } finally {
    isSending.value = false
  }
}
</script>

<style scoped>
/* ========== 整体布局 ========== */
.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
  background: #f7f8fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  overflow: hidden;
}

/* ========== 侧边栏 ========== */
.sidebar {
  width: 260px;
  min-width: 260px;
  background: linear-gradient(180deg, #2d5a42 0%, #3d6e52 100%);
  color: #c9d8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-top {
  padding: 16px 14px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 9px 14px;
  background: rgba(255,255,255,0.14);
  color: white;
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.new-chat-btn:hover { background: rgba(255,255,255,0.24); }

.history-label {
  padding: 14px 16px 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: rgba(255,255,255,0.35);
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px 16px;
}
.history-list::-webkit-scrollbar { width: 4px; }
.history-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 2px; }

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  color: rgba(255,255,255,0.6);
  font-size: 13.5px;
}
.history-item:hover { background: rgba(255,255,255,0.1); color: white; }
.history-item.active { background: rgba(255,255,255,0.18); color: white; }

.history-icon { flex-shrink: 0; opacity: 0.7; }
.history-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.history-empty {
  padding: 16px 10px;
  font-size: 13px;
  color: rgba(255,255,255,0.3);
  text-align: center;
}

/* ========== 主区域 ========== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
}

.chat-header {
  padding: 16px 28px;
  border-bottom: 1px solid #f0f0f2;
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-shrink: 0;
}
.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1b26;
}
.chat-subtitle {
  font-size: 12px;
  color: #9ca3af;
}

/* ========== 消息滚动区 ========== */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
}
.messages-area::-webkit-scrollbar { width: 6px; }
.messages-area::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 3px; }

/* ========== 欢迎屏 ========== */
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 360px;
  text-align: center;
  padding: 0 40px;
}
.welcome-icon { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; color: #5f9e75; }
.welcome-title { font-size: 26px; font-weight: 600; color: #1a1b26; margin: 0 0 10px; }
.welcome-sub { font-size: 15px; color: #6b7280; margin: 0 0 32px; }

.welcome-hints { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.hint-chip {
  padding: 8px 16px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  font-size: 13.5px;
  color: #374151;
  cursor: pointer;
  transition: all 0.15s;
}
.hint-chip:hover {
  background: #c4e2d0;
  border-color: #93c5fd;
  color: #5f9e75;
}

/* ========== 消息行 ========== */
.message-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 8px 28px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
.message-row.user { flex-direction: row-reverse; }

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}
.ai-avatar {
  background: #c4e2d0;
  color: #4d8764;
}
.user-avatar {
  background: #5f9e75;
  color: white;
  font-size: 12px;
  letter-spacing: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.user-content { align-items: flex-end; }

/* ========== 推理块 ========== */
.thought-block {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
}
.thought-summary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 12.5px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  user-select: none;
  list-style: none;
}
.thought-summary::-webkit-details-marker { display: none; }
.thought-summary::before {
  content: '▶';
  font-size: 9px;
  color: #9ca3af;
  transition: transform 0.2s;
}
details[open] .thought-summary::before { transform: rotate(90deg); }
.thought-content {
  padding: 10px 14px 14px;
  font-size: 13px;
  color: #6b7280;
  font-style: italic;
  line-height: 1.6;
  border-top: 1px solid #e5e7eb;
  white-space: pre-wrap;
}

/* ========== 气泡样式 ========== */
.reply-bubble {
  background: #f7f8fa;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 18px;
  font-size: 14.5px;
  line-height: 1.7;
  color: #1a1b26;
  word-break: break-word;
}

.user-bubble {
  background: #5f9e75;
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 18px;
  font-size: 14.5px;
  line-height: 1.6;
  max-width: 75%;
  word-break: break-word;
  white-space: pre-wrap;
}

/* 加载气泡 */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
  background: #f7f8fa;
}
.typing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #9ca3af;
  animation: typingBounce 1.2s infinite ease-in-out;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-6px); opacity: 1; }
}

/* ========== 输入区 ========== */
.input-wrapper {
  padding: 16px 28px 20px;
  background: white;
  border-top: 1px solid #f0f0f2;
  flex-shrink: 0;
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #f7f8fa;
  border: 1.5px solid #e5e7eb;
  border-radius: 14px;
  padding: 10px 12px;
  transition: border-color 0.2s;
  max-width: 900px;
  margin: 0 auto;
}
.input-box:focus-within { border-color: #5f9e75; }

.input-box textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-size: 14.5px;
  line-height: 1.6;
  color: #1a1b26;
  font-family: inherit;
  outline: none;
  max-height: 200px;
  overflow-y: auto;
}
.input-box textarea::placeholder { color: #9ca3af; }
.input-box textarea:disabled { opacity: 0.6; }

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: #5f9e75;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s, opacity 0.2s;
}
.send-btn:hover:not(:disabled) { background: #4d8764; }
.send-btn:disabled { background: #d1d5db; cursor: not-allowed; }

.input-hint {
  text-align: center;
  font-size: 11.5px;
  color: #d1d5db;
  margin-top: 8px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

/* ========== Markdown 内容样式 ========== */
</style>

<style>
/* Markdown 渲染（非 scoped，作用于 v-html 内容） */
.markdown-body { font-size: 14.5px; line-height: 1.75; color: #1a1b26; }
.markdown-body p { margin: 0 0 10px; }
.markdown-body p:last-child { margin-bottom: 0; }
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  font-weight: 600; margin: 16px 0 8px; color: #111827;
}
.markdown-body h1 { font-size: 20px; }
.markdown-body h2 { font-size: 17px; }
.markdown-body h3 { font-size: 15px; }
.markdown-body ul, .markdown-body ol { padding-left: 20px; margin: 8px 0; }
.markdown-body li { margin: 4px 0; }
.markdown-body code {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 13px;
  font-family: ui-monospace, Consolas, monospace;
  color: #5f9e75;
}
.markdown-body pre {
  background: #1a1b26;
  border-radius: 10px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}
.markdown-body pre code {
  background: none;
  border: none;
  padding: 0;
  color: #e2e4eb;
  font-size: 13px;
}
.markdown-body blockquote {
  border-left: 3px solid #5f9e75;
  margin: 10px 0;
  padding: 6px 16px;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 0 6px 6px 0;
}
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
  margin: 12px 0;
}
.markdown-body th, .markdown-body td {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}
.markdown-body th { background: #f3f4f6; font-weight: 600; }
.markdown-body tr:hover td { background: #fafafa; }
.markdown-body a { color: #7c3aed; text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }
.markdown-body hr { border: none; border-top: 1px solid #e5e7eb; margin: 16px 0; }
</style>
