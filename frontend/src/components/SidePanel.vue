<template>
  <div class="side-panel">
    <!-- 每日心理小贴士 -->
    <div class="panel-card tip-card">
      <div class="panel-title">
        <span class="title-dot"></span>
        每日心理小贴士
      </div>
      <div class="tip-content">
        <div class="tip-icon"><Lightbulb :size="22" :stroke-width="1.5" /></div>
        <p class="tip-text">{{ currentTip }}</p>
      </div>
      <button class="refresh-btn" @click="refreshTip">换一条 ↻</button>
    </div>

    <!-- 线上心理资源 -->
    <div class="panel-card resource-card">
      <div class="panel-title">
        <span class="title-dot"></span>
        线上心理资源
      </div>
      <ul class="resource-list">
        <li v-for="r in resources" :key="r.name" class="resource-item">
          <span class="resource-icon"><component :is="r.icon" :size="16" :stroke-width="1.5" /></span>
          <div class="resource-body">
            <a href="#" class="resource-name">{{ r.name }}</a>
            <span class="resource-tag">{{ r.tag }}</span>
          </div>
        </li>
      </ul>
    </div>

    <!-- 危机援助 -->
    <div class="panel-card crisis-card">
      <div class="crisis-header"><PhoneCall :size="14" :stroke-width="1.5" /> 心理援助热线</div>
      <div class="crisis-lines">
        <div class="crisis-line">
          <span class="line-label">学校热线</span>
          <a href="tel:075526033002" class="line-number">0755-26033002</a>
        </div>
        <div class="crisis-line">
          <span class="line-label">北京危机研究</span>
          <a href="tel:01082951332" class="line-number">010-82951332</a>
        </div>
        <div class="crisis-line">
          <span class="line-label">全国心理援助</span>
          <a href="tel:4001161117" class="line-number">400-116-1117</a>
        </div>
      </div>
      <p class="crisis-note">以上热线 24 小时开放</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Lightbulb, ClipboardList, Activity, Leaf, BookOpen, Headphones, PhoneCall } from 'lucide-vue-next'

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

const resources = [
  { icon: ClipboardList, name: 'PHQ-9 抑郁自测量表', tag: '情绪评估' },
  { icon: Activity,      name: 'GAD-7 焦虑自测量表', tag: '情绪评估' },
  { icon: Leaf,          name: '正念冥想引导音频',    tag: '放松减压' },
  { icon: BookOpen,      name: '心理健康科普文章库',  tag: '知识学习' },
  { icon: Headphones,    name: '睡眠放松白噪声',      tag: '睡眠辅助' },
]
</script>

<style scoped>
.side-panel { display: flex; flex-direction: column; gap: 16px; }

.panel-card {
  background: white;
  border: 1px solid #e8eef8;
  border-radius: 0;
  overflow: hidden;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 13px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 1px solid #f0f4fb;
  background: #fafbfe;
}
.title-dot {
  width: 3px;
  height: 16px;
  background: #009DE0;
  border-radius: 2px;
  flex-shrink: 0;
}

/* 贴士卡 */
.tip-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px 10px;
}
.tip-icon { display: flex; flex-shrink: 0; color: #f59e0b; }
.tip-text {
  font-size: 13.5px;
  line-height: 1.7;
  color: #374151;
  margin: 0;
}

.refresh-btn {
  display: block;
  margin: 0 16px 14px auto;
  background: none;
  border: 1px solid #d0dcf0;
  color: #009DE0;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 2px;
  cursor: pointer;
  transition: background 0.15s;
}
.refresh-btn:hover { background: #f0f5ff; }

/* 资源列表 */
.resource-list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}
.resource-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 16px;
  border-bottom: 1px solid #f4f7fb;
  transition: background 0.12s;
}
.resource-item:last-child { border-bottom: none; }
.resource-item:hover { background: #f5f8ff; }
.resource-icon { display: flex; flex-shrink: 0; color: #009DE0; }
.resource-body { display: flex; flex-direction: column; gap: 1px; }
.resource-name {
  font-size: 13px;
  color: #1e293b;
  text-decoration: none;
  transition: color 0.12s;
}
.resource-name:hover { color: #009DE0; }
.resource-tag {
  font-size: 11px;
  color: #94a3b8;
}

/* 危机热线 */
.crisis-card {
  border-color: #fde8e8;
  background: #fffaf9;
}
.crisis-header {
  padding: 12px 16px;
  font-size: 13.5px;
  font-weight: 600;
  color: #c0392b;
  border-bottom: 1px solid #fde8e8;
  display: flex;
  align-items: center;
  gap: 6px;
}
.crisis-lines { padding: 10px 16px; display: flex; flex-direction: column; gap: 8px; }
.crisis-line { display: flex; justify-content: space-between; align-items: center; }
.line-label { font-size: 12.5px; color: #64748b; }
.line-number {
  font-size: 13px;
  font-weight: 600;
  color: #c0392b;
  text-decoration: none;
  font-family: monospace;
}
.crisis-note {
  padding: 0 16px 12px;
  font-size: 11.5px;
  color: #94a3b8;
  margin: 0;
  text-align: right;
}
</style>
