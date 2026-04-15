<template>
  <div class="announcement-board">
    <div class="board-header">
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          :class="['tab', { active: activeTab === tab }]"
          @click="activeTab = tab"
        >{{ tab }}</button>
      </div>
      <a href="#" class="more-link">查看全部 →</a>
    </div>

    <div v-if="loading" class="state-row">
      <Loader2 :size="16" :stroke-width="1.5" class="spin" /> 加载中…
    </div>
    <div v-else-if="error" class="state-row state-error">
      <AlertCircle :size="15" :stroke-width="1.5" /> 加载失败，请检查后端服务
    </div>
    <ul v-else class="news-list">
      <li v-for="item in currentList" :key="item.id" class="news-item">
        <span class="news-dot"></span>
        <a href="#" class="news-title">{{ item.title }}</a>
        <span class="news-date">{{ item.published_at }}</span>
      </li>
      <li v-if="currentList.length === 0" class="news-empty">暂无相关公告</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Loader2, AlertCircle } from 'lucide-vue-next'
import { getAnnouncements } from '@/api/announcements'

const tabs = ['中心公告', '活动预告', '心理讲座']
const activeTab = ref('中心公告')
const allData = ref([])
const loading = ref(true)
const error = ref(false)

onMounted(async () => {
  try {
    allData.value = await getAnnouncements()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})

const currentList = computed(() =>
  allData.value.filter(item => item.category === activeTab.value)
)
</script>

<style scoped>
.announcement-board { background: white; border: 1px solid #cfe8da; overflow: hidden; }

.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 2px solid #cfe8da;
  background: #f5fbf7;
}

.tabs { display: flex; }
.tab {
  padding: 14px 18px;
  background: none;
  border: none;
  font-size: 14px;
  color: #5a7099;
  cursor: pointer;
  font-weight: 500;
  position: relative;
  transition: color 0.15s;
}
.tab::after {
  content: '';
  position: absolute;
  bottom: -2px; left: 0; right: 0;
  height: 2px;
  background: #5f9e75;
  transform: scaleX(0);
  transition: transform 0.2s;
}
.tab:hover { color: #5f9e75; }
.tab.active { color: #5f9e75; font-weight: 600; }
.tab.active::after { transform: scaleX(1); }

.more-link { font-size: 12.5px; color: #5f9e75; text-decoration: none; }
.more-link:hover { text-decoration: underline; }

.state-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 28px 20px;
  font-size: 13px;
  color: #94a3b8;
}
.state-error { color: #e53e3e; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.news-list { list-style: none; margin: 0; padding: 8px 0; }
.news-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-bottom: 1px dashed #f0f4fb;
  transition: background 0.12s;
}
.news-item:last-child { border-bottom: none; }
.news-item:hover { background: #edf7f2; }
.news-dot { width: 6px; height: 6px; border-radius: 50%; background: #5f9e75; flex-shrink: 0; }
.news-title {
  flex: 1;
  font-size: 13.5px;
  color: #1e293b;
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.12s;
}
.news-title:hover { color: #5f9e75; }
.news-date { font-size: 12px; color: #94a3b8; white-space: nowrap; flex-shrink: 0; }
.news-empty { padding: 20px; font-size: 13px; color: #94a3b8; text-align: center; }
</style>
