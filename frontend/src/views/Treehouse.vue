<template>
  <div class="th-page">

    <!-- ══ 页头 ══════════════════════════════════════════════════════════ -->
    <header class="th-header">
      <div class="th-nav-blend"></div>
      <div class="th-ambient" aria-hidden="true"></div>

      <!-- 弹幕层 -->
      <div class="th-danmaku" aria-hidden="true">
        <span
          v-for="pill in danmakuPills"
          :key="pill.id"
          class="th-danmaku-pill"
          :style="{
            top: pill.top + '%',
            animationDuration: pill.duration + 's',
            animationDelay: pill.delay + 's',
            opacity: pill.opacity,
          }"
        >{{ pill.text }}</span>
      </div>

      <!-- 内容层 -->
      <div class="th-header-content">
        <div class="th-icon-ring">
          <TreePine :size="34" :stroke-width="1.2" class="th-header-icon" />
        </div>
        <h1 class="th-title">校园树洞</h1>
        <p class="th-subtitle">说出你的故事，这里有人在听<br>每一条心声都会被温柔对待</p>
        <div class="th-header-actions">
          <button class="th-bottle-trigger" @click="fetchBottle" :disabled="fetchingBottle">
            <Loader2 v-if="fetchingBottle" :size="15" :stroke-width="1.5" class="spin" />
            <Waves v-else :size="15" :stroke-width="1.5" />
            捞一条漂流瓶
          </button>
          <button class="th-compose-btn" @click="showCompose = true">
            <PenLine :size="15" :stroke-width="1.5" /> 说点什么
          </button>
        </div>
      </div>

      <!-- 波浪底部 -->
      <div class="th-wave-sep" aria-hidden="true">
        <svg viewBox="0 0 1440 60" preserveAspectRatio="none" fill="none">
          <path d="M0,30 C240,58 480,4 720,30 C960,56 1200,4 1440,30 L1440,60 L0,60 Z" fill="#050b14"/>
        </svg>
      </div>
    </header>

    <!-- ══ 帖子列表 ═══════════════════════════════════════════════════ -->
    <main class="th-feed-wrap">
      <div class="th-feed-inner">

        <div class="th-meta" v-if="!loading && !error">
          <span class="th-meta-dot"></span>
          {{ posts.length }} 条心声，按时间排序
        </div>

        <div v-if="loading" class="th-state">
          <Loader2 :size="28" :stroke-width="1.5" class="spin" />
          <span>正在聆听…</span>
        </div>

        <div v-else-if="error" class="th-state th-state-error">
          <AlertCircle :size="24" :stroke-width="1.5" />
          <span>加载失败，请检查后端服务</span>
        </div>

        <div v-else-if="posts.length === 0" class="th-state">
          <MessageCircle :size="40" :stroke-width="1" style="opacity:0.25" />
          <span>这里还没有心声，来说第一句话吧</span>
          <button class="th-compose-btn-sm" @click="showCompose = true">立即发布</button>
        </div>

        <div v-else class="th-grid">
          <article
            v-for="post in posts"
            :key="post.id"
            class="th-card"
          >
            <div class="th-card-shimmer"></div>
            <div class="th-card-top">
              <span class="th-name">{{ post.anonymous_name }}</span>
              <span class="th-time">{{ timeAgo(post.created_at) }}</span>
            </div>
            <p class="th-content">{{ post.content }}</p>
            <div class="th-card-bottom">
              <div class="th-tags">
                <span v-for="tag in post.tags" :key="tag" :class="['th-tag', tagClass(tag)]">
                  {{ tag }}
                </span>
              </div>
              <button
                v-if="myToken(post.id) && post.status !== 'delete_requested'"
                class="th-delete-btn"
                @click="handleDeleteRequest(post)"
              >
                <Trash2 :size="12" :stroke-width="1.5" />
              </button>
              <span v-else-if="myToken(post.id)" class="th-delete-pending">已申请删除</span>
            </div>
          </article>
        </div>

      </div>
    </main>

    <!-- ══ 漂流瓶弹窗 ════════════════════════════════════════════════ -->
    <Transition name="th-modal">
      <div v-if="bottle" class="th-overlay" @click.self="bottle = null">
        <div class="th-bottle-card">
          <div class="th-bottle-header">
            <Waves :size="17" :stroke-width="1.5" />
            <span>{{ bottle._empty ? '大海空空如也' : '你捞到了一条漂流瓶' }}</span>
          </div>
          <template v-if="bottle._empty">
            <p class="th-bottle-content" style="opacity:0.45;font-style:italic">
              大海里还没有漂流瓶，快来投下第一条吧
            </p>
          </template>
          <template v-else>
            <span class="th-name th-bottle-name">{{ bottle.anonymous_name }}</span>
            <p class="th-bottle-content">{{ bottle.content }}</p>
            <div class="th-tags th-bottle-tags">
              <span v-for="tag in bottle.tags" :key="tag" :class="['th-tag', tagClass(tag)]">
                {{ tag }}
              </span>
            </div>
          </template>
          <div class="th-bottle-foot">
            <button v-if="!bottle._empty" class="th-bottle-again" @click="fetchBottle" :disabled="fetchingBottle">
              <Loader2 v-if="fetchingBottle" :size="13" :stroke-width="1.5" class="spin" />
              <Shuffle v-else :size="13" :stroke-width="1.5" />
              再捞一条
            </button>
            <button class="th-bottle-close" @click="bottle = null">放回大海</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══ 发帖弹窗 ════════════════════════════════════════════════════ -->
    <Transition name="th-modal">
      <div v-if="showCompose" class="th-overlay" @click.self="closeCompose">
        <div class="th-modal">

          <div class="th-modal-head">
            <span>说出你的心声</span>
            <button class="th-close-btn" @click="closeCompose"><X :size="18" /></button>
          </div>

          <div class="th-form-group">
            <textarea
              v-model="form.content"
              class="th-textarea"
              placeholder="有什么想说的，这里没有人认识你……"
              rows="5"
              maxlength="500"
            ></textarea>
            <div class="th-char-count">{{ form.content.length }} / 500</div>
          </div>

          <div class="th-form-group">
            <div class="th-form-label">选择标签（可多选）</div>
            <div class="th-tag-picker">
              <button
                v-for="tag in TAG_OPTIONS"
                :key="tag.name"
                :class="['th-tag-opt', tag.cls, { selected: form.tags.includes(tag.name) }]"
                @click="toggleTag(tag.name)"
              >{{ tag.name }}</button>
            </div>
          </div>

          <div class="th-form-group">
            <div class="th-form-label">可见范围</div>
            <div class="th-vis-row">
              <button
                :class="['th-vis-opt', { active: form.visibility === 'public' }]"
                @click="form.visibility = 'public'"
              >
                <span class="th-vis-dot th-vis-dot--public"></span>
                公开
                <span class="th-vis-hint">出现在下方列表</span>
              </button>
              <button
                :class="['th-vis-opt', { active: form.visibility === 'bottle_only' }]"
                @click="form.visibility = 'bottle_only'"
              >
                <span class="th-vis-dot th-vis-dot--bottle"></span>
                仅投入大海
                <span class="th-vis-hint">只能靠漂流瓶捞到</span>
              </button>
            </div>
          </div>

          <div class="th-form-group">
            <div class="th-form-label">选择你的匿名身份</div>
            <div class="th-nickname-row">
              <select v-model="form.adjective" class="th-select">
                <option v-for="a in ADJECTIVES" :key="a" :value="a">{{ a }}</option>
              </select>
              <select v-model="form.noun" class="th-select">
                <option v-for="n in NOUNS" :key="n" :value="n">{{ n }}</option>
              </select>
              <button class="th-random-btn" @click="randomize" title="随机">
                <Shuffle :size="14" :stroke-width="1.5" />
              </button>
            </div>
            <div class="th-nickname-preview">你将以「{{ form.adjective }}{{ form.noun }}」发言</div>
          </div>

          <div class="th-modal-foot">
            <p v-if="submitError" class="th-submit-error">{{ submitError }}</p>
            <p v-if="submitSuccess" class="th-submit-ok">
              已提交！通过审核后将{{ submittedVisibility === 'bottle_only' ? '投入大海，等待漂流瓶打捞' : '公开显示' }}。
            </p>
            <button
              class="th-submit-btn"
              :disabled="submitting || form.content.trim().length < 5"
              @click="submitPost"
            >
              <Loader2 v-if="submitting" :size="15" :stroke-width="1.5" class="spin" />
              <Send v-else :size="15" :stroke-width="1.5" />
              {{ submitting ? '提交中…' : '发布树洞' }}
            </button>
          </div>

        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  TreePine, PenLine, Waves, Loader2, AlertCircle,
  MessageCircle, Trash2, X, Shuffle, Send,
} from 'lucide-vue-next'
import { getPosts, createPost, requestDelete, getMyToken, getBottle } from '@/api/treehole'

// ── 昵称数据 ──────────────────────────────────────────────────────────
const ADJECTIVES = [
  '慵懒的', '迷路的', '快乐的', '温柔的', '勇敢的', '害羞的', '好奇的',
  '安静的', '活泼的', '文艺的', '呆萌的', '淡定的', '热情的', '腼腆的',
  '睿智的', '可爱的', '神秘的', '欢脱的', '沉稳的', '纯真的',
]
const NOUNS = [
  '小熊猫', '云朵', '蘑菇', '薯条', '水獭', '柴犬', '仙人掌', '棉花糖',
  '星星', '月亮', '向日葵', '企鹅', '松鼠', '奶茶', '彩虹', '萤火虫',
  '猫咪', '兔子', '橘子', '雪花',
]
const TAG_OPTIONS = [
  { name: '学业压力', cls: 'tag-teal'    },
  { name: '人际关系', cls: 'tag-emerald' },
  { name: '就业焦虑', cls: 'tag-amber'   },
  { name: '情感困惑', cls: 'tag-pink'    },
  { name: '生活琐事', cls: 'tag-sage'    },
  { name: '分享快乐', cls: 'tag-green'   },
  { name: '其他',     cls: 'tag-slate'   },
]
const TAG_CLASS_MAP = Object.fromEntries(TAG_OPTIONS.map(t => [t.name, t.cls]))
const tagClass = (name) => TAG_CLASS_MAP[name] || 'tag-slate'

// ── 列表状态 ─────────────────────────────────────────────────────────
const posts = ref([])
const loading = ref(true)
const error = ref(false)

// ── 散落弹幕 ─────────────────────────────────────────────────────────
const danmakuPills = ref([])

const buildDanmaku = (postList) => {
  const EXCERPT_LEN = 18
  const excerpts = postList.map(p =>
    p.content.length > EXCERPT_LEN ? p.content.slice(0, EXCERPT_LEN) + '…' : p.content
  )
  const PER_BAND = 7
  const STEP = 4.5
  const pills = []
  for (let b = 0; b < 2; b++) {
    const base = b === 0 ? 3 : 70
    for (let j = 0; j < PER_BAND; j++) {
      const i = b * PER_BAND + j
      const top = base + j * STEP
      const duration = 28 + (i * 4.1) % 28
      const delay    = -((i * 8.3) % duration)
      const opacity  = 0.13 + (j % 4) * 0.025
      pills.push({
        id: i,
        text: excerpts[i % excerpts.length],
        top: +top.toFixed(1),
        duration: +duration.toFixed(1),
        delay:    +delay.toFixed(1),
        opacity,
      })
    }
  }
  danmakuPills.value = pills
}

onMounted(async () => {
  try {
    posts.value = await getPosts()
    if (posts.value.length) buildDanmaku(posts.value)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})

// ── 漂流瓶 ───────────────────────────────────────────────────────────
const bottle         = ref(null)
const fetchingBottle = ref(false)
const bottleEmpty    = ref(false)

const fetchBottle = async () => {
  fetchingBottle.value = true
  bottleEmpty.value = false
  try {
    const result = await getBottle(bottle.value?.id)
    if (!result) {
      bottleEmpty.value = true
      bottle.value = { _empty: true }
    } else {
      bottle.value = result
    }
  } finally {
    fetchingBottle.value = false
  }
}

// ── 发帖表单 ─────────────────────────────────────────────────────────
const showCompose        = ref(false)
const submitting         = ref(false)
const submitError        = ref('')
const submitSuccess      = ref(false)
const submittedVisibility = ref('public')

const randItem = (arr) => arr[Math.floor(Math.random() * arr.length)]

const form = reactive({
  content: '',
  tags: [],
  adjective: randItem(ADJECTIVES),
  noun: randItem(NOUNS),
  visibility: 'public',
})

const randomize = () => {
  form.adjective = randItem(ADJECTIVES)
  form.noun = randItem(NOUNS)
}

const toggleTag = (tag) => {
  const idx = form.tags.indexOf(tag)
  idx === -1 ? form.tags.push(tag) : form.tags.splice(idx, 1)
}

const closeCompose = () => {
  showCompose.value = false
  submitError.value = ''
  submitSuccess.value = false
}

const submitPost = async () => {
  submitError.value = ''
  submitSuccess.value = false
  submitting.value = true
  try {
    submittedVisibility.value = form.visibility
    await createPost({
      anonymous_name: form.adjective + form.noun,
      content: form.content.trim(),
      tags: form.tags,
      visibility: form.visibility,
    })
    submitSuccess.value = true
    form.content = ''
    form.tags = []
    form.adjective = randItem(ADJECTIVES)
    form.noun = randItem(NOUNS)
    form.visibility = 'public'
  } catch (e) {
    submitError.value = e?.response?.data?.detail || '提交失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

// ── 删除申请 ─────────────────────────────────────────────────────────
const myToken = (postId) => getMyToken(postId)

const handleDeleteRequest = async (post) => {
  if (!confirm('确认申请删除这条树洞？')) return
  try {
    await requestDelete(post.id)
    post.status = 'delete_requested'
  } catch (e) {
    alert(e?.response?.data?.detail || '操作失败')
  }
}

// ── 时间格式化 ────────────────────────────────────────────────────────
const timeAgo = (isoStr) => {
  const diff = Date.now() - new Date(isoStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1)  return '刚刚'
  if (m < 60) return `${m} 分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h} 小时前`
  const d = Math.floor(h / 24)
  if (d < 30) return `${d} 天前`
  return new Date(isoStr).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');

/* ── 基底 ────────────────────────────────────────────────────────────── */
.th-page {
  min-height: 100%;
  background: #050b14;
  color: #a8cce0;
  font-family: var(--f-sans);
}

/* ── 页头 ────────────────────────────────────────────────────────────── */
.th-header {
  position: relative;
  overflow: hidden;
  padding: 84px 24px 100px;
  text-align: center;
  background: #080f1c;
}

/* 导航栏渐变遮罩 */
.th-nav-blend {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 72px;
  background: linear-gradient(to bottom, #0c1a2e 0%, transparent 100%);
  pointer-events: none;
  z-index: 2;
}

/* 环境光 — CSS 动画三色径向渐变 */
.th-ambient {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background:
    radial-gradient(ellipse 70% 60% at 15% 70%, rgba(0, 190, 160, 0.09) 0%, transparent 65%),
    radial-gradient(ellipse 50% 70% at 85% 30%, rgba(20, 90, 200, 0.08) 0%, transparent 65%),
    radial-gradient(ellipse 80% 50% at 50% 105%, rgba(0, 60, 120, 0.18) 0%, transparent 55%);
  animation: ambient-breathe 14s ease-in-out infinite alternate;
}

@keyframes ambient-breathe {
  0%   { opacity: 0.7; }
  50%  { opacity: 1;   }
  100% { opacity: 0.75; }
}

/* ── 弹幕 ──────────────────────────────────────────────────────────── */
.th-danmaku {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.th-danmaku-pill {
  position: absolute;
  left: 0;
  background: rgba(0, 200, 180, 0.05);
  border: 1px solid rgba(0, 200, 180, 0.09);
  color: rgba(140, 220, 210, 0.5);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  white-space: nowrap;
  animation: danmaku-float linear infinite;
  will-change: transform;
  letter-spacing: 0.03em;
}

@keyframes danmaku-float {
  from { transform: translateX(110vw); }
  to   { transform: translateX(-110vw); }
}

/* ── 页头内容 ──────────────────────────────────────────────────────── */
.th-header-content {
  position: relative;
  z-index: 3;
}

.th-icon-ring {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(0, 200, 165, 0.07);
  border: 1px solid rgba(0, 200, 165, 0.2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 0 24px rgba(0, 200, 165, 0.12), inset 0 0 16px rgba(0, 200, 165, 0.05);
  animation: ring-pulse 4s ease-in-out infinite;
}

@keyframes ring-pulse {
  0%, 100% { box-shadow: 0 0 24px rgba(0,200,165,0.12), inset 0 0 16px rgba(0,200,165,0.05); }
  50%       { box-shadow: 0 0 36px rgba(0,200,165,0.22), inset 0 0 24px rgba(0,200,165,0.10); }
}

.th-header-icon { color: #00c8a8; }

.th-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 14px;
  letter-spacing: 4px;
  color: #d8f0f8;
  text-shadow: 0 0 40px rgba(0, 200, 165, 0.3);
}

.th-subtitle {
  font-size: 14.5px;
  color: #4a8aaa;
  line-height: 1.85;
  margin: 0 0 36px;
  letter-spacing: 0.04em;
}

.th-header-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.th-bottle-trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: #00c8a8;
  border: 1px solid rgba(0, 200, 168, 0.4);
  padding: 10px 24px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 0 16px rgba(0, 200, 165, 0.15);
  letter-spacing: 0.03em;
}
.th-bottle-trigger:hover {
  border-color: #00c8a8;
  color: #50e8d0;
  box-shadow: 0 0 28px rgba(0, 200, 165, 0.32);
  background: rgba(0, 200, 165, 0.05);
}
.th-bottle-trigger:disabled { opacity: 0.3; cursor: not-allowed; box-shadow: none; }

.th-compose-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 200, 165, 0.14);
  color: #c8f0e8;
  border: 1px solid rgba(0, 200, 165, 0.35);
  padding: 10px 28px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 20px rgba(0, 200, 165, 0.1);
  letter-spacing: 0.03em;
}
.th-compose-btn:hover {
  background: rgba(0, 200, 165, 0.22);
  border-color: rgba(0, 200, 165, 0.6);
  box-shadow: 0 4px 28px rgba(0, 200, 165, 0.25);
  transform: translateY(-1px);
}

/* 波浪分隔 */
.th-wave-sep {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  z-index: 4;
  line-height: 0;
}
.th-wave-sep svg {
  width: 100%;
  height: 60px;
  display: block;
}

/* ── Feed ────────────────────────────────────────────────────────────── */
.th-feed-wrap {
  padding: 36px 28px 72px;
}
.th-feed-inner {
  max-width: 1160px;
  margin: 0 auto;
}

.th-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #2a5a78;
  margin-bottom: 22px;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.04em;
}
.th-meta-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #00c8a8;
  box-shadow: 0 0 8px rgba(0,200,165,0.6);
  flex-shrink: 0;
  animation: dot-glow 2.5s ease-in-out infinite;
}
@keyframes dot-glow {
  0%, 100% { box-shadow: 0 0 6px rgba(0,200,165,0.5); }
  50%       { box-shadow: 0 0 14px rgba(0,200,165,0.9); }
}

.th-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 0;
  color: #2a5a78;
  font-size: 14px;
}
.th-state-error { color: #f87171; }

.th-compose-btn-sm {
  background: rgba(0, 200, 165, 0.12);
  color: #00c8a8;
  border: 1px solid rgba(0, 200, 165, 0.25);
  padding: 8px 20px;
  border-radius: 9999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.th-compose-btn-sm:hover { background: rgba(0, 200, 165, 0.2); border-color: rgba(0, 200, 165, 0.5); }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 3列网格 ────────────────────────────────────────────────────────── */
.th-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
@media (max-width: 960px) { .th-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 580px) { .th-grid { grid-template-columns: 1fr; } }

/* ── 帖子卡片 ────────────────────────────────────────────────────────── */
.th-card {
  position: relative;
  background: rgba(8, 20, 38, 0.9);
  border: 1px solid rgba(0, 180, 160, 0.1);
  border-radius: 16px;
  padding: 18px 18px 14px;
  height: 182px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
  transition: border-color 0.22s ease, transform 0.18s ease, box-shadow 0.22s ease;
  backdrop-filter: blur(4px);
}
.th-card:hover {
  border-color: rgba(0, 200, 165, 0.3);
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 200, 165, 0.08);
}

/* 悬停光晕 */
.th-card-shimmer {
  position: absolute;
  top: -50%; left: -50%;
  width: 200%; height: 200%;
  background: radial-gradient(circle at 50% 50%, rgba(0, 200, 165, 0.04) 0%, transparent 65%);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.th-card:hover .th-card-shimmer { opacity: 1; }

.th-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.th-name {
  font-size: 12px;
  font-weight: 600;
  color: #50d8c0;
  background: rgba(0, 200, 165, 0.1);
  border: 1px solid rgba(0, 200, 165, 0.18);
  padding: 3px 10px;
  border-radius: 9999px;
  letter-spacing: 0.02em;
}

.th-time {
  font-size: 11px;
  color: #2a5a78;
  font-family: 'DM Mono', monospace;
  flex-shrink: 0;
}

.th-content {
  font-size: 13.5px;
  line-height: 1.72;
  color: #7ab0cc;
  margin: 0;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  letter-spacing: 0.01em;
}

.th-card-bottom {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  flex-shrink: 0;
  margin-top: 10px;
}
.th-tags { display: flex; gap: 5px; flex-wrap: wrap; flex: 1; }

/* 标签 — 生物荧光色调 */
.th-tag {
  font-size: 11px;
  padding: 2px 9px;
  border-radius: 9999px;
  letter-spacing: 0.03em;
  font-weight: 500;
}
.tag-teal    { background: rgba(0, 212, 191, 0.1);   color: #2dd4bf; border: 1px solid rgba(0,212,191,0.18); }
.tag-emerald { background: rgba(52, 211, 153, 0.1);  color: #34d399; border: 1px solid rgba(52,211,153,0.18); }
.tag-amber   { background: rgba(251, 191, 36, 0.1);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.18); }
.tag-pink    { background: rgba(244, 114, 182, 0.1); color: #f472b6; border: 1px solid rgba(244,114,182,0.18); }
.tag-sage    { background: rgba(110, 190, 160, 0.1); color: #6ee7b7; border: 1px solid rgba(110,190,160,0.18); }
.tag-green   { background: rgba(74, 222, 128, 0.1);  color: #4ade80; border: 1px solid rgba(74,222,128,0.18); }
.tag-slate   { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.18); }

.th-delete-btn {
  background: none;
  border: 1px solid rgba(248, 113, 113, 0.22);
  color: #f87171;
  padding: 4px 9px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.15s;
  flex-shrink: 0;
}
.th-delete-btn:hover { background: rgba(248, 113, 113, 0.1); }
.th-delete-pending { font-size: 11px; color: #2a5a78; font-family: 'DM Mono', monospace; }

/* ── 弹窗遮罩 ──────────────────────────────────────────────────────── */
.th-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 14, 0.82);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 24px;
}

/* ── 漂流瓶卡片 ────────────────────────────────────────────────────── */
.th-bottle-card {
  background: #08141f;
  border: 1px solid rgba(0, 200, 165, 0.18);
  border-radius: 22px;
  padding: 30px;
  width: 100%;
  max-width: 460px;
  box-shadow:
    0 24px 60px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(0, 200, 165, 0.06),
    inset 0 1px 0 rgba(0, 200, 165, 0.08);
}

.th-bottle-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: #00c8a8;
  margin-bottom: 20px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.th-bottle-name { display: inline-block; margin-bottom: 14px; }

.th-bottle-content {
  font-size: 15px;
  line-height: 1.82;
  color: #8ac8e0;
  margin: 0 0 16px;
}

.th-bottle-tags { margin-bottom: 24px; }

.th-bottle-foot {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.th-bottle-again {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(0, 200, 165, 0.1);
  border: 1px solid rgba(0, 200, 165, 0.28);
  color: #00c8a8;
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.th-bottle-again:hover { background: rgba(0, 200, 165, 0.18); }
.th-bottle-again:disabled { opacity: 0.4; cursor: not-allowed; }

.th-bottle-close {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #5a8aaa;
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.th-bottle-close:hover { background: rgba(255, 255, 255, 0.08); color: #8ab0cc; }

/* ── 发帖弹窗 ──────────────────────────────────────────────────────── */
.th-modal {
  background: #07121e;
  border: 1px solid rgba(0, 180, 160, 0.15);
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  max-height: 92vh;
  overflow-y: auto;
  padding: 28px;
  box-shadow:
    0 28px 72px rgba(0, 0, 0, 0.65),
    0 0 0 1px rgba(0, 200, 165, 0.05),
    inset 0 1px 0 rgba(0, 200, 165, 0.07);
}
.th-modal::-webkit-scrollbar { width: 4px; }
.th-modal::-webkit-scrollbar-thumb { background: rgba(0, 200, 165, 0.2); border-radius: 2px; }

.th-modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  font-size: 15.5px;
  font-weight: 600;
  color: #c0dff0;
  letter-spacing: 0.04em;
}

.th-close-btn {
  background: none;
  border: none;
  color: #2a5a78;
  cursor: pointer;
  padding: 5px;
  display: flex;
  border-radius: 8px;
  transition: color 0.15s, background 0.15s;
}
.th-close-btn:hover { color: #50d8c0; background: rgba(0, 200, 165, 0.08); }

.th-form-group { margin-bottom: 20px; }

.th-form-label {
  font-size: 11.5px;
  color: #2a5a78;
  margin-bottom: 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 600;
}

.th-textarea {
  width: 100%;
  background: rgba(0, 10, 22, 0.6);
  border: 1px solid rgba(0, 180, 160, 0.15);
  border-radius: 10px;
  color: #a8cce0;
  font-size: 14px;
  line-height: 1.75;
  padding: 12px 14px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.18s;
  caret-color: #00c8a8;
}
.th-textarea:focus { outline: none; border-color: rgba(0, 200, 165, 0.45); box-shadow: 0 0 0 2px rgba(0, 200, 165, 0.08); }
.th-textarea::placeholder { color: #1e4060; }

.th-char-count {
  font-size: 11px;
  color: #1e4060;
  text-align: right;
  margin-top: 5px;
  font-family: 'DM Mono', monospace;
}

.th-tag-picker { display: flex; gap: 7px; flex-wrap: wrap; }

.th-tag-opt {
  border: 1px solid rgba(0, 180, 160, 0.18);
  background: transparent;
  color: #4a8aaa;
  padding: 5px 13px;
  border-radius: 9999px;
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.th-tag-opt:not(.selected):hover { border-color: rgba(0, 200, 165, 0.38); color: #80c8e0; }
.th-tag-opt.selected.tag-teal    { background: rgba(0,212,191,0.15);   border-color: #2dd4bf; color: #2dd4bf; }
.th-tag-opt.selected.tag-emerald { background: rgba(52,211,153,0.15);  border-color: #34d399; color: #34d399; }
.th-tag-opt.selected.tag-amber   { background: rgba(251,191,36,0.15);  border-color: #fbbf24; color: #fbbf24; }
.th-tag-opt.selected.tag-pink    { background: rgba(244,114,182,0.15); border-color: #f472b6; color: #f472b6; }
.th-tag-opt.selected.tag-sage    { background: rgba(110,190,160,0.15); border-color: #6ee7b7; color: #6ee7b7; }
.th-tag-opt.selected.tag-green   { background: rgba(74,222,128,0.15);  border-color: #4ade80; color: #4ade80; }
.th-tag-opt.selected.tag-slate   { background: rgba(148,163,184,0.15); border-color: #94a3b8; color: #94a3b8; }

/* 可见范围 */
.th-vis-row { display: flex; gap: 10px; }

.th-vis-opt {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(0, 10, 22, 0.4);
  border: 1px solid rgba(0, 180, 160, 0.13);
  border-radius: 10px;
  color: #4a8aaa;
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.18s;
  text-align: left;
}
.th-vis-opt:hover { border-color: rgba(0, 200, 165, 0.3); color: #80c8e0; }
.th-vis-opt.active {
  border-color: rgba(0, 200, 165, 0.45);
  background: rgba(0, 200, 165, 0.07);
  color: #c0f0e8;
}

.th-vis-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.th-vis-dot--public { background: #4ade80; box-shadow: 0 0 7px rgba(74,222,128,0.6); }
.th-vis-dot--bottle { background: #00c8a8; box-shadow: 0 0 7px rgba(0,200,165,0.6); }

.th-vis-hint { font-size: 11px; color: #1e4060; margin-left: auto; white-space: nowrap; }
.th-vis-opt.active .th-vis-hint { color: #4a8aaa; }

/* 昵称 */
.th-nickname-row { display: flex; align-items: center; gap: 8px; }

.th-select {
  flex: 1;
  background: rgba(0, 10, 22, 0.6);
  border: 1px solid rgba(0, 180, 160, 0.15);
  border-radius: 8px;
  color: #a8cce0;
  font-size: 13px;
  padding: 8px 10px;
  cursor: pointer;
  font-family: inherit;
  color-scheme: dark;
}
.th-select:focus { outline: none; border-color: rgba(0, 200, 165, 0.4); }

.th-random-btn {
  background: rgba(0, 200, 165, 0.1);
  border: 1px solid rgba(0, 200, 165, 0.22);
  color: #00c8a8;
  padding: 9px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.15s;
  flex-shrink: 0;
}
.th-random-btn:hover { background: rgba(0, 200, 165, 0.2); }

.th-nickname-preview {
  font-size: 12px;
  color: #00c8a8;
  margin-top: 9px;
  letter-spacing: 0.04em;
}

/* 提交 footer */
.th-modal-foot {
  border-top: 1px solid rgba(0, 180, 160, 0.1);
  padding-top: 20px;
  text-align: right;
}

.th-submit-error { font-size: 12.5px; color: #f87171; margin: 0 0 10px; text-align: left; }
.th-submit-ok    { font-size: 12.5px; color: #00c8a8; margin: 0 0 10px; text-align: left; }

.th-submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 200, 165, 0.16);
  color: #50e8d0;
  border: 1px solid rgba(0, 200, 165, 0.38);
  padding: 10px 26px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s;
  box-shadow: 0 0 20px rgba(0, 200, 165, 0.1);
  letter-spacing: 0.04em;
}
.th-submit-btn:hover:not(:disabled) {
  background: rgba(0, 200, 165, 0.24);
  border-color: rgba(0, 200, 165, 0.6);
  box-shadow: 0 0 28px rgba(0, 200, 165, 0.25);
}
.th-submit-btn:disabled { opacity: 0.35; cursor: not-allowed; }

/* ── 弹窗过渡 ──────────────────────────────────────────────────────── */
.th-modal-enter-active,
.th-modal-leave-active { transition: opacity 0.22s ease; }
.th-modal-enter-active .th-modal,
.th-modal-enter-active .th-bottle-card,
.th-modal-leave-active .th-modal,
.th-modal-leave-active .th-bottle-card { transition: transform 0.22s ease; }
.th-modal-enter-from,
.th-modal-leave-to { opacity: 0; }
.th-modal-enter-from .th-modal,
.th-modal-enter-from .th-bottle-card,
.th-modal-leave-to .th-modal,
.th-modal-leave-to .th-bottle-card { transform: translateY(18px); }
</style>
