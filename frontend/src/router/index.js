import { createRouter, createWebHistory } from 'vue-router'
import Home        from '../views/Home.vue'
import Chat        from '../views/Chat.vue'
import Diary       from '../views/Diary.vue'
import Science     from '../views/Science.vue'
import Appointment from '../views/Appointment.vue'
import About       from '../views/About.vue'
import Treehouse   from '../views/Treehouse.vue'

const routes = [
  { path: '/',            component: Home },
  { path: '/chat',        component: Chat },
  { path: '/diary',       component: Diary },
  { path: '/science',     component: Science },
  { path: '/appointment', component: Appointment },
  { path: '/about',       component: About },
  { path: '/treehouse',   component: Treehouse },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

export default router
