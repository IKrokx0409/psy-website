<template>
  <section class="hero">
    <!-- 幻灯片 -->
    <div class="slides-wrap">
      <transition name="fade" mode="out-in">
        <div class="slide" :key="current" :style="{ background: slides[current].bg }">
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
            <component :is="slides[current].deco" class="slide-deco" :size="120" :stroke-width="0.8" />
          </div>
        </div>
      </transition>
    </div>

    <!-- 控制点 -->
    <div class="dots">
      <span
        v-for="(_, i) in slides"
        :key="i"
        :class="['dot', { active: i === current }]"
        @click="goTo(i)"
      />
    </div>

    <!-- 前/后箭头 -->
    <button class="arrow arrow-prev" @click="prev">‹</button>
    <button class="arrow arrow-next" @click="next">›</button>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Leaf, Bot, BookOpen } from 'lucide-vue-next'

const slides = [
  {
    bg: 'linear-gradient(135deg, #5f9e75 0%, #4d8764 100%)',
    tag: '哈工大（深圳）心理健康中心',
    title: '陪伴每一位同学\n守护你的心灵健康',
    desc: '专业、温暖、保密。无论你正在经历什么，我们都在这里。',
    deco: Leaf,
    primaryBtn: '与 AI 倾诉',
    primaryLink: '/chat',
  },
  {
    bg: 'linear-gradient(135deg, #6aad82 0%, #5f9e75 60%, #4d8764 100%)',
    tag: 'AI 智能疏导',
    title: '随时倾诉\n不再一个人扛',
    desc: '基于先进大语言模型，提供 7×24 小时智能情绪支持与陪伴。',
    deco: Bot,
    primaryBtn: '立即体验',
    primaryLink: '/chat',
  },
  {
    bg: 'linear-gradient(135deg, #4d8764 0%, #5f9e75 100%)',
    tag: '丰富的心理资源',
    title: '科普 · 测评 · 日记\n全方位守护心理健康',
    desc: '心理科普文章、情绪打卡日记、专业量表自测，一站式心理健康平台。',
    deco: BookOpen,
    primaryBtn: '浏览资源',
    primaryLink: '/science',
  },
]

const current = ref(0)
let timer = null

const next = () => { current.value = (current.value + 1) % slides.length }
const prev = () => { current.value = (current.value - 1 + slides.length) % slides.length }
const goTo = (i) => { current.value = i; resetTimer() }

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
  height: 420px;
  overflow: hidden;
}

.slides-wrap { width: 100%; height: 100%; }

.slide {
  width: 100%;
  height: 420px;
  display: flex;
  align-items: center;
}

.slide-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.slide-text { max-width: 580px; color: white; }

.slide-tag {
  display: inline-block;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 2px;
  padding: 4px 14px;
  font-size: 12px;
  margin-bottom: 20px;
  letter-spacing: 0.5px;
}

.slide-title {
  font-size: 38px;
  font-weight: 700;
  line-height: 1.3;
  margin: 0 0 16px;
  white-space: pre-line;
  letter-spacing: 1px;
  text-shadow: 0 2px 12px rgba(0,0,0,0.15);
}

.slide-desc {
  font-size: 15px;
  opacity: 0.88;
  line-height: 1.7;
  margin: 0 0 28px;
}

.slide-actions { display: flex; gap: 14px; align-items: center; }

.btn-primary {
  display: inline-block;
  background: white;
  color: #5f9e75;
  padding: 11px 28px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15);
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(0,0,0,0.2); }

.btn-outline {
  display: inline-block;
  color: white;
  border: 1.5px solid rgba(255,255,255,0.7);
  padding: 10px 24px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s;
}
.btn-outline:hover { background: rgba(255,255,255,0.15); }

.slide-deco { opacity: 0.25; user-select: none; color: white; flex-shrink: 0; }

/* 控制点 */
.dots {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.45);
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}
.dot.active { background: white; transform: scale(1.3); }

/* 箭头 */
.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.15);
  border: none;
  color: white;
  font-size: 32px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  z-index: 10;
  line-height: 1;
  padding: 0;
}
.arrow:hover { background: rgba(255,255,255,0.28); }
.arrow-prev { left: 20px; }
.arrow-next { right: 20px; }

/* 过渡动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
