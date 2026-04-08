<template>
  <header class="site-header">
    <!-- 顶部工具条 -->
    <div class="top-bar">
      <div class="top-bar-inner">
        <span>哈尔滨工业大学（深圳）· 心理健康中心</span>
        <div class="top-links">
          <a href="https://www.hitsz.edu.cn" target="_blank" rel="noopener">返回学校官网</a>
          <span class="divider">|</span>
          <span>{{ currentDate }}</span>
        </div>
      </div>
    </div>

    <!-- 主导航栏 -->
    <nav class="navbar">
      <div class="nav-inner">
        <router-link to="/" class="nav-brand">
          <span class="brand-icon">🧠</span>
          <div class="brand-text">
            <div class="brand-main">心理健康中心</div>
            <div class="brand-sub">Mental Health Center · HITSZ</div>
          </div>
        </router-link>

        <div class="nav-links">
          <router-link to="/">首页</router-link>
          <router-link to="/science">心理科普</router-link>
          <router-link to="/chat">AI 智能疏导</router-link>
          <router-link to="/treehouse">校园树洞</router-link>
          <router-link to="/appointment">预约咨询</router-link>
          <router-link to="/about">关于我们</router-link>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'short'
})
</script>

<style scoped>
.site-header { width: 100%; }

/* 顶部工具条 */
.top-bar {
  background: #f0f4fb;
  border-bottom: 1px solid #d0dcf0;
  font-size: 12px;
  color: #5a7099;
}
.top-bar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 5px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.top-links {
  display: flex;
  align-items: center;
  gap: 10px;
}
.top-links a {
  color: #009DE0;
  text-decoration: none;
  font-size: 12px;
}
.top-links a:hover { text-decoration: underline; }
.divider { color: #c0cce0; }

/* 主导航 */
.navbar {
  background: #009DE0;
  box-shadow: 0 2px 8px rgba(0, 157, 224, 0.35);
}
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: white;
}
.brand-icon { font-size: 24px; line-height: 1; }
.brand-main { font-size: 16px; font-weight: 700; letter-spacing: 0.5px; }
.brand-sub { font-size: 10px; opacity: 0.7; letter-spacing: 0.3px; margin-top: 1px; }

.nav-links {
  display: flex;
  gap: 2px;
}
.nav-links a {
  color: rgba(255, 255, 255, 0.88);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.nav-links a:hover {
  background: rgba(255, 255, 255, 0.18);
  color: white;
}
.nav-links a.router-link-active {
  background: rgba(255, 255, 255, 0.22);
  color: white;
  font-weight: 600;
}
</style>
