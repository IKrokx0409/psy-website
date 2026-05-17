<template>
  <div class="login-page">
    <!-- 左侧装饰区 -->
    <div class="login-deco" aria-hidden="true">
      <div class="deco-content">
        <div class="deco-logo">
          <BrainCircuit :size="48" :stroke-width="1.2" />
        </div>
        <h1 class="deco-title">大学生心理健康<br>教育与咨询中心</h1>
        <p class="deco-sub">哈尔滨工业大学（深圳）</p>
        <div class="deco-divider"></div>
        <p class="deco-quote">专业 · 温暖 · 保密</p>
      </div>
      <svg class="deco-bg-svg" viewBox="0 0 400 500" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="350" cy="80"  r="120" fill="white" fill-opacity="0.04"/>
        <circle cx="50"  cy="420" r="100" fill="white" fill-opacity="0.04"/>
        <circle cx="200" cy="260" r="200" stroke="white" stroke-opacity="0.05" stroke-width="1"/>
        <circle cx="200" cy="260" r="150" stroke="white" stroke-opacity="0.04" stroke-width="1"/>
        <circle cx="200" cy="260" r="100" stroke="white" stroke-opacity="0.04" stroke-width="1"/>
      </svg>
    </div>

    <!-- 右侧登录区 -->
    <div class="login-panel">
      <div class="login-card">
        <div class="card-header">
          <div class="card-title">欢迎回来</div>
          <div class="card-sub">请选择您的身份以继续</div>
        </div>

        <div class="id-field">
          <label class="id-label">工号 / 学号</label>
          <input
            v-model="inputId"
            class="id-input"
            placeholder="例如：001"
            maxlength="50"
            @keyup.enter="inputId && login('student')"
          />
          <p v-if="idError" class="id-error">请输入工号或学号</p>
        </div>

        <div class="role-grid">
          <!-- 学生 -->
          <button class="role-btn" @click="login('student')">
            <div class="role-icon-wrap role-icon-student">
              <GraduationCap :size="32" :stroke-width="1.3" />
            </div>
            <div class="role-name">学生</div>
            <div class="role-desc">浏览资源、AI 疏导<br>情绪日记、预约咨询</div>
          </button>

          <!-- 教师/咨询师 -->
          <button class="role-btn" @click="login('teacher')">
            <div class="role-icon-wrap role-icon-teacher">
              <UserCog :size="32" :stroke-width="1.3" />
            </div>
            <div class="role-name">教师 / 咨询师</div>
            <div class="role-desc">管理公告、查看树洞<br>处理预约、数据统计</div>
          </button>
        </div>

        <p class="login-note">
          <Lock :size="12" :stroke-width="1.5" />
          当前为开发模式，填写 ID 后选择身份即可进入
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { BrainCircuit, GraduationCap, UserCog, Lock } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { setRole } = useAuth()

const inputId  = ref(localStorage.getItem('diary_user_id') || '')
const idError  = ref(false)

const login = (role) => {
  const id = inputId.value.trim()
  if (!id) { idError.value = true; return }
  idError.value = false
  localStorage.setItem('diary_user_id', id)
  setRole(role)
  router.push('/')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

/* 左侧装饰 */
.login-deco {
  flex: 1;
  background: linear-gradient(145deg, #2d5a42 0%, #3d6e52 50%, #4a8763 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--sp-12);
  position: relative;
  overflow: hidden;
}

.deco-bg-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.deco-content {
  position: relative;
  z-index: 1;
  color: white;
  max-width: 320px;
}

.deco-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: var(--r-xl);
  margin-bottom: var(--sp-6);
  color: white;
}

.deco-title {
  font-size: 28px;
  font-weight: 700;
  font-family: var(--f-serif);
  line-height: 1.4;
  letter-spacing: 2px;
  margin: 0 0 var(--sp-3);
  text-shadow: 0 2px 16px rgba(0,0,0,0.15);
  color: white;
}

.deco-sub {
  font-size: 14px;
  opacity: 0.65;
  margin: 0 0 var(--sp-6);
  letter-spacing: 0.5px;
}

.deco-divider {
  width: 40px;
  height: 2px;
  background: rgba(255,255,255,0.35);
  border-radius: 2px;
  margin-bottom: var(--sp-4);
}

.deco-quote {
  font-size: 13px;
  opacity: 0.7;
  letter-spacing: 3px;
  margin: 0;
}

/* 右侧登录面板 */
.login-panel {
  width: 480px;
  flex-shrink: 0;
  background: var(--c-beige);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--sp-10) var(--sp-8);
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.card-header {
  margin-bottom: var(--sp-8);
}

.card-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-text-dark);
  font-family: var(--f-serif);
  letter-spacing: 1px;
  margin-bottom: var(--sp-2);
}

.card-sub {
  font-size: 14px;
  color: var(--c-text-muted);
}

/* 角色选择 */
.role-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-4);
  margin-bottom: var(--sp-6);
}

.role-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-6) var(--sp-4);
  border: 1.5px solid var(--c-beige-border);
  border-radius: var(--r-xl);
  background: white;
  cursor: pointer;
  transition: border-color var(--t-base), background var(--t-base), transform var(--t-base), box-shadow var(--t-base);
  text-align: center;
  box-shadow: var(--shadow-xs);
}
.role-btn:hover {
  border-color: var(--c-green-base);
  background: white;
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.role-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: var(--r-lg);
  transition: background var(--t-base), color var(--t-base);
}
.role-icon-student {
  background: var(--c-green-pale);
  color: var(--c-green-mid);
}
.role-icon-teacher {
  background: #e8f0ff;
  color: #4a6eb5;
}

.role-btn:hover .role-icon-student {
  background: var(--c-green-mid);
  color: white;
}
.role-btn:hover .role-icon-teacher {
  background: #4a6eb5;
  color: white;
}

.role-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--c-text-dark);
  letter-spacing: 0.3px;
}

.role-desc {
  font-size: 11.5px;
  color: var(--c-text-muted);
  line-height: 1.7;
}

.id-field {
  margin-bottom: var(--sp-5);
}

.id-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text-dark);
  margin-bottom: var(--sp-2);
  letter-spacing: 0.3px;
}

.id-input {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  font-size: 14px;
  color: var(--c-text-dark);
  background: white;
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--t-base), box-shadow var(--t-base);
}
.id-input:focus {
  border-color: var(--c-green-base);
  box-shadow: 0 0 0 3px rgba(74, 135, 99, 0.12);
}

.id-error {
  font-size: 12px;
  color: #e05252;
  margin: var(--sp-1) 0 0;
}

.login-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-1);
  font-size: 11.5px;
  color: #b0bcc5;
  margin: 0;
  text-align: center;
}
</style>
