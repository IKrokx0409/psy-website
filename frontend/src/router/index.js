import { createRouter, createWebHistory } from 'vue-router'
import Home                from '../views/Home.vue'
import Chat                from '../views/Chat.vue'
import Diary               from '../views/Diary.vue'
import Science             from '../views/Science.vue'
import Appointment         from '../views/Appointment.vue'
import About               from '../views/About.vue'
import Treehouse           from '../views/Treehouse.vue'
import Login               from '../views/Login.vue'
import TeacherPanel        from '../views/TeacherPanel.vue'
import AnnouncementList    from '../views/AnnouncementList.vue'
import AnnouncementDetail  from '../views/AnnouncementDetail.vue'
import ResourceDetail       from '../views/ResourceDetail.vue'

const routes = [
  { path: '/login',                component: Login,             meta: { public: true } },
  { path: '/',                     component: Home,              meta: { public: true } },
  { path: '/about',                component: About,             meta: { public: true } },
  { path: '/science',              component: Science,           meta: { public: true } },
  { path: '/announcements',        component: AnnouncementList,  meta: { public: true } },
  { path: '/announcements/:id',    component: AnnouncementDetail, meta: { public: true } },
  { path: '/resources/:id',        component: ResourceDetail,     meta: { public: true } },
  { path: '/chat',                 component: Chat },
  { path: '/diary',                component: Diary },
  { path: '/appointment',          component: Appointment },
  { path: '/treehouse',            component: Treehouse },
  { path: '/teacher',              component: TeacherPanel,      meta: { teacherOnly: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth', top: 20 }
    }
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  const role    = localStorage.getItem('mock_role')
  const hasRole = !!role
  if (!to.meta.public && !hasRole) {
    next('/login')
  } else if (to.path === '/login' && hasRole) {
    next('/')
  } else if (to.meta.teacherOnly && role !== 'teacher') {
    next('/')
  } else {
    next()
  }
})

export default router
