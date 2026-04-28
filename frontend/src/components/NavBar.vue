<template>
  <header class="site-header">
    <!-- 主导航栏 -->
    <nav class="navbar" :class="isTreehouse ? 'navbar--treehouse' : 'navbar--default'">
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
          <router-link to="/science">心理资源</router-link>
          <router-link to="/chat">AI 智能疏导</router-link>
          <router-link to="/diary">情绪日记</router-link>
          <router-link to="/course">心理课</router-link>
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
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { GraduationCap, UserCog, LogOut, LogIn, ShieldCheck } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route  = useRoute()
const { isTeacher, isLoggedIn, clearRole } = useAuth()

const isTreehouse = computed(() => route.path === '/treehouse')

const switchRole = () => {
  clearRole()
  router.push('/login')
}
</script>

<style scoped>
.site-header { width: 100%; }

/* 主导航 */
.navbar {
  box-shadow: 0 2px 10px rgba(20, 50, 30, 0.35);
  transition: background 0.3s;
}
.navbar--default   { background: linear-gradient(170deg, #2d5a42 0%, #4a8763 100%); }
.navbar--treehouse { background: #1c3358; }
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
  height: 52px;
  width: auto;
  object-fit: contain;
  display: block;
}

.brand-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.brand-text { display: flex; flex-direction: column; gap: 3px; }
.brand-main {
  font-size: 17px;
  font-weight: 700;
  font-family: 'Songti SC', 'STSong', 'SimSun', Georgia, serif;
  letter-spacing: 2px;
  white-space: nowrap;
  line-height: 1;
}
.brand-sub {
  font-size: 10.5px;
  opacity: 0.75;
  letter-spacing: 0.3px;
  white-space: nowrap;
  line-height: 1;
}

/* 导航链接 */
.nav-links {
  display: flex;
  height: 100%;
}
.nav-links a {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 0 18px;
  height: 100%;
  border-bottom: 3px solid transparent;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  white-space: nowrap;
  box-sizing: border-box;
}
.nav-links a:hover {
  background: rgba(0, 0, 0, 0.12);
  color: white;
}
.nav-links a.router-link-active {
  background: rgba(0, 0, 0, 0.15);
  color: white;
  border-bottom-color: white;
  font-weight: 600;
}

/* 身份标识 */
.nav-role {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px 0 18px;
  height: 100%;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  font-weight: 500;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  white-space: nowrap;
}

.switch-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 4px;
  color: white;
  cursor: pointer;
  padding: 3px 5px;
  transition: background 0.15s;
  margin-left: 2px;
}
.switch-btn:hover { background: rgba(255, 255, 255, 0.28); }

/* 未登录时的登录按钮 */
.nav-login-btn {
  display: flex !important;
  align-items: center;
  gap: 5px;
  margin-left: 8px;
  padding: 0 18px !important;
  height: 36px !important;
  border: 1.5px solid rgba(255, 255, 255, 0.7) !important;
  border-radius: 3px;
  color: white !important;
  font-size: 13.5px !important;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.12) !important;
  transition: background 0.15s, border-color 0.15s !important;
  align-self: center;
  border-bottom: 1.5px solid rgba(255, 255, 255, 0.7) !important;
}
.nav-login-btn:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: white !important;
}

/* 管理后台链接 */
.nav-admin-link {
  display: flex !important;
  align-items: center;
  gap: 5px;
  background: rgba(255, 255, 255, 0.12) !important;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
