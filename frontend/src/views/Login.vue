<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 顶部品牌 -->
      <div class="login-header">
        <BrainCircuit :size="36" :stroke-width="1.2" class="header-icon" />
        <div>
          <div class="header-title">哈工大（深圳）心理健康中心</div>
          <div class="header-sub">请选择您的登录身份以继续</div>
        </div>
      </div>

      <div class="role-grid">
        <!-- 学生 -->
        <button class="role-btn" @click="login('student')">
          <GraduationCap :size="40" :stroke-width="1.2" class="role-icon" />
          <div class="role-name">学生</div>
          <div class="role-desc">浏览资源、AI 疏导<br>情绪日记、预约咨询</div>
        </button>

        <!-- 教师/咨询师 -->
        <button class="role-btn role-btn--teacher" @click="login('teacher')">
          <UserCog :size="40" :stroke-width="1.2" class="role-icon" />
          <div class="role-name">教师 / 咨询师</div>
          <div class="role-desc">管理公告、查看树洞<br>处理预约、数据统计</div>
        </button>
      </div>

      <p class="login-note">
        <Lock :size="12" :stroke-width="1.5" />
        当前为开发模式，无需账号密码，选择身份即可进入
      </p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { BrainCircuit, GraduationCap, UserCog, Lock } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { setRole } = useAuth()

const login = (role) => {
  setRole(role)
  router.push('/')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #5f9e75 0%, #4d8764 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.login-card {
  background: white;
  border-radius: 4px;
  padding: 44px 48px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
}

.login-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 36px;
  padding-bottom: 28px;
  border-bottom: 1px solid #cfe8da;
}

.header-icon { color: #5f9e75; flex-shrink: 0; }

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}
.header-sub {
  font-size: 13px;
  color: #64748b;
}

.role-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.role-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 28px 16px;
  border: 2px solid #cfe8da;
  border-radius: 4px;
  background: #f5fbf7;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
  text-align: center;
}
.role-btn:hover {
  border-color: #5f9e75;
  background: #edf7f2;
  transform: translateY(-2px);
}

.role-btn--teacher:hover {
  border-color: #4d8764;
  background: #edf7f2;
}

.role-icon { color: #5f9e75; }
.role-btn--teacher .role-icon { color: #4d8764; }

.role-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.role-desc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}

.login-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
  text-align: center;
}
</style>
