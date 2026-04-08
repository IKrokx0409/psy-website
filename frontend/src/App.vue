<template>
  <div class="app-container">
    <nav class="navbar">
      <h1>HITSZ 心理中心</h1>
      <div class="nav-links">
        <router-link to="/">大厅首页</router-link>
        <router-link to="/chat">AI 聊天</router-link>
        <router-link to="/diary">情绪日记</router-link>
      </div>
    </nav>

    <div class="content-area">
      <router-view></router-view>
    </div>
  </div>
</template>

<style scoped>
.app-container { font-family: sans-serif; color: #333; }
.navbar { 
  display: flex; justify-content: space-between; align-items: center; 
  background-color: #2c3e50; color: white; padding: 10px 30px; 
}
.nav-links a {
  color: white; text-decoration: none; margin-left: 20px; font-weight: bold;
}
.nav-links a:hover { color: #4CAF50; }
.content-area { padding: 40px; text-align: center; }
</style>