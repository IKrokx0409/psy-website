<template>
  <header class="site-header">
    <!-- 顶部工具条 -->
    <div class="top-bar">
      <div class="top-bar-inner">
        <span>哈尔滨工业大学（深圳）· 心理健康教育与咨询中心</span>
        <div class="top-links">
          <a href="https://www.hitsz.edu.cn" target="_blank" rel="noopener">学校官网</a>
          <span class="divider">|</span>
          <a href="#">教务系统</a>
          <span class="divider">|</span>
          <span>{{ currentDate }}</span>
        </div>
      </div>
    </div>

    <!-- 主导航栏 -->
    <nav class="navbar">
      <div class="nav-inner">
        <!-- 左侧：学校 Logo + 中心名称 -->
        <router-link to="/" class="nav-brand">
          <img src="/logos/logo-white.png" alt="哈工大深圳" class="nav-logo" />
          <div class="brand-divider"></div>
          <div class="brand-text">
            <div class="brand-main">心理健康教育与咨询中心</div>
            <div class="brand-sub">Mental Health Education &amp; Counseling Center · HITSZ</div>
          </div>
        </router-link>

        <!-- 右侧：导航链接 -->
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
  max-width: 1280px;
  margin: 0 auto;
  padding: 6px 32px;
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
  box-shadow: 0 2px 6px rgba(0, 120, 180, 0.3);
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
  letter-spacing: 1px;
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
</style>
