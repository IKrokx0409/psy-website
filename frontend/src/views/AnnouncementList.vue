<template>
  <div class="ann-list-page">

    <!-- 页头 -->
    <div class="ann-list-header">
      <div class="ann-list-header-inner">
        <router-link to="/" class="back-link">
          <ChevronLeft :size="15" :stroke-width="2" /> 返回首页
        </router-link>
        <h1 class="ann-list-title">通知公告</h1>
        <p class="ann-list-subtitle">哈尔滨工业大学（深圳）大学生心理健康教育与咨询中心</p>
      </div>
    </div>

    <!-- 分类 Tab -->
    <div class="ann-list-tabs-wrap">
      <div class="ann-list-tabs">
        <button
          v-for="tab in TABS"
          :key="tab"
          :class="['ann-tab', { active: activeTab === tab }]"
          @click="activeTab = tab"
        >{{ tab }}</button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="ann-list-body">
      <div class="ann-list-inner">

        <div v-if="loading" class="ann-state">
          <Loader2 :size="28" :stroke-width="1.5" class="spin" />
          <span>加载中…</span>
        </div>

        <div v-else-if="error" class="ann-state ann-state-error">
          <AlertCircle :size="22" :stroke-width="1.5" />
          <span>加载失败，请检查后端服务</span>
        </div>

        <div v-else-if="currentList.length === 0" class="ann-state">
          <FileText :size="36" :stroke-width="1" style="opacity:.3" />
          <span>暂无相关公告</span>
        </div>

        <div v-else class="ann-table">
          <router-link
            v-for="item in currentList"
            :key="item.id"
            :to="`/announcements/${item.id}`"
            class="ann-row"
          >
            <div class="ann-row-date">
              <span class="ann-row-day">{{ item.published_at?.slice(8, 10) }}</span>
              <span class="ann-row-ym">{{ item.published_at?.slice(0, 7) }}</span>
            </div>
            <div class="ann-row-sep"></div>
            <div class="ann-row-body">
              <span class="ann-row-cat">{{ item.category }}</span>
              <span class="ann-row-title">{{ item.title }}</span>
            </div>
            <ChevronRight :size="14" :stroke-width="1.5" class="ann-row-arrow" />
          </router-link>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, Loader2, AlertCircle, FileText } from 'lucide-vue-next'
import { getAnnouncements } from '@/api/announcements'

const TABS = ['全部', '中心公告', '活动预告', '心理讲座']

const activeTab = ref('全部')
const allData  = ref([])
const loading  = ref(true)
const error    = ref(false)

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
  activeTab.value === '全部'
    ? allData.value
    : allData.value.filter(item => item.category === activeTab.value)
)
</script>

<style scoped>
.ann-list-page {
  min-height: 100%;
  background: var(--c-beige);
  font-family: var(--f-sans);
}

/* ── 页头 ────────────────────────────────────────────────────────── */
.ann-list-header {
  background: linear-gradient(160deg, #5f9e75 0%, #4d8764 100%);
  padding: 56px 32px 48px;
  border-bottom: 3px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 6px rgba(30, 100, 60, 0.3);
}
.ann-list-header-inner {
  max-width: 900px;
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

.ann-list-title {
  font-family: 'SimSun', '宋体', 'STSong', 'NSimSun', Georgia, serif;
  font-size: 40px;
  font-weight: 900;
  color: #ffffff;
  margin: 0 0 10px;
  letter-spacing: 8px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
.ann-list-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  letter-spacing: 1px;
}

/* ── 分类 Tab ────────────────────────────────────────────────────── */
.ann-list-tabs-wrap {
  background: #fff;
  border-bottom: 1px solid #d8d2c8;
  position: sticky;
  top: 0;
  z-index: 10;
}
.ann-list-tabs {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  gap: 0;
}
.ann-tab {
  padding: 16px 24px;
  background: none;
  border: none;
  font-size: 14px;
  color: #5a5040;
  cursor: pointer;
  font-weight: 500;
  letter-spacing: 1px;
  position: relative;
  transition: color 0.15s;
  white-space: nowrap;
}
.ann-tab::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0; right: 0;
  height: 2px;
  background: #5f9e75;
  transform: scaleX(0);
  transition: transform 0.2s;
}
.ann-tab:hover { color: #5f9e75; }
.ann-tab.active { color: #5f9e75; font-weight: 600; }
.ann-tab.active::after { transform: scaleX(1); }

/* ── 内容区 ──────────────────────────────────────────────────────── */
.ann-list-body {
  padding: 40px 32px 80px;
}
.ann-list-inner {
  max-width: 900px;
  margin: 0 auto;
}

.ann-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 0;
  color: #94a3b8;
  font-size: 14px;
}
.ann-state-error { color: #b91c1c; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 行式列表 ────────────────────────────────────────────────────── */
.ann-table {
  background: #fff;
  border: 1px solid #d8d2c8;
  border-radius: var(--r-lg);
  overflow: hidden;
}

.ann-row {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 22px 28px;
  text-decoration: none;
  border-bottom: 1px solid #ece8e0;
  transition: background 0.15s;
}
.ann-row:last-child { border-bottom: none; }
.ann-row:hover { background: #faf8f4; }

/* 日期列 */
.ann-row-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 56px;
  flex-shrink: 0;
}
.ann-row-day {
  font-family: 'SimSun', '宋体', Georgia, serif;
  font-size: 26px;
  font-weight: 700;
  color: #5f9e75;
  line-height: 1;
}
.ann-row-ym {
  font-size: 11px;
  color: #8a8070;
  margin-top: 3px;
  letter-spacing: 0.5px;
}

/* 竖线分隔 */
.ann-row-sep {
  width: 1px;
  height: 44px;
  background: #d4cec4;
  margin: 0 24px;
  flex-shrink: 0;
}

/* 标题区 */
.ann-row-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
  overflow: hidden;
}
.ann-row-cat {
  font-size: 11.5px;
  color: #7a6e5a;
  letter-spacing: 0.5px;
}
.ann-row-title {
  font-family: 'SimSun', '宋体', 'STSong', Georgia, serif;
  font-size: 16px;
  color: #1e1a14;
  font-weight: 500;
  letter-spacing: 0.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.5;
  transition: color 0.15s;
}
.ann-row:hover .ann-row-title { color: #5f9e75; }

.ann-row-arrow {
  color: #b8b0a0;
  flex-shrink: 0;
  margin-left: 16px;
  transition: color 0.15s, transform 0.15s;
}
.ann-row:hover .ann-row-arrow {
  color: #5f9e75;
  transform: translateX(3px);
}

/* ── 响应式 ──────────────────────────────────────────────────────── */
@media (max-width: 600px) {
  .ann-list-header { padding: 40px 20px 36px; }
  .ann-list-title { font-size: 24px; }
  .ann-list-body { padding: 24px 16px 60px; }
  .ann-row { padding: 18px 16px; }
  .ann-row-sep { margin: 0 16px; }
  .ann-row-ym { display: none; }
}
</style>
