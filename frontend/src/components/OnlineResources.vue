<template>
  <section id="resources" class="resources-section">
    <div class="inner">
      <div class="section-head">
        <div class="head-left">
          <h2 class="section-title">
            <Library :size="22" :stroke-width="1.5" />
            线上心理资源
          </h2>
          <p class="section-sub">专业量表、冥想音频、科普文章，随时随地支持你的心理健康。</p>
        </div>
      </div>

      <div class="resources-grid">
        <!-- 自测量表 -->
        <div class="resource-card" v-for="r in resources" :key="r.name">
          <div class="card-icon" :style="{ background: r.bg }">
            <component :is="r.icon" :size="24" :stroke-width="1.5" :style="{ color: r.color }" />
          </div>
          <div class="card-body">
            <a href="#" class="card-name">{{ r.name }}</a>
            <p class="card-desc">{{ r.desc }}</p>
          </div>
          <span class="card-tag" :style="{ background: r.tagBg, color: r.color }">{{ r.tag }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import {
  Library,
  ClipboardList,
  Activity,
  Leaf,
  BookOpen,
  Headphones,
  Wind,
  HeartPulse,
} from 'lucide-vue-next'

const resources = [
  {
    icon: ClipboardList,
    name: 'PHQ-9 抑郁自测量表',
    desc: '基于国际标准的抑郁症状评估问卷，约 2 分钟完成。',
    tag: '情绪评估',
    bg: '#eef6ff', color: '#3b82f6', tagBg: '#dbeafe',
  },
  {
    icon: Activity,
    name: 'GAD-7 焦虑自测量表',
    desc: '广泛性焦虑障碍评估，了解你的焦虑程度。',
    tag: '情绪评估',
    bg: '#fff7ed', color: '#f97316', tagBg: '#ffedd5',
  },
  {
    icon: Leaf,
    name: '正念冥想引导音频',
    desc: '10 分钟身体扫描冥想，帮助平静思绪、回到当下。',
    tag: '放松减压',
    bg: '#f0fdf4', color: '#22c55e', tagBg: '#dcfce7',
  },
  {
    icon: Wind,
    name: '4-7-8 呼吸练习',
    desc: '经科学验证的呼吸技术，快速缓解急性焦虑与紧张。',
    tag: '放松减压',
    bg: '#f0f9ff', color: '#0ea5e9', tagBg: '#e0f2fe',
  },
  {
    icon: BookOpen,
    name: '心理健康科普文章库',
    desc: '涵盖情绪、人际、睡眠、学业压力等主题的专业文章。',
    tag: '知识学习',
    bg: '#fdf4ff', color: '#a855f7', tagBg: '#f3e8ff',
  },
  {
    icon: Headphones,
    name: '睡眠放松白噪声',
    desc: '雨声、森林、海浪等环境音，助你进入深度放松状态。',
    tag: '睡眠辅助',
    bg: '#fff1f2', color: '#f43f5e', tagBg: '#ffe4e6',
  },
  {
    icon: HeartPulse,
    name: '压力自评工具',
    desc: 'PSS 感知压力量表，帮助了解近期生活中的压力水平。',
    tag: '情绪评估',
    bg: '#fff7ed', color: '#ea580c', tagBg: '#ffedd5',
  },
  {
    icon: BookOpen,
    name: '人际关系小册子',
    desc: '宿舍相处、恋爱沟通、家庭压力——来自咨询师的建议。',
    tag: '知识学习',
    bg: '#f0fdf4', color: '#16a34a', tagBg: '#dcfce7',
  },
]
</script>

<style scoped>
.resources-section {
  background: #f4f7fc;
  padding: 56px 0;
  border-top: 1px solid #e5eaf2;
}
.inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

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
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}
.section-sub {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.resource-card {
  background: white;
  border: 1px solid #e8edf5;
  padding: 20px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  transition: transform 0.15s, box-shadow 0.15s;
  cursor: pointer;
}
.resource-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(30, 70, 120, 0.08);
  border-color: #c8d8ef;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-body { flex: 1; }
.card-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  text-decoration: none;
  margin-bottom: 4px;
  line-height: 1.4;
}
.card-name:hover { color: #5f9e75; }
.card-desc {
  font-size: 12.5px;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

.card-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  align-self: flex-start;
}

@media (max-width: 1024px) {
  .resources-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .resources-grid { grid-template-columns: 1fr; }
}
</style>
