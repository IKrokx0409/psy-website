import { createRouter, createWebHistory } from 'vue-router'
import Home                from '../views/Home.vue'
import Chat                from '../views/Chat.vue'
import Diary               from '../views/Diary.vue'
import Science             from '../views/Science.vue'
import Appointment         from '../views/Appointment.vue'
// About redirects to external site — no component needed
import Treehouse           from '../views/Treehouse.vue'
import Login               from '../views/Login.vue'
import TeacherPanel        from '../views/TeacherPanel.vue'
import AnnouncementList    from '../views/AnnouncementList.vue'
import AnnouncementDetail  from '../views/AnnouncementDetail.vue'
import ResourceDetail       from '../views/ResourceDetail.vue'
import CourseCenter         from '../views/CourseCenter.vue'
import ClassHome            from '../views/ClassHome.vue'
import AssignmentDetail     from '../views/AssignmentDetail.vue'
import DiscussionDetail     from '../views/DiscussionDetail.vue'
import GroupDetail          from '../views/GroupDetail.vue'

const routes = [
  { path: '/login',                component: Login,             meta: { public: true } },
  { path: '/',                     component: Home,              meta: { public: true } },
  { path: '/about', beforeEnter() { window.location.href = 'http://xg.hitsz.edu.cn/xlzx/zxgk1/zxjj.htm' }, component: { render: () => null } },
  { path: '/science',              component: Science,           meta: { public: true } },
  { path: '/announcements',        component: AnnouncementList,  meta: { public: true } },
  { path: '/announcements/:id',    component: AnnouncementDetail, meta: { public: true } },
  { path: '/resources/:id',        component: ResourceDetail,     meta: { public: true } },
  { path: '/chat',                 component: Chat },
  { path: '/diary',                component: Diary },
  { path: '/appointment',          component: Appointment },
  { path: '/treehouse',            component: Treehouse },
  { path: '/course',               component: CourseCenter },
  { path: '/course/:classId',      component: ClassHome },
  { path: '/course/:classId/assignment/:assignmentId', component: AssignmentDetail },
  { path: '/course/:classId/discuss/:threadId',        component: DiscussionDetail },
  { path: '/course/:classId/group/:groupId',           component: GroupDetail },
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
