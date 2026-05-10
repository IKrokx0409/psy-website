<template>
  <div class="announcement-board">
    <!-- 板块标题 -->
    <div class="board-section-header">
      <span class="section-label">动态</span>
      <h2 class="section-title">中心公告与活动</h2>
    </div>

    <!-- Tab + 更多链接 -->
    <div class="board-header">
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          :class="['tab', { active: activeTab === tab }]"
          @click="activeTab = tab"
        >{{ tab }}</button>
      </div>
      <router-link to="/announcements" class="more-link">
        查看全部
        <ArrowRight :size="12" :stroke-width="2.5" />
      </router-link>
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
        <router-link :to="`/announcements/${item.id}`" class="news-title">{{ item.title }}</router-link>
        <span class="news-date">{{ item.published_at }}</span>
      </li>
      <li v-if="currentList.length === 0" class="news-empty">暂无相关公告</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Loader2, AlertCircle, ArrowRight } from 'lucide-vue-next'
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
.announcement-board {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* 板块标题 */
.board-section-header {
  padding: var(--sp-6) var(--sp-6) var(--sp-3);
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  border-bottom: 1px solid var(--c-beige-border);
  background: var(--c-beige-card);
}

.section-label {
  display: inline-block;
  background: var(--c-green-pale);
  color: var(--c-green-deep);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: var(--r-pill);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--c-text-dark);
  font-family: var(--f-serif);
  letter-spacing: 1px;
}

/* Tab 行 */
.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--sp-5);
  background: white;
  border-bottom: 1px solid #f0f0eb;
}

.tabs {
  display: flex;
  gap: var(--sp-1);
  padding: var(--sp-2) 0;
}

.tab {
  padding: 6px 14px;
  background: none;
  border: none;
  font-size: 13px;
  color: var(--c-text-muted);
  cursor: pointer;
  font-weight: 500;
  border-radius: var(--r-pill);
  transition: background var(--t-base), color var(--t-base);
  letter-spacing: 0.2px;
}
.tab:hover {
  background: var(--c-green-pale);
  color: var(--c-green-deep);
}
.tab.active {
  background: var(--c-green-pale);
  color: var(--c-green-deep);
  font-weight: 600;
}

.more-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--c-green-mid);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--t-fast);
}
.more-link:hover { color: var(--c-green-deep); }

/* 状态行 */
.state-row {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: 28px var(--sp-5);
  font-size: 13px;
  color: #94a3b8;
}
.state-error { color: #e53e3e; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 公告列表 */
.news-list { list-style: none; margin: 0; padding: var(--sp-2) 0; }

.news-item {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: 10px var(--sp-5);
  border-bottom: 1px solid #f5f5f2;
  transition: background var(--t-fast);
}
.news-item:last-child { border-bottom: none; }
.news-item:hover { background: var(--c-beige); }

.news-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--c-green-mid);
  flex-shrink: 0;
  box-shadow: 0 0 0 3px var(--c-green-pale);
}

.news-title {
  flex: 1;
  font-size: 13.5px;
  color: var(--c-text-dark);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color var(--t-fast);
}
.news-title:hover { color: var(--c-green-mid); }

.news-date {
  font-size: 11.5px;
  color: var(--c-text-muted);
  white-space: nowrap;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.news-empty {
  padding: var(--sp-5);
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
}
</style>
