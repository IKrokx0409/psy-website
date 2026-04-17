<template>
  <div class="rd-page">

    <div v-if="loading" class="rd-state">
      <Loader2 :size="28" :stroke-width="1.5" class="spin" /><span>加载中…</span>
    </div>

    <div v-else-if="error" class="rd-state rd-error">
      <AlertCircle :size="24" /><span>{{ errorMsg }}</span>
      <router-link to="/science" class="back-btn">← 返回心理资源</router-link>
    </div>

    <template v-else>
      <!-- 页头 -->
      <div class="rd-header">
        <div class="rd-header-inner">
          <router-link to="/science" class="back-link">
            <ChevronLeft :size="15" :stroke-width="2" /> 心理资源
          </router-link>
          <div class="rd-meta">
            <span class="rd-cat">{{ resource.category }}</span>
            <span class="rd-sep">·</span>
            <span class="rd-date">{{ fmtDate(resource.created_at) }}</span>
          </div>
          <h1 class="rd-title">{{ resource.title }}</h1>
        </div>
      </div>

      <!-- 正文 -->
      <div class="rd-body">
        <div class="rd-inner">
          <div v-if="resource.content" class="rd-markdown" v-html="renderMd(resource.content)"></div>
          <div v-else class="rd-no-content">
            <FileText :size="36" :stroke-width="1" style="opacity:.3" /><span>暂无正文内容</span>
          </div>
          <div class="rd-footer">
            <router-link to="/science" class="back-btn">
              <ChevronLeft :size="14" :stroke-width="2" /> 返回心理资源
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronLeft, Loader2, AlertCircle, FileText } from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'
import { getResource } from '@/api/resources'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
const renderMd = (src) => md.render(src || '')

const route    = useRoute()
const resource = ref(null)
const loading  = ref(true)
const error    = ref(false)
const errorMsg = ref('加载失败')

const fmtDate = (iso) => iso ? new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) : ''

onMounted(async () => {
  try {
    resource.value = await getResource(route.params.id)
  } catch (e) {
    error.value = true
    if (e?.response?.status === 404) errorMsg.value = '文章不存在'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.rd-page { min-height: 100%; background: #f5f4f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

.rd-state { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 120px 24px; color: #94a3b8; font-size: 14px; }
.rd-error { color: #b91c1c; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.rd-header {
  background: linear-gradient(160deg, #5f9e75 0%, #4d8764 100%);
  padding: 56px 32px 52px;
  border-bottom: 3px solid rgba(255,255,255,0.2);
  box-shadow: 0 2px 6px rgba(30,100,60,0.3);
}
.rd-header-inner { max-width: 860px; margin: 0 auto; }
.back-link { display: inline-flex; align-items: center; gap: 4px; color: rgba(255,255,255,0.6); text-decoration: none; font-size: 13px; margin-bottom: 28px; transition: color 0.15s; }
.back-link:hover { color: rgba(255,255,255,0.9); }
.rd-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.rd-cat  { font-size: 12px; color: rgba(255,255,255,0.75); letter-spacing: 1px; font-weight: 500; }
.rd-sep  { color: rgba(255,255,255,0.3); font-size: 12px; }
.rd-date { font-size: 12px; color: rgba(255,255,255,0.5); }
.rd-title { font-family: 'SimSun','宋体','STSong',Georgia,serif; font-size: 28px; font-weight: 700; color: #f5efe0; margin: 0; line-height: 1.6; letter-spacing: 1px; }

.rd-body { padding: 48px 32px 80px; }
.rd-inner { max-width: 860px; margin: 0 auto; background: white; border: 1px solid #d8d2c8; padding: 48px 60px; }

.rd-markdown { color: #2a241a; font-size: 15.5px; line-height: 2; font-family: 'SimSun','宋体','STSong',Georgia,serif; }
.rd-markdown :deep(h1),.rd-markdown :deep(h2),.rd-markdown :deep(h3) { font-family: 'SimSun','宋体',Georgia,serif; font-weight: 700; color: #1a1208; margin: 2em 0 0.75em; line-height: 1.5; }
.rd-markdown :deep(h2) { font-size: 18px; padding-bottom: 10px; border-bottom: 1px solid #d8d2c8; }
.rd-markdown :deep(p) { margin: 0 0 1.2em; }
.rd-markdown :deep(ul),.rd-markdown :deep(ol) { padding-left: 2em; margin: 0 0 1.2em; }
.rd-markdown :deep(blockquote) { border-left: 3px solid #5f9e75; margin: 0 0 1.2em; padding: 12px 20px; background: #f5fbf7; color: #4d6b56; font-style: italic; }
.rd-markdown :deep(a) { color: #5f9e75; text-decoration: underline; text-underline-offset: 2px; }
.rd-markdown :deep(hr) { border: none; border-top: 1px solid #d8d2c8; margin: 2em 0; }
.rd-markdown :deep(img) { max-width: 100%; border-radius: 2px; margin: 12px 0; display: block; }

.rd-no-content { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 0; color: #94a3b8; font-size: 14px; }

.rd-footer { margin-top: 48px; padding-top: 28px; border-top: 1px solid #d8d2c8; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; background: #f0ece4; border: 1px solid #d0c9bc; color: #3a3020; padding: 10px 22px; border-radius: 2px; text-decoration: none; font-size: 13.5px; font-weight: 500; transition: background 0.15s; }
.back-btn:hover { background: #e4ddd0; }

@media (max-width: 640px) {
  .rd-header { padding: 40px 20px 36px; }
  .rd-title { font-size: 22px; }
  .rd-body { padding: 24px 16px 60px; }
  .rd-inner { padding: 28px 20px; }
}
</style>
