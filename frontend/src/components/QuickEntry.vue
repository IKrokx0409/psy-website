<template>
  <section class="quick-entry">
    <div class="inner">
      <router-link
        v-for="item in entries"
        :key="item.to"
        :to="item.to"
        class="entry-card"
      >
        <div class="entry-icon"><component :is="item.icon" :size="28" :stroke-width="1.5" /></div>
        <div class="entry-body">
          <div class="entry-title">{{ item.title }}</div>
          <div class="entry-desc">{{ item.desc }}</div>
        </div>
        <div class="entry-arrow">→</div>
      </router-link>
    </div>
  </section>
</template>

<script setup>
import { Bot, BookMarked, Library, ClipboardList } from 'lucide-vue-next'

const entries = [
  { to: '/chat',        icon: Bot,           title: 'AI 智能疏导', desc: '随时倾诉，智能陪伴' },
  { to: '/diary',       icon: BookMarked,    title: '情绪日记',    desc: '记录情绪，洞察自己' },
  { to: '/#resources',  icon: Library,       title: '心理资源',    desc: '专业资源，随时获取' },
  { to: '/science',     icon: ClipboardList, title: '心理测评',    desc: '专业量表，了解自我' },
]
</script>

<style scoped>
.quick-entry {
  background: white;
  border-bottom: 1px solid #cfe8da;
  box-shadow: 0 4px 16px rgba(0, 157, 224, 0.07);
}
.inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}

.entry-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 22px 20px;
  text-decoration: none;
  color: inherit;
  border-right: 1px solid #eef2fa;
  transition: background 0.15s, transform 0.15s;
  position: relative;
}
.entry-card:last-child { border-right: none; }
.entry-card:hover {
  background: #edf7f2;
}
.entry-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: #5f9e75;
  transform: scaleX(0);
  transition: transform 0.2s;
}
.entry-card:hover::after { transform: scaleX(1); }

.entry-icon { display: flex; align-items: center; justify-content: center; width: 36px; flex-shrink: 0; color: #5f9e75; }

.entry-body { flex: 1; min-width: 0; }
.entry-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 3px;
}
.entry-desc {
  font-size: 12.5px;
  color: #64748b;
}

.entry-arrow {
  color: #5f9e75;
  font-size: 18px;
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity 0.15s, transform 0.15s;
}
.entry-card:hover .entry-arrow { opacity: 1; transform: translateX(0); }
</style>
