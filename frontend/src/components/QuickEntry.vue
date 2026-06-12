<template>
  <section class="quick-entry">
    <div class="inner">
      <router-link
        v-for="item in entries"
        :key="item.to"
        :to="item.to"
        class="entry-card"
      >
        <div class="entry-icon-wrap">
          <component :is="item.icon" :size="24" :stroke-width="1.5" />
        </div>
        <div class="entry-body">
          <div class="entry-title">{{ item.title }}</div>
          <div class="entry-desc">{{ item.desc }}</div>
        </div>
        <div class="entry-arrow">
          <ArrowRight :size="15" :stroke-width="2" />
        </div>
      </router-link>
    </div>
  </section>
</template>

<script setup>
import { Bot, BookMarked, Library, ClipboardList, ArrowRight } from 'lucide-vue-next'

const entries = [
  { to: '/chat',        icon: Bot,           title: 'AI 智能疏导', desc: '随时倾诉，智能陪伴' },
  { to: '/diary',       icon: BookMarked,    title: '情绪日记',    desc: '记录情绪，洞察自己' },
  { to: '/science',          icon: Library,       title: '心理资源',    desc: '专业资源，随时获取' },
  { to: '/science?tab=quiz', icon: ClipboardList, title: '心理测评',    desc: '专业量表，了解自我' },
]
</script>

<style scoped>
.quick-entry {
  background: var(--c-beige-card);
  border-top: 3px solid var(--c-green-mid);
  border-bottom: 1px solid var(--c-beige-border);
  box-shadow: var(--shadow-sm);
}

.inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}

.entry-card {
  display: flex;
  align-items: center;
  gap: var(--sp-4);
  padding: 20px var(--sp-5);
  text-decoration: none;
  color: inherit;
  border-right: 1px solid var(--c-beige-border);
  transition: background var(--t-base), transform var(--t-base), box-shadow var(--t-base);
  position: relative;
}
.entry-card:last-child { border-right: none; }
.entry-card:hover {
  background: var(--c-gold-pale);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(30, 70, 40, 0.06);
  z-index: 1;
}

/* 图标容器 */
.entry-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--r-md);
  background: var(--c-green-pale);
  color: var(--c-green-deep);
  flex-shrink: 0;
  transition: background var(--t-base), color var(--t-base);
}
.entry-card:hover .entry-icon-wrap {
  background: var(--c-green-mid);
  color: white;
}

.entry-body { flex: 1; min-width: 0; }

.entry-title {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--c-text-dark);
  margin-bottom: 3px;
  letter-spacing: 0.2px;
}
.entry-desc {
  font-size: 12px;
  color: var(--c-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.entry-arrow {
  color: var(--c-green-mid);
  opacity: 0;
  transform: translateX(-6px);
  transition: opacity var(--t-base), transform var(--t-base);
  flex-shrink: 0;
}
.entry-card:hover .entry-arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>
