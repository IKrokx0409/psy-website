<template>
  <div class="shell-page">
    <div class="shell-inner">
      <div class="shell-icon"><Building2 :size="56" :stroke-width="1" /></div>
      <h2 class="shell-title">关于我们</h2>
      <p class="shell-desc">正在跳转至学校官网中心介绍页……</p>
      <a :href="TARGET_URL" class="back-btn" target="_blank" rel="noopener">立即前往 →</a>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Building2 } from 'lucide-vue-next'

const TARGET_URL = 'http://xg.hitsz.edu.cn/xlzx/zxgk1/zxjj.htm'

onMounted(() => {
  window.location.href = TARGET_URL
})
</script>

<style scoped>
.shell-page { display: flex; align-items: center; justify-content: center; min-height: 60vh; background: #f8fafc; }
.shell-inner { text-align: center; padding: 60px 40px; }
.shell-icon { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; color: #009DE0; }
.shell-title { font-size: 26px; font-weight: 700; color: #1e293b; margin: 0 0 12px; }
.shell-desc { font-size: 15px; color: #64748b; margin: 0 0 28px; }
.back-btn { display: inline-block; background: #009DE0; color: white; padding: 10px 24px; border-radius: 2px; text-decoration: none; font-size: 14px; font-weight: 500; }
.back-btn:hover { background: #007ab0; }
</style>
