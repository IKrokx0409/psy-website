<template>
  <div class="app-shell">
    <NavBar />
    <div :class="['page-content', { 'chat-mode': route.path === '/chat' }]">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
const route = useRoute()
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
</style>
