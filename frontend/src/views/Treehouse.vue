<template>
  <div class="th-page">

    <!-- ══ 页头（含弹幕背景）══════════════════════════════════════════ -->
    <header class="th-header">

      <!-- 导航栏渐变遮罩 -->
      <div class="th-nav-blend"></div>

      <!-- 弹幕层（散落，绝对定位，pointer-events:none） -->
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
        <TreePine :size="40" :stroke-width="1" class="th-header-icon" />
        <h1 class="th-title">校园树洞</h1>
        <p class="th-subtitle">说出你的故事，这里有人在听<br>每一条心声都会被温柔对待</p>
        <div class="th-header-actions">
          <button class="th-bottle-trigger" @click="fetchBottle" :disabled="posts.length === 0">
            <Waves :size="15" :stroke-width="1.5" /> 捞一条漂流瓶
          </button>
          <button class="th-compose-btn" @click="showCompose = true">
            <PenLine :size="15" :stroke-width="1.5" /> 说点什么
          </button>
        </div>
      </div>

    </header>

    <!-- ══ 帖子列表 ═══════════════════════════════════════════════════ -->
    <main class="th-feed-wrap">
      <div class="th-feed-inner">

        <div class="th-meta" v-if="!loading && !error">
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
          <MessageCircle :size="40" :stroke-width="1" style="opacity:0.3" />
          <span>这里还没有心声，来说第一句话吧</span>
          <button class="th-compose-btn-sm" @click="showCompose = true">立即发布</button>
        </div>

        <div v-else class="th-grid">
          <article
            v-for="post in posts"
            :key="post.id"
            class="th-card"
          >
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
                <Trash2 :size="13" :stroke-width="1.5" />
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
            <Waves :size="18" :stroke-width="1.5" />
            <span>你捞到了一条漂流瓶</span>
          </div>
          <span class="th-name th-bottle-name">{{ bottle.anonymous_name }}</span>
          <p class="th-bottle-content">{{ bottle.content }}</p>
          <div class="th-tags th-bottle-tags">
            <span v-for="tag in bottle.tags" :key="tag" :class="['th-tag', tagClass(tag)]">
              {{ tag }}
            </span>
          </div>
          <div class="th-bottle-foot">
            <button class="th-bottle-again" @click="fetchBottle">
              <Shuffle :size="13" :stroke-width="1.5" /> 再捞一条
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
            <p v-if="submitSuccess" class="th-submit-ok">已提交！通过审核后将公开显示。</p>
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
import { getPosts, createPost, requestDelete, getMyToken } from '@/api/treehole'

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
  // 上下两个水平带各 7 条，共 14 条，等间距保证不重叠
  // 上带：3% ~ 30%，下带：70% ~ 97%，步长 4.5%
  const PER_BAND = 7
  const STEP = 4.5
  const pills = []
  for (let b = 0; b < 2; b++) {
    const base = b === 0 ? 3 : 70
    for (let j = 0; j < PER_BAND; j++) {
      const i = b * PER_BAND + j
      const top = base + j * STEP
      // 速度差异化：上带稍快，下带稍慢，同带内各自不同
      const duration = 28 + (i * 4.1) % 28   // 28s – 56s
      const delay    = -((i * 8.3) % duration) // 各自错位，不同步
      const opacity  = 0.13 + (j % 4) * 0.025 // 0.13 – 0.205
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
const bottle = ref(null)

const fetchBottle = () => {
  if (!posts.value.length) return
  const pool = posts.value.filter(p => bottle.value ? p.id !== bottle.value.id : true)
  const src = pool.length ? pool : posts.value
  bottle.value = src[Math.floor(Math.random() * src.length)]
}

// ── 发帖表单 ─────────────────────────────────────────────────────────
const showCompose = ref(false)
const submitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

const randItem = (arr) => arr[Math.floor(Math.random() * arr.length)]

const form = reactive({
  content: '',
  tags: [],
  adjective: randItem(ADJECTIVES),
  noun: randItem(NOUNS),
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
    await createPost({
      anonymous_name: form.adjective + form.noun,
      content: form.content.trim(),
      tags: form.tags,
    })
    submitSuccess.value = true
    form.content = ''
    form.tags = []
    form.adjective = randItem(ADJECTIVES)
    form.noun = randItem(NOUNS)
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
/* ── 基底 ────────────────────────────────────────────────────────────── */
.th-page {
  min-height: 100%;
  background: #0a1525;
  color: #d0e8f8;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── 页头 ────────────────────────────────────────────────────────────── */
.th-header {
  position: relative;
  overflow: hidden;
  padding: 80px 24px 72px;
  text-align: center;
  background: #0e1e35;
}

/* 导航栏渐变遮罩：从 #3d78b5 淡出，平滑衔接 */
.th-nav-blend {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 80px;
  background: linear-gradient(to bottom, #1c3358 0%, transparent 100%);
  pointer-events: none;
  z-index: 2;
}

/* ── 散落弹幕 ─────────────────────────────────────────────────────────── */
.th-danmaku {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  /* 不加 overflow:hidden：让 header 本身的 overflow:hidden 做裁剪，
     避免双重裁剪导致 pill 在容器内部被提前截断 */
}

.th-danmaku-pill {
  position: absolute;
  left: 0;           /* 明确锚定基准 x=0，translateX 参考值可靠 */
  background: rgba(91, 159, 212, 0.07);
  border: 1px solid rgba(91, 159, 212, 0.10);
  color: rgba(208, 232, 248, 0.55);
  padding: 5px 16px;
  border-radius: 20px;
  font-size: 12.5px;
  white-space: nowrap;
  animation: danmaku-float linear infinite;
  will-change: transform;
}

@keyframes danmaku-float {
  from { transform: translateX(110vw); }
  to   { transform: translateX(-110vw); }  /* 确保完全飘出左侧后才循环 */
}

/* ── 页头内容 ─────────────────────────────────────────────────────────── */
.th-header-content {
  position: relative;
  z-index: 3;
}
.th-header-icon { color: #7cc4f0; margin-bottom: 16px; }
.th-title {
  font-size: 34px;
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: 2px;
  color: #e0f0fb;
}
.th-subtitle {
  font-size: 15px;
  color: #7ab0d8;
  line-height: 1.8;
  margin: 0 0 32px;
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
  color: #38c2ff;
  border: 1.5px solid #38c2ff;
  padding: 11px 24px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s, box-shadow 0.2s;
  box-shadow: 0 0 10px rgba(56, 194, 255, 0.25);
}
.th-bottle-trigger:hover {
  border-color: #7adaff;
  color: #7adaff;
  box-shadow: 0 0 18px rgba(56, 194, 255, 0.45);
}
.th-bottle-trigger:disabled { opacity: 0.35; cursor: not-allowed; box-shadow: none; }

.th-compose-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #3d78b5;
  color: white;
  border: none;
  padding: 11px 28px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  box-shadow: 0 4px 20px rgba(61, 120, 181, 0.4);
}
.th-compose-btn:hover { background: #2e6aa0; transform: translateY(-1px); }

/* ── 页头底部向 Feed 过渡 ────────────────────────────────────────────── */
.th-header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 72px;
  background: linear-gradient(to bottom, transparent 0%, #0a1525 100%);
  pointer-events: none;
  z-index: 4;
}

/* ── Feed ────────────────────────────────────────────────────────────── */
.th-feed-wrap { padding: 40px 24px 64px; }
.th-feed-inner { max-width: 1100px; margin: 0 auto; }
.th-meta { font-size: 12.5px; color: #3d6898; margin-bottom: 20px; }

.th-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 0;
  color: #3d6898;
  font-size: 14px;
}
.th-state-error { color: #f87171; }
.th-compose-btn-sm {
  background: #3d78b5;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.th-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

/* ── 帖子卡片（固定高度，内容超出截断） ──────────────────────────────── */
.th-card {
  background: #132035;
  border: 1px solid rgba(91, 159, 212, 0.1);
  border-radius: 16px;
  padding: 20px;
  height: 190px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  transition: border-color 0.2s, transform 0.15s;
}
.th-card:hover {
  border-color: rgba(91, 159, 212, 0.28);
  transform: translateY(-2px);
}
.th-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  flex-shrink: 0;
}
.th-name {
  font-size: 13px;
  font-weight: 600;
  color: #7cc4f0;
  background: rgba(91, 159, 212, 0.1);
  padding: 3px 12px;
  border-radius: 20px;
}
.th-time { font-size: 12px; color: #3d6898; }
.th-content {
  font-size: 14px;
  line-height: 1.75;
  color: #a8c8e8;
  margin: 0;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}
.th-card-bottom { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; flex-shrink: 0; margin-top: 10px; }
.th-tags { display: flex; gap: 6px; flex-wrap: wrap; flex: 1; }

/* 标签颜色 */
.th-tag { font-size: 11.5px; padding: 3px 10px; border-radius: 20px; }
.tag-teal    { background: rgba(45,212,191,0.12);  color: #5eead4; }
.tag-emerald { background: rgba(52,211,153,0.12);  color: #6ee7b7; }
.tag-amber   { background: rgba(251,191,36,0.12);  color: #fcd34d; }
.tag-pink    { background: rgba(244,114,182,0.12); color: #f9a8d4; }
.tag-sage    { background: rgba(109,184,138,0.12); color: #9ddcb8; }
.tag-green   { background: rgba(134,239,172,0.12); color: #86efac; }
.tag-slate   { background: rgba(148,163,184,0.12); color: #94a3b8; }

.th-delete-btn {
  background: none;
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  padding: 4px 10px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.15s;
}
.th-delete-btn:hover { background: rgba(248, 113, 113, 0.1); }
.th-delete-pending { font-size: 11.5px; color: #3d6898; }

/* ── 弹窗通用遮罩 ─────────────────────────────────────────────────────── */
.th-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 24px;
}

/* ── 漂流瓶卡片 ───────────────────────────────────────────────────────── */
.th-bottle-card {
  background: #0e1e35;
  border: 1px solid rgba(128, 190, 240, 0.22);
  border-radius: 24px;
  padding: 32px;
  width: 100%;
  max-width: 460px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5), 0 0 40px rgba(128, 190, 240, 0.06);
}
.th-bottle-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #80bef0;
  margin-bottom: 20px;
  font-weight: 500;
}
.th-bottle-name { display: inline-block; margin-bottom: 14px; }
.th-bottle-content {
  font-size: 15px;
  line-height: 1.8;
  color: #b8d8f0;
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
  background: rgba(128, 190, 240, 0.1);
  border: 1px solid rgba(128, 190, 240, 0.32);
  color: #80bef0;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}
.th-bottle-again:hover { background: rgba(128, 190, 240, 0.18); }
.th-bottle-close {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: #7ab0d8;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}
.th-bottle-close:hover { background: rgba(148, 163, 184, 0.15); }

/* ── 发帖弹窗 ─────────────────────────────────────────────────────────── */
.th-modal {
  background: #0f1e35;
  border: 1px solid rgba(91, 159, 212, 0.15);
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 28px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
}
.th-modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  font-size: 16px;
  font-weight: 600;
  color: #e0f0fb;
}
.th-close-btn {
  background: none;
  border: none;
  color: #4a7aaa;
  cursor: pointer;
  padding: 4px;
  display: flex;
  border-radius: 8px;
  transition: color 0.15s, background 0.15s;
}
.th-close-btn:hover { color: #e0f0fb; background: rgba(91,159,212,0.1); }

.th-form-group { margin-bottom: 20px; }
.th-form-label { font-size: 12.5px; color: #4a7aaa; margin-bottom: 8px; }

.th-textarea {
  width: 100%;
  background: #0a1525;
  border: 1px solid rgba(91, 159, 212, 0.15);
  border-radius: 12px;
  color: #d0e8f8;
  font-size: 14px;
  line-height: 1.7;
  padding: 12px 14px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.th-textarea:focus { outline: none; border-color: #7cc4f0; }
.th-textarea::placeholder { color: #3d6898; }
.th-char-count { font-size: 11.5px; color: #3d6898; text-align: right; margin-top: 4px; }

.th-tag-picker { display: flex; gap: 8px; flex-wrap: wrap; }
.th-tag-opt {
  border: 1px solid rgba(91, 159, 212, 0.18);
  background: transparent;
  color: #7ab0d8;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.15s;
}
.th-tag-opt:not(.selected):hover { border-color: #4a7aaa; color: #d0e8f8; }
.th-tag-opt.selected.tag-teal    { background: rgba(45,212,191,0.18);   border-color: #2dd4bf; color: #5eead4; }
.th-tag-opt.selected.tag-emerald { background: rgba(52,211,153,0.18);   border-color: #34d399; color: #6ee7b7; }
.th-tag-opt.selected.tag-amber   { background: rgba(251,191,36,0.18);   border-color: #fbbf24; color: #fcd34d; }
.th-tag-opt.selected.tag-pink    { background: rgba(244,114,182,0.18);  border-color: #f472b6; color: #f9a8d4; }
.th-tag-opt.selected.tag-sage    { background: rgba(91,159,212,0.18);  border-color: #7cc4f0; color: #9ddcb8; }
.th-tag-opt.selected.tag-green   { background: rgba(134,239,172,0.18);  border-color: #4ade80; color: #86efac; }
.th-tag-opt.selected.tag-slate   { background: rgba(148,163,184,0.18);  border-color: #94a3b8; color: #cbd5e1; }

.th-nickname-row { display: flex; align-items: center; gap: 8px; }
.th-select {
  flex: 1;
  background: #0a1525;
  border: 1px solid rgba(91, 159, 212, 0.15);
  border-radius: 10px;
  color: #d0e8f8;
  font-size: 13.5px;
  padding: 8px 10px;
  cursor: pointer;
}
.th-select:focus { outline: none; border-color: #7cc4f0; }
.th-random-btn {
  background: rgba(91, 159, 212, 0.12);
  border: 1px solid rgba(91, 159, 212, 0.25);
  color: #7cc4f0;
  padding: 9px 12px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.15s;
}
.th-random-btn:hover { background: rgba(91, 159, 212, 0.22); }
.th-nickname-preview { font-size: 12.5px; color: #7cc4f0; margin-top: 8px; }

.th-modal-foot {
  border-top: 1px solid rgba(91, 159, 212, 0.1);
  padding-top: 20px;
  text-align: right;
}
.th-submit-error { font-size: 12.5px; color: #f87171; margin: 0 0 10px; text-align: left; }
.th-submit-ok    { font-size: 12.5px; color: #7cc4f0; margin: 0 0 10px; text-align: left; }

.th-submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #3d78b5;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 4px 16px rgba(61, 120, 181, 0.35);
}
.th-submit-btn:hover:not(:disabled) { background: #2e6aa0; }
.th-submit-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* ── 弹窗过渡 ─────────────────────────────────────────────────────────── */
.th-modal-enter-active,
.th-modal-leave-active { transition: opacity 0.2s ease; }
.th-modal-enter-active .th-modal,
.th-modal-enter-active .th-bottle-card,
.th-modal-leave-active .th-modal,
.th-modal-leave-active .th-bottle-card { transition: transform 0.2s ease; }
.th-modal-enter-from,
.th-modal-leave-to { opacity: 0; }
.th-modal-enter-from .th-modal,
.th-modal-enter-from .th-bottle-card,
.th-modal-leave-to .th-modal,
.th-modal-leave-to .th-bottle-card { transform: translateY(16px); }
</style>
