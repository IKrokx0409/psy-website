<template>
  <div class="app-shell">
    <NavBar />
    <div :class="['page-content', {
      'chat-mode':   route.path === '/chat',
      'diary-mode':  route.path === '/diary',
      'course-mode': route.path.startsWith('/course/'),
    }]">
      <router-view />
    </div>

    <!-- 树洞浮标：隐秘入口，仅在非树洞页显示 -->
    <Transition name="float-fade">
      <router-link
        v-if="route.path !== '/treehouse'"
        to="/treehouse"
        class="treehouse-float"
        :title="floatHovered ? '有什么想说的…' : ''"
        @mouseenter="floatHovered = true"
        @mouseleave="floatHovered = false"
      >
        <TreePine :size="20" :stroke-width="1.5" />
        <span class="float-label" :class="{ visible: floatHovered }">树洞</span>
      </router-link>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { TreePine } from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const floatHovered = ref(false)
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 普通页面：可滚动，内容由各页面自管理 */
.page-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Chat 页面：不滚动，撑满，以 flex 向下传递高度 */
.page-content.chat-mode {
  overflow: hidden;
  display: flex;
}

/* 日记页面：不滚动，撑满剩余高度 */
.page-content.diary-mode {
  overflow: hidden;
}

/* 课程详情页：不滚动，flex 向下传递 */
.page-content.course-mode {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 树洞隐秘浮标 */
.treehouse-float {
  position: fixed;
  bottom: 36px;
  right: 28px;
  z-index: 900;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(120, 170, 140, 0.3);
  color: #4a8a60;
  border-radius: var(--r-pill);
  padding: 10px 16px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  box-shadow: var(--shadow-md);
  transition: background var(--t-base), box-shadow var(--t-base), border-color var(--t-base);
  overflow: hidden;
  white-space: nowrap;
  letter-spacing: 0.3px;
}
.treehouse-float:hover {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--shadow-lg);
  border-color: rgba(95, 158, 117, 0.45);
}

.float-label {
  max-width: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-width 0.25s ease, opacity 0.2s ease;
}
.float-label.visible {
  max-width: 60px;
  opacity: 1;
}

/* 进场/离场动画 */
.float-fade-enter-active,
.float-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.float-fade-enter-from,
.float-fade-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
