<template>
  <div class="side-panel">
    <!-- 每日心理小贴士 -->
    <div class="panel-card tip-card">
      <div class="panel-header">
        <div class="header-icon-wrap"><Lightbulb :size="14" :stroke-width="1.5" /></div>
        <span class="panel-title-text">每日心理小贴士</span>
        <button class="refresh-btn" @click="refreshTip" title="换一条">
          <RotateCcw :size="12" :stroke-width="2" />
        </button>
      </div>
      <div class="tip-body">
        <p class="tip-text">{{ currentTip }}</p>
      </div>
    </div>

    <!-- 预约咨询 -->
    <div class="panel-card appt-card">
      <div class="panel-header">
        <div class="header-icon-wrap appt-icon"><CalendarDays :size="14" :stroke-width="1.5" /></div>
        <span class="panel-title-text">预约咨询</span>
      </div>
      <div class="info-body">
        <div class="info-row">
          <span class="info-label">咨询热线</span>
          <a href="tel:075526400952" class="info-number appt-number">0755-26400952</a>
        </div>
        <p class="info-note">周一至周日 &nbsp;8:30–11:30 / 13:30–17:00</p>
      </div>
    </div>

    <!-- 危机援助 -->
    <div class="panel-card crisis-card">
      <div class="panel-header">
        <div class="header-icon-wrap crisis-icon"><PhoneCall :size="14" :stroke-width="1.5" /></div>
        <span class="panel-title-text">心理援助热线</span>
        <span class="badge-24h">24h</span>
      </div>
      <div class="info-body">
        <div class="info-row">
          <span class="info-label">北京危机研究</span>
          <a href="tel:01082951332" class="info-number crisis-number">010-82951332</a>
        </div>
        <div class="info-row">
          <span class="info-label">全国心理援助</span>
          <a href="tel:4001161117" class="info-number crisis-number">400-116-1117</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Lightbulb, PhoneCall, CalendarDays, RotateCcw } from 'lucide-vue-next'

const tips = [
  '深呼吸练习：吸气 4 秒，屏息 4 秒，呼气 6 秒。每天练习 3 次，有效缓解焦虑。',
  '每天花 5 分钟记录 3 件让你感到感激的事，有助于提升整体幸福感。',
  '"5-4-3-2-1" 接地技术：找出 5 样能看到的、4 样能触摸到的、3 样能听到的、2 样能闻到的、1 样能尝到的，帮你回到当下。',
  '适度运动是天然抗抑郁剂，哪怕每天只是散步 20 分钟也有明显帮助。',
  '与信任的朋友倾诉，比一个人扛所有事情轻松得多。开口是勇气，不是软弱。',
  '当感到不知所措时，把事情分解成"今天只需要做这一件小事"，专注当下。',
  '睡前放下手机，给自己留 30 分钟"缓冲区"，进行轻度阅读或冥想。',
  '情绪没有对错。允许自己感到悲伤、愤怒或焦虑，接纳情绪是处理情绪的第一步。',
]

const idx = ref(Math.floor(Math.random() * tips.length))
const currentTip = ref(tips[idx.value])

const refreshTip = () => {
  let next = Math.floor(Math.random() * tips.length)
  while (next === idx.value && tips.length > 1) next = Math.floor(Math.random() * tips.length)
  idx.value = next
  currentTip.value = tips[next]
}
</script>

<style scoped>
.side-panel { display: flex; flex-direction: column; gap: var(--sp-4); }

/* 通用卡片 */
.panel-card {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* 卡片标题行 */
.panel-header {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: 14px var(--sp-4);
  border-bottom: 1px solid var(--c-beige-border);
  background: var(--c-beige-card);
}

.header-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: var(--r-sm);
  background: var(--c-green-pale);
  color: var(--c-green-mid);
  flex-shrink: 0;
}
.appt-icon  { background: #e8f4ff; color: #3b82f6; }
.crisis-icon { background: #fff0f0; color: #ef4444; }

.panel-title-text {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text-dark);
  letter-spacing: 0.3px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-sm);
  color: var(--c-text-muted);
  cursor: pointer;
  padding: 4px 6px;
  transition: background var(--t-fast), color var(--t-fast);
}
.refresh-btn:hover {
  background: var(--c-green-pale);
  color: var(--c-green-mid);
  border-color: var(--c-green-pale);
}

.badge-24h {
  font-size: 10px;
  font-weight: 700;
  background: #fff0f0;
  color: #ef4444;
  padding: 2px 7px;
  border-radius: var(--r-pill);
  letter-spacing: 0.5px;
  border: 1px solid #ffd5d5;
}

/* 贴士内容 */
.tip-body { padding: var(--sp-4); }
.tip-text {
  font-size: 13px;
  line-height: 1.75;
  color: var(--c-text-body);
  margin: 0;
}

/* 咨询/热线信息 */
.info-body {
  padding: var(--sp-3) var(--sp-4) var(--sp-4);
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--sp-2);
}

.info-label {
  font-size: 12px;
  color: var(--c-text-muted);
}

.info-number {
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.3px;
  transition: opacity var(--t-fast);
}
.info-number:hover { opacity: 0.75; }

.appt-number  { color: #3b82f6; }
.crisis-number { color: #ef4444; }

.info-note {
  font-size: 11.5px;
  color: var(--c-text-muted);
  margin: -4px 0 0;
  text-align: right;
}

/* 预约卡 */
.appt-card {
  border-color: #d8eaff;
}
.appt-card .panel-header { background: #f0f7ff; border-bottom-color: #d8eaff; }

/* 危机卡 */
.crisis-card {
  border-color: #ffd5d5;
}
.crisis-card .panel-header { background: #fff5f5; border-bottom-color: #ffd5d5; }
</style>
