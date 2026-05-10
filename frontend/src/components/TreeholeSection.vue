<template>
  <section class="treehole-section">
    <div class="inner">
      <div class="section-head">
        <div class="head-left">
          <span class="section-label">校园树洞</span>
          <h2 class="section-title">说出你的心声</h2>
          <p class="section-sub">匿名发声，温暖同行。这里有人在听。</p>
        </div>
        <router-link to="/treehouse" class="enter-btn">
          进入树洞
          <ArrowRight :size="14" :stroke-width="2.5" />
        </router-link>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="preview-loading">
        <Loader2 :size="20" :stroke-width="1.5" class="spin" />
      </div>

      <!-- 帖子预览 -->
      <div v-else class="holes-grid">
        <div v-for="hole in posts" :key="hole.id" class="hole-card">
          <p class="hole-content">{{ hole.content }}</p>
          <div class="hole-footer">
            <span v-for="tag in hole.tags" :key="tag" class="hole-tag">{{ tag }}</span>
            <span class="hole-name">{{ hole.anonymous_name }}</span>
          </div>
        </div>
        <div v-if="posts.length === 0" class="hole-empty">暂无内容，快来说点什么吧</div>
      </div>

      <p class="privacy-note">
        <Lock :size="12" :stroke-width="1.5" />
        所有内容匿名发布，经审核后可见，中心老师会关注每一条留言。
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Lock, Loader2, ArrowRight } from 'lucide-vue-next'
import { getPosts } from '@/api/treehole'

const posts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const all = await getPosts()
    posts.value = all.slice(0, 3)
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.treehole-section {
  background: linear-gradient(135deg, #2d5a42 0%, #3a6b50 50%, #4a8763 100%);
  padding: var(--sp-16) 0;
  position: relative;
  overflow: hidden;
}

.treehole-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 100%, rgba(255,255,255,0.04) 0%, transparent 70%);
  pointer-events: none;
}

.inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
  position: relative;
  z-index: 1;
}

/* 章节头 */
.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: var(--sp-8);
}

.head-left {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.section-label {
  display: inline-block;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.22);
  color: rgba(255,255,255,0.9);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: var(--r-pill);
  letter-spacing: 2px;
  text-transform: uppercase;
  align-self: flex-start;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  color: white;
  font-family: var(--f-serif);
  letter-spacing: 2px;
  margin: 0;
  text-shadow: 0 2px 12px rgba(0,0,0,0.15);
}

.section-sub {
  font-size: 14px;
  color: rgba(255,255,255,0.65);
  margin: 0;
}

.enter-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  background: white;
  color: var(--c-green-deep);
  padding: 11px 22px;
  border-radius: var(--r-sm);
  font-size: 13.5px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  transition: transform var(--t-base), box-shadow var(--t-base);
  flex-shrink: 0;
  letter-spacing: 0.3px;
}
.enter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0,0,0,0.25);
}

/* 加载 */
.preview-loading {
  display: flex;
  justify-content: center;
  padding: var(--sp-10) 0;
  color: rgba(255,255,255,0.5);
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 帖子网格 */
.holes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--sp-4);
  margin-bottom: var(--sp-6);
}

.hole-card {
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.16);
  border-radius: var(--r-xl);
  padding: var(--sp-5);
  transition: background var(--t-base), transform var(--t-base), border-color var(--t-base);
}
.hole-card:hover {
  background: rgba(255,255,255,0.14);
  transform: translateY(-3px);
  border-color: rgba(255,255,255,0.28);
}

.hole-content {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255,255,255,0.88);
  margin: 0 0 var(--sp-4);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hole-footer {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  flex-wrap: wrap;
}

.hole-tag {
  background: rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.82);
  padding: 2px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: var(--r-pill);
  border: 1px solid rgba(255,255,255,0.12);
}

.hole-name {
  margin-left: auto;
  font-size: 11.5px;
  color: rgba(255,255,255,0.4);
}

.hole-empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: var(--sp-10);
  color: rgba(255,255,255,0.4);
  font-size: 14px;
}

/* 隐私提示 */
.privacy-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-1);
  font-size: 12px;
  color: rgba(255,255,255,0.45);
  margin: 0;
}
</style>
