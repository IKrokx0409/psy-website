import { createRouter, createWebHistory } from 'vue-router'
// 引入我们刚才建好的房间
import Home from '../views/Home.vue'
import Chat from '../views/Chat.vue'
import Diary from '../views/Diary.vue'

const routes = [
  { path: '/', component: Home },          // 访问根目录，显示主页
  { path: '/chat', component: Chat },      // 访问 /chat，显示 AI 聊天室
  { path: '/diary', component: Diary }     // 访问 /diary，显示日记本
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router