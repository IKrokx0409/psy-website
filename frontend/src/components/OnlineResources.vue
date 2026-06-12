<template>
  <section id="resources" class="resources-section">
    <div class="inner">
      <div class="section-header">
        <span class="section-label">资源库</span>
        <h2 class="section-title">线上心理资源</h2>
        <p class="section-sub">专业量表、冥想音频、科普文章，随时随地支持你的心理健康。</p>
      </div>

      <div class="resources-grid">
        <router-link
          v-for="r in resources" :key="r.name"
          :to="r.to"
          class="resource-card"
        >
          <div class="card-icon" :style="{ background: r.bg }">
            <component :is="r.icon" :size="22" :stroke-width="1.5" :style="{ color: r.color }" />
          </div>
          <div class="card-body">
            <span class="card-name">{{ r.name }}</span>
            <p class="card-desc">{{ r.desc }}</p>
          </div>
          <span class="card-tag" :style="{ background: r.tagBg, color: r.color }">{{ r.tag }}</span>
          <div class="card-arrow">
            <ArrowUpRight :size="14" :stroke-width="2" />
          </div>
        </router-link>
      </div>

      <div class="more-wrap">
        <router-link to="/science" class="more-btn">
          查看全部心理资源
          <ArrowRight :size="14" :stroke-width="2" />
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import {
  Library, ClipboardList, Activity, Leaf, BookOpen,
  Headphones, Wind, HeartPulse, ArrowRight, ArrowUpRight,
} from 'lucide-vue-next'

const resources = [
  { to: '/science?tab=quiz&quiz=2', icon: ClipboardList, name: 'PHQ-9 抑郁自测量表',   desc: '基于国际标准的抑郁症状评估问卷，约 2 分钟完成。', tag: '情绪评估', bg: '#eef6ff', color: '#3b82f6', tagBg: '#dbeafe' },
  { to: '/science?tab=quiz&quiz=3', icon: Activity,      name: 'GAD-7 焦虑自测量表',   desc: '广泛性焦虑障碍评估，了解你的焦虑程度。',           tag: '情绪评估', bg: '#fff7ed', color: '#f97316', tagBg: '#ffedd5' },
  { to: '/resources/5',             icon: Wind,          name: '腹式呼吸 · 4-7-8练习', desc: '经科学验证的呼吸技术，快速激活副交感神经，缓解急性焦虑。', tag: '放松减压', bg: '#f0f9ff', color: '#0ea5e9', tagBg: '#e0f2fe' },
  { to: '/science?tab=quiz&quiz=4', icon: HeartPulse,    name: '压力知觉量表（PSS-10）', desc: 'PSS-10 感知压力量表，帮助了解近期生活中的压力水平。', tag: '情绪评估', bg: '#fff7ed', color: '#ea580c', tagBg: '#ffedd5' },
  { to: '/science?tab=quiz&quiz=5', icon: Leaf,          name: '失眠严重程度自评（ISI）', desc: '7道题评估你的失眠严重程度，并给出改善建议。',      tag: '睡眠辅助', bg: '#f0fdf4', color: '#22c55e', tagBg: '#dcfce7' },
  { to: '/resources/8',             icon: Headphones,    name: '大学生睡眠健康指南',    desc: '昼夜节律、睡眠压力、CBT-I——搞懂为什么你总睡不好。',  tag: '睡眠辅助', bg: '#fff1f2', color: '#f43f5e', tagBg: '#ffe4e6' },
  { to: '/resources/7',             icon: BookOpen,      name: '非暴力沟通基础',        desc: '4步框架让对话从对抗变为连接，适用于宿舍、恋爱、家庭。', tag: '知识学习', bg: '#fdf4ff', color: '#a855f7', tagBg: '#f3e8ff' },
  { to: '/science',                 icon: BookOpen,      name: '心理健康科普文章库',    desc: '涵盖情绪、人际、睡眠、学业压力等主题的专业文章。',    tag: '知识学习', bg: '#f0fdf4', color: '#16a34a', tagBg: '#dcfce7' },
]
</script>

<style scoped>
.resources-section {
  background: var(--c-beige);
  padding: var(--sp-16) 0;
  border-top: 1px solid var(--c-beige-border);
}

.inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
}

/* 章节头 */
.section-header {
  margin-bottom: var(--sp-10);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--sp-3);
}

.section-label {
  display: inline-block;
  background: var(--c-green-pale);
  color: var(--c-green-deep);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: var(--r-pill);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--c-text-dark);
  font-family: var(--f-serif);
  letter-spacing: 1.5px;
  margin: 0;
}

.section-sub {
  font-size: 14px;
  color: var(--c-text-muted);
  margin: 0;
  line-height: 1.6;
}

/* 资源网格 */
.resources-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--sp-5);
}

.resource-card {
  background: var(--c-beige-card);
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  padding: var(--sp-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
  text-decoration: none;
  position: relative;
  transition: transform var(--t-base), box-shadow var(--t-base), border-color var(--t-base);
  overflow: hidden;
}
.resource-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: #d4cfc8;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-body { flex: 1; }

.card-name {
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--c-text-dark);
  margin-bottom: var(--sp-1);
  line-height: 1.4;
}

.card-desc {
  font-size: 12px;
  color: var(--c-text-muted);
  line-height: 1.6;
  margin: 0;
}

.card-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--r-pill);
  font-size: 11px;
  font-weight: 600;
  align-self: flex-start;
  letter-spacing: 0.3px;
}

.card-arrow {
  position: absolute;
  top: var(--sp-4);
  right: var(--sp-4);
  color: #c4bdb4;
  opacity: 0;
  transform: translate(4px, -4px);
  transition: opacity var(--t-base), transform var(--t-base), color var(--t-base);
}
.resource-card:hover .card-arrow {
  opacity: 1;
  transform: translate(0, 0);
  color: var(--c-text-muted);
}

/* 更多按钮 */
.more-wrap { margin-top: var(--sp-8); text-align: center; }
.more-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  background: transparent;
  color: var(--c-green-mid);
  border: 1.5px solid var(--c-green-mid);
  padding: 11px 28px;
  border-radius: var(--r-sm);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: background var(--t-base), color var(--t-base);
  letter-spacing: 0.3px;
}
.more-btn:hover {
  background: var(--c-green-mid);
  color: white;
}

@media (max-width: 1024px) {
  .resources-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .resources-grid { grid-template-columns: 1fr; }
}
</style>
