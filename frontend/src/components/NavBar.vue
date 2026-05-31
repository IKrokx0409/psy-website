<template>
  <header class="site-header">
    <nav class="navbar" :class="[isTreehouse ? 'navbar--treehouse' : 'navbar--default', { scrolled: isScrolled }]">
      <div class="nav-inner">
        <!-- 左侧：学校 Logo + 中心名称 -->
        <router-link to="/" class="nav-brand">
          <img src="/logos/logo-white.png" alt="哈工大深圳" class="nav-logo" />
          <div class="brand-divider"></div>
          <div class="brand-text">
            <div class="brand-main">大学生心理健康教育与咨询中心</div>
            <div class="brand-sub">Mental Health Education &amp; Counseling Center · HITSZ</div>
          </div>
        </router-link>

        <!-- 右侧：导航链接 -->
        <div class="nav-links" :class="{ 'nav-links--dark': isTreehouse }">
          <router-link to="/">首页</router-link>
          <router-link to="/course">心理课</router-link>
          <router-link to="/science">心理资源</router-link>
          <router-link to="/chat">AI 智能疏导</router-link>
          <router-link to="/diary">情绪日记</router-link>
          <router-link to="/appointment">预约咨询</router-link>
          <router-link to="/about">关于我们</router-link>
          <router-link v-if="isTeacher" to="/teacher" class="nav-admin-link">
            <ShieldCheck :size="13" :stroke-width="1.5" />
            管理后台
          </router-link>

          <!-- 已登录：身份标识 + 退出 -->
          <div v-if="isLoggedIn" class="nav-role">
            <component :is="isTeacher ? UserCog : GraduationCap" :size="14" :stroke-width="1.5" />
            <span>{{ isTeacher ? '教师' : '学生' }}</span>
            <button class="switch-btn" @click="switchRole" title="退出登录">
              <LogOut :size="12" :stroke-width="1.5" />
            </button>
          </div>

          <!-- 未登录：登录按钮 -->
          <router-link v-else to="/login" class="nav-login-btn">
            <LogIn :size="13" :stroke-width="1.5" />
            登录
          </router-link>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { GraduationCap, UserCog, LogOut, LogIn, ShieldCheck } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route  = useRoute()
const { isTeacher, isLoggedIn, clearRole } = useAuth()

const isTreehouse = computed(() => route.path === '/treehouse')
const isScrolled  = ref(false)

let pageContent = null

const onScroll = () => {
  isScrolled.value = (pageContent?.scrollTop ?? 0) > 12
}

onMounted(() => {
  pageContent = document.querySelector('.page-content')
  pageContent?.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  pageContent?.removeEventListener('scroll', onScroll)
})

const switchRole = () => {
  clearRole()
  router.push('/login')
}
</script>

<style scoped>
.site-header { width: 100%; position: relative; z-index: 100; }

/* 主导航 */
.navbar {
  transition: background var(--t-slow), box-shadow var(--t-slow);
}

.navbar--default {
  background: linear-gradient(170deg, rgba(37, 78, 56, 0.97) 0%, rgba(68, 122, 93, 0.97) 100%);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 1px 0 rgba(255,255,255,0.06), 0 4px 20px rgba(15, 40, 25, 0.3);
}
.navbar--default.scrolled {
  background: linear-gradient(170deg, #2d5a42 0%, #4a8763 100%);
  box-shadow: 0 2px 16px rgba(15, 40, 25, 0.35);
}
.navbar--treehouse {
  background: #1c3358;
  box-shadow: 0 2px 16px rgba(10, 20, 50, 0.4);
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 80px;
}

/* 品牌区 */
.nav-brand {
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  color: white;
  flex-shrink: 0;
}

.nav-logo {
  height: 54px;
  width: auto;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 1px 4px rgba(0,0,0,0.15));
}

.brand-divider {
  width: 1px;
  height: 38px;
  background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.35), transparent);
  flex-shrink: 0;
}

.brand-text { display: flex; flex-direction: column; gap: 4px; }

.brand-main {
  font-size: 18px;
  font-weight: 700;
  font-family: var(--f-serif);
  letter-spacing: 2.5px;
  white-space: nowrap;
  line-height: 1;
  text-shadow: 0 1px 6px rgba(0,0,0,0.15);
}
.brand-sub {
  font-size: 10.5px;
  opacity: 0.65;
  letter-spacing: 0.5px;
  white-space: nowrap;
  line-height: 1;
  font-weight: 400;
}

/* 导航链接 */
.nav-links {
  display: flex;
  height: 100%;
  align-items: stretch;
}

.nav-links a {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  padding: 0 16px;
  height: 100%;
  position: relative;
  transition: color var(--t-base), background var(--t-base);
  white-space: nowrap;
  letter-spacing: 0.2px;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: 0; left: 16px; right: 16px;
  height: 2px;
  background: white;
  border-radius: 2px 2px 0 0;
  transform: scaleX(0);
  transition: transform var(--t-base);
}

.nav-links a:hover {
  color: white;
  background: rgba(255, 255, 255, 0.08);
}

.nav-links a.router-link-active {
  color: white;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.1);
}
.nav-links a.router-link-active::after { transform: scaleX(1); }

/* 身份标识 */
.nav-role {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px 0 16px;
  height: 100%;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  font-weight: 500;
  border-left: 1px solid rgba(255, 255, 255, 0.15);
  white-space: nowrap;
  margin-left: 4px;
}

.switch-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--r-sm);
  color: white;
  cursor: pointer;
  padding: 4px 6px;
  transition: background var(--t-fast);
  margin-left: 2px;
}
.switch-btn:hover { background: rgba(255, 255, 255, 0.25); }

/* 未登录时的登录按钮 */
.nav-login-btn {
  display: flex !important;
  align-items: center;
  gap: 5px;
  margin-left: 10px;
  padding: 0 18px !important;
  height: 34px !important;
  border: 1.5px solid rgba(255, 255, 255, 0.6) !important;
  border-radius: var(--r-pill) !important;
  color: white !important;
  font-size: 13px !important;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.1) !important;
  transition: background var(--t-base), border-color var(--t-base) !important;
  align-self: center;
}
.nav-login-btn::after { display: none !important; }
.nav-login-btn:hover {
  background: rgba(255, 255, 255, 0.22) !important;
  border-color: rgba(255,255,255,0.9) !important;
}

/* 管理后台链接 */
.nav-admin-link {
  display: flex !important;
  align-items: center;
  gap: 5px;
  background: rgba(255, 255, 255, 0.1) !important;
  border-left: 1px solid rgba(255, 255, 255, 0.15) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
  font-size: 13px !important;
}
</style>
