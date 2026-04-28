<template>
  <section class="treehole-section">
    <div class="inner">
      <div class="section-head">
        <div class="head-left">
          <h2 class="section-title"><MessageCircle :size="22" :stroke-width="1.5" /> 树洞 · 说出你的心声</h2>
          <p class="section-sub">匿名发声，温暖同行。这里有人在听。</p>
        </div>
        <router-link to="/treehouse" class="enter-btn">进入树洞 →</router-link>
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

      <p class="privacy-note"><Lock :size="12" :stroke-width="1.5" /> 所有内容匿名发布，经审核后可见，中心老师会关注每一条留言。</p>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MessageCircle, Lock, Loader2 } from 'lucide-vue-next'
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
  background: linear-gradient(135deg, #2d5a42 0%, #3d6e52 60%, #4a8763 100%);
  padding: 56px 0;
}
.inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
}
.head-left { flex: 1; }
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px;
}
.section-sub { font-size: 14px; color: rgba(255,255,255,0.7); margin: 0; }

.enter-btn {
  display: inline-block;
  background: white;
  color: #5f9e75;
  padding: 10px 24px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  transition: transform 0.15s, box-shadow 0.15s;
}
.enter-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,0.2); }

.preview-loading {
  display: flex;
  justify-content: center;
  padding: 40px 0;
  color: rgba(255,255,255,0.6);
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.holes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.hole-card {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.2);
  padding: 20px;
  transition: background 0.15s, transform 0.15s;
}
.hole-card:hover { background: rgba(255,255,255,0.18); transform: translateY(-2px); }
.hole-content { font-size: 14px; line-height: 1.75; color: rgba(255,255,255,0.92); margin: 0 0 14px; }
.hole-footer { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.hole-tag {
  background: rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.88);
  padding: 2px 10px;
  font-size: 11.5px;
}
.hole-name { margin-left: auto; font-size: 12px; color: rgba(255,255,255,0.5); }
.hole-empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: rgba(255,255,255,0.5);
  font-size: 14px;
}

.privacy-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  text-align: center;
  font-size: 12.5px;
  color: rgba(255,255,255,0.55);
  margin: 0;
}
</style>
