<template>
  <div class="ann-detail-page">

    <div v-if="loading" class="ann-detail-state">
      <Loader2 :size="28" :stroke-width="1.5" class="spin" />
      <span>加载中…</span>
    </div>

    <div v-else-if="error" class="ann-detail-state ann-detail-error">
      <AlertCircle :size="24" :stroke-width="1.5" />
      <span>{{ errorMsg }}</span>
      <router-link to="/announcements" class="back-btn">← 返回公告列表</router-link>
    </div>

    <template v-else>

      <!-- 页头（封面背景） -->
      <div class="ann-detail-header" :style="headerStyle">
        <div class="ann-detail-header-inner">
          <router-link to="/announcements" class="back-link">
            <ChevronLeft :size="15" :stroke-width="2" /> 通知公告
          </router-link>
          <div class="ann-detail-meta">
            <span class="ann-detail-cat">{{ ann.category }}</span>
            <span class="ann-detail-sep">·</span>
            <span class="ann-detail-date">{{ ann.published_at }}</span>
          </div>
          <h1 class="ann-detail-title">{{ ann.title }}</h1>
        </div>
      </div>

      <!-- 正文 -->
      <div class="ann-detail-body">
        <div class="ann-detail-inner">

          <!-- Markdown 正文 -->
          <div
            v-if="ann.body"
            class="ann-markdown"
            v-html="renderMd(ann.body)"
          ></div>

          <!-- 无正文兜底 -->
          <div v-else class="ann-no-body">
            <FileText :size="36" :stroke-width="1" style="opacity:.3" />
            <span>暂无正文内容</span>
          </div>

          <!-- 底部导航 -->
          <div class="ann-detail-footer">
            <router-link to="/announcements" class="back-btn">
              <ChevronLeft :size="14" :stroke-width="2" /> 返回公告列表
            </router-link>
          </div>

        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronLeft, Loader2, AlertCircle, FileText } from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'
import { getAnnouncement } from '@/api/announcements'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
const renderMd = (src) => md.render(src || '')

const route    = useRoute()
const ann      = ref(null)
const loading  = ref(true)
const error    = ref(false)
const errorMsg = ref('加载失败')

onMounted(async () => {
  try {
    ann.value = await getAnnouncement(route.params.id)
  } catch (e) {
    error.value = true
    if (e?.response?.status === 404) errorMsg.value = '公告不存在或已下线'
  } finally {
    loading.value = false
  }
})

const headerStyle = computed(() => {
  if (ann.value?.cover_image) {
    return {
      backgroundImage: `linear-gradient(rgba(61,120,90,0.75), rgba(55,105,80,0.85)), url(${ann.value.cover_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }
  }
  return {}
})
</script>

<style scoped>
.ann-detail-page {
  min-height: 100%;
  background: var(--c-beige);
  font-family: var(--f-sans);
}

/* ── 加载 / 错误状态 ─────────────────────────────────────────────── */
.ann-detail-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 120px 24px;
  color: #94a3b8;
  font-size: 14px;
}
.ann-detail-error { color: #b91c1c; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 页头 ────────────────────────────────────────────────────────── */
.ann-detail-header {
  padding: 56px 32px 52px;
  border-bottom: 3px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 6px rgba(30, 100, 60, 0.3);
  /* 无封面图时直接用导航栏色 */
  background: linear-gradient(160deg, #5f9e75 0%, #4d8764 100%);
  background-size: cover;
  background-position: center;
}
.ann-detail-header-inner {
  max-width: 860px;
  margin: 0 auto;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 13px;
  margin-bottom: 28px;
  letter-spacing: 0.3px;
  transition: color 0.15s;
}
.back-link:hover { color: rgba(255, 255, 255, 0.9); }

.ann-detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.ann-detail-cat {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  letter-spacing: 1px;
  font-weight: 500;
}
.ann-detail-sep {
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
}
.ann-detail-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.5px;
}

.ann-detail-title {
  font-family: 'SimSun', '宋体', 'STSong', 'NSimSun', Georgia, serif;
  font-size: 28px;
  font-weight: 700;
  color: #f5efe0;
  margin: 0;
  line-height: 1.6;
  letter-spacing: 1px;
}

/* ── 正文区域 ────────────────────────────────────────────────────── */
.ann-detail-body {
  padding: 48px 32px 80px;
}
.ann-detail-inner {
  max-width: 860px;
  margin: 0 auto;
  background: white;
  border: 1px solid #d8d2c8;
  border-radius: var(--r-xl);
  padding: 48px 60px;
  box-shadow: var(--shadow-sm);
}

/* ── Markdown 渲染样式 ───────────────────────────────────────────── */
.ann-markdown {
  color: #2a241a;
  font-size: 15.5px;
  line-height: 2;
  font-family: 'SimSun', '宋体', 'STSong', Georgia, serif;
}

.ann-markdown :deep(h1),
.ann-markdown :deep(h2),
.ann-markdown :deep(h3) {
  font-family: 'SimSun', '宋体', 'STSong', Georgia, serif;
  font-weight: 700;
  color: #1a1208;
  margin: 2em 0 0.75em;
  line-height: 1.5;
}
.ann-markdown :deep(h1) { font-size: 22px; }
.ann-markdown :deep(h2) {
  font-size: 18px;
  padding-bottom: 10px;
  border-bottom: 1px solid #d8d2c8;
}
.ann-markdown :deep(h3) { font-size: 16px; }

.ann-markdown :deep(p) { margin: 0 0 1.2em; }

.ann-markdown :deep(ul),
.ann-markdown :deep(ol) {
  padding-left: 2em;
  margin: 0 0 1.2em;
}
.ann-markdown :deep(li) { margin-bottom: 0.5em; }

.ann-markdown :deep(strong) { color: #1a1208; font-weight: 700; }
.ann-markdown :deep(em) { color: #5a4a30; }

.ann-markdown :deep(a) {
  color: #5f9e75;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.ann-markdown :deep(a:hover) { color: #5f9e75; }

.ann-markdown :deep(blockquote) {
  border-left: 3px solid #c8a96e;
  margin: 0 0 1.2em;
  padding: 12px 20px;
  background: #faf8f4;
  color: #5a4a30;
  font-style: italic;
}

.ann-markdown :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 1.2em;
  font-size: 14px;
}
.ann-markdown :deep(th) {
  background: #f0ece4;
  padding: 10px 16px;
  text-align: left;
  font-weight: 600;
  color: #2a241a;
  border: 1px solid #d8d2c8;
}
.ann-markdown :deep(td) {
  padding: 10px 16px;
  border: 1px solid #e0dbd0;
  color: #3a3020;
}
.ann-markdown :deep(tr:nth-child(even) td) { background: #faf8f4; }

.ann-markdown :deep(code) {
  background: #f0ece4;
  padding: 2px 6px;
  border-radius: 2px;
  font-size: 13.5px;
  font-family: monospace;
  color: #5a3010;
}
.ann-markdown :deep(pre) {
  background: #2a241a;
  padding: 16px 20px;
  border-radius: 2px;
  overflow-x: auto;
  margin: 0 0 1.2em;
}
.ann-markdown :deep(pre code) {
  background: none;
  color: #e8e0d0;
  padding: 0;
}

.ann-markdown :deep(hr) {
  border: none;
  border-top: 1px solid #d8d2c8;
  margin: 2em 0;
}

.ann-markdown :deep(img) {
  max-width: 100%;
  border-radius: 2px;
  margin: 12px 0;
  display: block;
}

/* ── 无正文兜底 ──────────────────────────────────────────────────── */
.ann-no-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: #94a3b8;
  font-size: 14px;
}

/* ── 底部导航 ────────────────────────────────────────────────────── */
.ann-detail-footer {
  margin-top: 48px;
  padding-top: 28px;
  border-top: 1px solid #d8d2c8;
}
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--c-beige);
  border: 1px solid var(--c-beige-border);
  color: var(--c-text-body);
  padding: 10px 22px;
  border-radius: var(--r-sm);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: background var(--t-base), border-color var(--t-base);
}
.back-btn:hover {
  background: #eee8de;
  border-color: #c8b89a;
}

/* ── 响应式 ──────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .ann-detail-header { padding: 40px 20px 36px; }
  .ann-detail-title { font-size: 22px; }
  .ann-detail-body { padding: 24px 16px 60px; }
  .ann-detail-inner { padding: 28px 20px; }
}
</style>
