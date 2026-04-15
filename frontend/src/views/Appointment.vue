<template>
  <div class="shell-page">
    <div class="shell-inner">
      <div class="shell-icon"><CalendarDays :size="56" :stroke-width="1" /></div>
      <h2 class="shell-title">预约咨询</h2>
      <p class="shell-desc">线下一对一心理咨询预约系统，保密、专业、温暖，持续建设中……</p>
      <p class="contact-hint">紧急情况请拨打：<strong>0755-2603-3002</strong>（24h）</p>
      <router-link to="/" class="back-btn">← 返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
import { CalendarDays } from 'lucide-vue-next'
</script>

<style scoped>
.shell-page { display: flex; align-items: center; justify-content: center; min-height: 60vh; background: #f8fafc; }
.shell-inner { text-align: center; padding: 60px 40px; }
.shell-icon { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; color: #5f9e75; }
.shell-title { font-size: 26px; font-weight: 700; color: #1e293b; margin: 0 0 12px; }
.shell-desc { font-size: 15px; color: #64748b; margin: 0 0 10px; }
.contact-hint { font-size: 14px; color: #374151; margin: 0 0 28px; }
.contact-hint strong { color: #5f9e75; }
.back-btn { display: inline-block; background: #5f9e75; color: white; padding: 10px 24px; border-radius: 2px; text-decoration: none; font-size: 14px; font-weight: 500; }
.back-btn:hover { background: #4d8764; }
</style>
