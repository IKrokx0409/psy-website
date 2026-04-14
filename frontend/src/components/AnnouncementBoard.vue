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

    <ul class="news-list">
      <li
        v-for="item in currentList"
        :key="item.title"
        class="news-item"
      >
        <span class="news-dot"></span>
        <a href="#" class="news-title">{{ item.title }}</a>
        <span class="news-date">{{ item.date }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const tabs = ['中心公告', '活动预告', '心理讲座']
const activeTab = ref('中心公告')

const data = {
  '中心公告': [
    { title: '关于开展2026年春季"5·25"心理健康月系列活动的通知', date: '2026-04-07' },
    { title: '心理健康教育与咨询中心2026年春季预约咨询安排', date: '2026-04-01' },
    { title: '关于心理测评系统维护升级的通知', date: '2026-03-25' },
    { title: '2025-2026学年秋季心理普查结果反馈说明', date: '2026-03-18' },
    { title: '团体心理辅导"压力管理"课程开放报名', date: '2026-03-10' },
    { title: '心理危机干预工作规范（修订版）正式施行', date: '2026-03-01' },
  ],
  '活动预告': [
    { title: '【5·25系列】正念减压体验工作坊（第一期）', date: '2026-04-15' },
    { title: '大学生情绪管理专题沙龙 — 如何与焦虑共处', date: '2026-04-20' },
    { title: '"心灵绿洲"户外团体活动报名开启', date: '2026-04-22' },
    { title: '2026届毕业生压力疏导专场团辅', date: '2026-04-28' },
    { title: '人际关系与沟通技巧训练营（四期）', date: '2026-05-06' },
    { title: '全国大学生心理健康日线上直播答疑', date: '2026-05-25' },
  ],
  '心理讲座': [
    { title: '【讲座】睡眠与心理健康 — 为什么你总睡不好？', date: '2026-04-10' },
    { title: '【讲座】如何建立安全的亲密关系', date: '2026-04-17' },
    { title: '【讲座】学业拖延背后的心理机制与应对', date: '2026-04-24' },
    { title: '【讲座】抑郁情绪识别与自我关怀', date: '2026-05-08' },
    { title: '【讲座】大学生职业规划中的心理适应', date: '2026-05-15' },
    { title: '【讲座】正念冥想入门：活在当下的科学方法', date: '2026-05-22' },
  ],
}

const currentList = computed(() => data[activeTab.value])
</script>

<style scoped>
.announcement-board {
  background: white;
  border: 1px solid #e8eef8;
  border-radius: 0;
  overflow: hidden;
}

.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 2px solid #e8eef8;
  background: #fafbfe;
}

.tabs { display: flex; gap: 0; }
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
  background: #009DE0;
  transform: scaleX(0);
  transition: transform 0.2s;
}
.tab:hover { color: #009DE0; }
.tab.active { color: #009DE0; font-weight: 600; }
.tab.active::after { transform: scaleX(1); }

.more-link {
  font-size: 12.5px;
  color: #009DE0;
  text-decoration: none;
}
.more-link:hover { text-decoration: underline; }

.news-list {
  list-style: none;
  margin: 0;
  padding: 8px 0;
}

.news-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-bottom: 1px dashed #f0f4fb;
  transition: background 0.12s;
}
.news-item:last-child { border-bottom: none; }
.news-item:hover { background: #f5f8ff; }

.news-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #009DE0;
  flex-shrink: 0;
}

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
.news-title:hover { color: #009DE0; }

.news-date {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
  flex-shrink: 0;
}
</style>
