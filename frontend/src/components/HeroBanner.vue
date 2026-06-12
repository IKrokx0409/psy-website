<template>
  <section class="hero">
    <div class="slides-wrap">
      <transition name="fade" mode="out-in">
        <div class="slide" :key="current" :style="{ background: slides[current].bg }">

          <!-- 几何装饰背景 -->
          <div class="deco-wrap" aria-hidden="true">
            <svg class="deco-svg" viewBox="0 0 520 520" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="260" cy="260" r="230" stroke="white" stroke-opacity="0.04" stroke-width="1"/>
              <circle cx="260" cy="260" r="175" stroke="white" stroke-opacity="0.06" stroke-width="1.5"/>
              <circle cx="260" cy="260" r="120" stroke="white" stroke-opacity="0.09" stroke-width="2"/>
              <circle cx="260" cy="260" r="62"  fill="white" fill-opacity="0.06"/>
              <line x1="30"  y1="260" x2="490" y2="260" stroke="white" stroke-opacity="0.04" stroke-dasharray="6 12"/>
              <line x1="260" y1="30"  x2="260" y2="490" stroke="white" stroke-opacity="0.04" stroke-dasharray="6 12"/>
              <circle cx="420" cy="90"  r="32" stroke="white" stroke-opacity="0.07" stroke-width="1"/>
              <circle cx="90"  cy="420" r="20" stroke="white" stroke-opacity="0.05" stroke-width="1"/>
              <circle cx="400" cy="380" r="8"  fill="white" fill-opacity="0.08"/>
              <circle cx="120" cy="140" r="5"  fill="white" fill-opacity="0.07"/>
              <circle cx="450" cy="240" r="4"  fill="white" fill-opacity="0.1"/>
              <circle cx="180" cy="450" r="4"  fill="white" fill-opacity="0.07"/>
              <circle cx="460" cy="140" r="2.5" fill="white" fill-opacity="0.12"/>
              <circle cx="80"  cy="280" r="2.5" fill="white" fill-opacity="0.09"/>
            </svg>
          </div>

          <div class="slide-inner">
            <div class="slide-text">
              <div class="slide-tag">{{ slides[current].tag }}</div>
              <h1 class="slide-title">{{ slides[current].title }}</h1>
              <p class="slide-desc">{{ slides[current].desc }}</p>
              <div class="slide-actions">
                <router-link :to="slides[current].primaryLink" class="btn-primary">
                  {{ slides[current].primaryBtn }}
                </router-link>
                <router-link to="/appointment" class="btn-outline">预约线下咨询</router-link>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 进度条 -->
    <div class="progress-track">
      <div class="progress-fill" :key="`p-${current}`"></div>
    </div>

    <!-- 控制点 -->
    <div class="dots">
      <button
        v-for="(_, i) in slides"
        :key="i"
        :class="['dot', { active: i === current }]"
        @click="goTo(i)"
        :aria-label="`切换到第 ${i + 1} 张`"
      />
    </div>

    <!-- 前/后箭头 -->
    <button class="arrow arrow-prev" @click="prev" aria-label="上一张">
      <ChevronLeft :size="18" :stroke-width="2.5" />
    </button>
    <button class="arrow arrow-next" @click="next" aria-label="下一张">
      <ChevronRight :size="18" :stroke-width="2.5" />
    </button>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const slides = [
  {
    bg: 'linear-gradient(135deg, #2d5a42 0%, #3d6e52 55%, #4e8a66 100%)',
    tag: '哈工大（深圳）大学生心理健康教育与咨询中心',
    title: '陪伴每一位同学\n守护你的心灵健康',
    desc: '专业、温暖、保密。无论你正在经历什么，我们都在这里。',
    primaryBtn: '与 AI 倾诉',
    primaryLink: '/chat',
  },
  {
    bg: 'linear-gradient(135deg, #2a4e3a 0%, #38664e 55%, #4a7d5e 100%)',
    tag: 'AI 智能疏导',
    title: '随时倾诉\n不再一个人扛',
    desc: '基于先进大语言模型，提供 7×24 小时智能情绪支持与陪伴。',
    primaryBtn: '立即体验',
    primaryLink: '/chat',
  },
  {
    bg: 'linear-gradient(135deg, #264838 0%, #3d6e52 100%)',
    tag: '丰富的心理资源',
    title: '科普 · 测评 · 日记\n全方位守护心理健康',
    desc: '心理科普文章、情绪打卡日记、专业量表自测，一站式心理健康平台。',
    primaryBtn: '浏览资源',
    primaryLink: '/science',
  },
]

const current = ref(0)
let timer = null

const next  = () => { current.value = (current.value + 1) % slides.length }
const prev  = () => { current.value = (current.value - 1 + slides.length) % slides.length }
const goTo  = (i) => { current.value = i; resetTimer() }

const resetTimer = () => {
  clearInterval(timer)
  timer = setInterval(next, 5000)
}

onMounted(() => resetTimer())
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.hero {
  position: relative;
  width: 100%;
  height: 520px;
  overflow: hidden;
}

.slides-wrap { width: 100%; height: 100%; }

.slide {
  width: 100%;
  height: 520px;
  display: flex;
  align-items: center;
  position: relative;
}

/* 几何装饰 */
.deco-wrap {
  position: absolute;
  right: -40px;
  top: 50%;
  transform: translateY(-50%);
  width: 520px;
  height: 520px;
  pointer-events: none;
  user-select: none;
}
.deco-svg {
  width: 100%;
  height: 100%;
}

/* 幻灯片内容 */
.slide-inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
  width: 100%;
  position: relative;
  z-index: 1;
}

.slide-text {
  max-width: 580px;
  color: white;
}

.slide-tag {
  display: inline-flex;
  align-items: center;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: var(--r-pill);
  padding: 5px 16px;
  font-size: 12px;
  margin-bottom: var(--sp-5);
  letter-spacing: 0.6px;
  font-weight: 500;
}

.slide-title {
  font-size: 48px;
  font-weight: 700;
  font-family: var(--f-serif);
  color: white;
  line-height: 1.3;
  margin: 0 0 var(--sp-4);
  white-space: pre-line;
  letter-spacing: 3px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.25);
}

.slide-desc {
  font-size: 15px;
  opacity: 0.85;
  line-height: 1.75;
  margin: 0 0 var(--sp-8);
  max-width: 460px;
}

.slide-actions {
  display: flex;
  gap: var(--sp-4);
  align-items: center;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  background: white;
  color: #2e5c41;
  padding: 12px 30px;
  border-radius: var(--r-sm);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  transition: transform var(--t-base), box-shadow var(--t-base);
  box-shadow: 0 4px 20px rgba(0,0,0,0.22);
  letter-spacing: 0.3px;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0,0,0,0.28);
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  color: rgba(255,255,255,0.9);
  border: 1.5px solid rgba(255,255,255,0.55);
  padding: 11px 24px;
  border-radius: var(--r-sm);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background var(--t-base), border-color var(--t-base);
}
.btn-outline:hover {
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.8);
}

/* 进度条 */
.progress-track {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255,255,255,0.12);
  z-index: 20;
}
.progress-fill {
  height: 100%;
  background: rgba(255,255,255,0.55);
  border-radius: 0 2px 2px 0;
  animation: progress-run 5s linear forwards;
}
@keyframes progress-run {
  from { width: 0; }
  to   { width: 100%; }
}

/* 控制点 */
.dots {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: var(--sp-2);
  z-index: 20;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  border: none;
  cursor: pointer;
  transition: background var(--t-base), transform var(--t-base), width var(--t-base);
  padding: 0;
}
.dot.active {
  background: white;
  transform: scale(1.2);
  width: 22px;
  border-radius: 4px;
}

/* 箭头 */
.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--t-base), transform var(--t-base);
  z-index: 20;
  padding: 0;
}
.arrow:hover {
  background: rgba(255,255,255,0.25);
  transform: translateY(-50%) scale(1.05);
}
.arrow-prev { left: 24px; }
.arrow-next { right: 24px; }

/* 过渡动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.55s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── 移动端适配 ─────────────────────────────────────────── */
@media (max-width: 768px) {
  .hero { height: 380px; }
  .slide { height: 380px; }
  .slide-title { font-size: 32px; letter-spacing: 2px; }
  .slide-desc { font-size: 13.5px; margin-bottom: var(--sp-6); }
  .slide-tag { font-size: 11px; }
  .slide-inner { padding: 0 var(--sp-5); }
  .deco-wrap { width: 340px; height: 340px; right: -80px; opacity: 0.5; }
  .arrow-prev { left: 12px; }
  .arrow-next { right: 12px; }
  .arrow { width: 36px; height: 36px; }
}

@media (max-width: 480px) {
  .hero { height: 320px; }
  .slide { height: 320px; }
  .slide-title { font-size: 26px; letter-spacing: 1.5px; }
  .slide-actions { flex-direction: column; align-items: flex-start; gap: var(--sp-3); }
  .deco-wrap { display: none; }
  .btn-primary { padding: 11px 22px; font-size: 13px; }
  .btn-outline { padding: 10px 20px; font-size: 13px; }
}
</style>
