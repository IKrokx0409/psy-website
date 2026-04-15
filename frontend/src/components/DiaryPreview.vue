<template>
  <section class="diary-preview">
    <div class="inner">
      <!-- 左：图表预览 -->
      <div class="chart-side">
        <div class="chart-header">
          <span class="chart-label">本周情绪追踪</span>
          <span class="chart-sub">示例数据</span>
        </div>
        <div class="chart-bars">
          <div v-for="day in weekData" :key="day.label" class="bar-col">
            <div class="bar-wrap">
              <div
                class="bar-fill"
                :style="{ height: day.val + '%', background: day.color }"
              ></div>
            </div>
            <div class="bar-emoji">{{ day.emoji }}</div>
            <div class="bar-label">{{ day.label }}</div>
          </div>
        </div>
        <div class="legend">
          <span v-for="l in legend" :key="l.name" class="legend-item">
            <span class="legend-dot" :style="{ background: l.color }"></span>{{ l.name }}
          </span>
        </div>
      </div>

      <!-- 右：文案 + 入口 -->
      <div class="text-side">
        <div class="feature-tag">情绪日记</div>
        <h2 class="feature-title">记录情绪<br>洞察自己</h2>
        <p class="feature-desc">
          每天花 2 分钟记录当下的情绪状态。通过长期追踪，发现情绪规律，
          找到压力的来源，学会与自己的内心对话。
        </p>
        <ul class="feature-points">
          <li><BarChart2 :size="15" :stroke-width="1.5" /> 可视化周/月情绪趋势图</li>
          <li><Lock :size="15" :stroke-width="1.5" /> 数据本地存储，完全私密</li>
          <li><PenLine :size="15" :stroke-width="1.5" /> 支持自由文字记录与情绪打标</li>
          <li><Bell :size="15" :stroke-width="1.5" /> 每日提醒，养成记录习惯</li>
        </ul>
        <router-link to="/diary" class="diary-btn">开始记录情绪 →</router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { BarChart2, Lock, PenLine, Bell } from 'lucide-vue-next'

const weekData = [
  { label: '周一', val: 60, emoji: '😐', color: '#f59e0b' },
  { label: '周二', val: 45, emoji: '😔', color: '#ef4444' },
  { label: '周三', val: 70, emoji: '🙂', color: '#10b981' },
  { label: '周四', val: 80, emoji: '😊', color: '#10b981' },
  { label: '周五', val: 55, emoji: '😐', color: '#f59e0b' },
  { label: '周六', val: 90, emoji: '😄', color: '#5f9e75' },
  { label: '周日', val: 75, emoji: '🙂', color: '#10b981' },
]

const legend = [
  { name: '愉悦', color: '#5f9e75' },
  { name: '平静', color: '#10b981' },
  { name: '一般', color: '#f59e0b' },
  { name: '低落', color: '#ef4444' },
]
</script>

<style scoped>
.diary-preview {
  background: #f8fafc;
  padding: 64px 0;
  border-top: 1px solid #cfe8da;
  border-bottom: 1px solid #cfe8da;
}
.inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

/* 图表侧 */
.chart-side {
  background: white;
  border: 1px solid #cfe8da;
  border-radius: 0;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 157, 224,0.06);
}
.chart-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 20px;
}
.chart-label { font-size: 15px; font-weight: 600; color: #1e293b; }
.chart-sub { font-size: 11.5px; color: #94a3b8; }

.chart-bars {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  height: 140px;
  margin-bottom: 10px;
}
.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.bar-wrap {
  flex: 1;
  width: 100%;
  background: #f1f5f9;
  border-radius: 4px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  min-height: 100px;
}
.bar-fill {
  width: 100%;
  border-radius: 0;
  transition: height 0.4s ease;
  opacity: 0.85;
}
.bar-emoji { font-size: 14px; }
.bar-label { font-size: 11px; color: #94a3b8; }

.legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 12px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: #64748b;
}
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }

/* 文案侧 */
.feature-tag {
  display: inline-block;
  background: #c4e2d0;
  color: #5f9e75;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 2px;
  margin-bottom: 16px;
}
.feature-title {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.3;
  margin: 0 0 16px;
}
.feature-desc {
  font-size: 14.5px;
  color: #475569;
  line-height: 1.75;
  margin: 0 0 20px;
}
.feature-points {
  list-style: none;
  margin: 0 0 28px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.feature-points li { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #374151; }
.feature-points li svg { color: #5f9e75; flex-shrink: 0; }

.diary-btn {
  display: inline-block;
  background: #5f9e75;
  color: white;
  padding: 12px 28px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s, transform 0.15s;
}
.diary-btn:hover { background: #4d8764; transform: translateY(-1px); }
</style>
