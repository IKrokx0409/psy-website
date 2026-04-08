<template>
  <div class="shell-page">
    <div class="shell-inner">
      <div class="shell-icon">🕳️</div>
      <h2 class="shell-title">校园树洞</h2>
      <p class="shell-desc">匿名发声，温暖同行。完整树洞功能（发帖、浏览、回应）持续建设中……</p>
      <router-link to="/" class="back-btn">← 返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.shell-page { display: flex; align-items: center; justify-content: center; min-height: 60vh; background: #f8fafc; }
.shell-inner { text-align: center; padding: 60px 40px; }
.shell-icon { font-size: 56px; margin-bottom: 20px; }
.shell-title { font-size: 26px; font-weight: 700; color: #1e293b; margin: 0 0 12px; }
.shell-desc { font-size: 15px; color: #64748b; margin: 0 0 28px; }
.back-btn { display: inline-block; background: #009DE0; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: 500; }
.back-btn:hover { background: #007ab0; }
</style>
