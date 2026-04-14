<template>
  <footer class="site-footer">
    <div class="footer-main">
      <div class="inner">
        <!-- 品牌列 -->
        <div class="footer-col brand-col">
          <div class="footer-brand"><BrainCircuit :size="18" :stroke-width="1.5" /> 心理健康中心</div>
          <p class="footer-intro">
            哈尔滨工业大学（深圳）心理健康教育与咨询中心，
            致力于为全校师生提供专业、温暖的心理健康服务。
          </p>
          <div class="footer-tags">
            <span>专业</span><span>温暖</span><span>保密</span>
          </div>
        </div>

        <!-- 快速导航 -->
        <div class="footer-col">
          <div class="col-title">快速导航</div>
          <ul class="footer-links">
            <li><router-link to="/">网站首页</router-link></li>
            <li><router-link to="/science">心理科普</router-link></li>
            <li><router-link to="/chat">AI 智能疏导</router-link></li>
            <li><router-link to="/diary">情绪日记</router-link></li>
            <li><router-link to="/treehouse">校园树洞</router-link></li>
            <li><router-link to="/appointment">预约咨询</router-link></li>
            <li><router-link to="/about">关于我们</router-link></li>
          </ul>
        </div>

        <!-- 友情链接 -->
        <div class="footer-col">
          <div class="col-title">友情链接</div>
          <ul class="footer-links">
            <li><a href="https://www.hitsz.edu.cn" target="_blank" rel="noopener">哈工大（深圳）官网</a></li>
            <li><a href="#" target="_blank">教育部心理健康指导中心</a></li>
            <li><a href="#" target="_blank">中国心理卫生协会</a></li>
            <li><a href="#" target="_blank">北京心理危机研究与干预中心</a></li>
            <li><a href="#" target="_blank">广东省心理援助热线</a></li>
          </ul>
        </div>

        <!-- 关注我们 -->
        <div class="footer-col">
          <div class="col-title">关注我们</div>
          <div class="qr-placeholder">
            <div class="qr-box">
              <Smartphone :size="32" :stroke-width="1.5" class="qr-icon" />
              <div class="qr-label">微信公众号<br>HITSZ心理中心</div>
            </div>
          </div>
          <div class="hotline">
            <div class="hotline-label">24h 心理援助</div>
            <div class="hotline-number">0755-2603-3002</div>
          </div>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="inner bottom-inner">
        <span>© 2026 哈尔滨工业大学（深圳）心理健康教育与咨询中心</span>
        <span>粤ICP备XXXXXXXX号</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { BrainCircuit, Smartphone } from 'lucide-vue-next'
</script>

<style scoped>
.site-footer { background: #007ab0; color: rgba(255,255,255,0.75); }

.footer-main { padding: 52px 0 40px; }
.inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr;
  gap: 40px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 700;
  color: white;
  margin-bottom: 12px;
}
.footer-intro {
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255,255,255,0.6);
  margin: 0 0 16px;
}
.footer-tags {
  display: flex;
  gap: 8px;
}
.footer-tags span {
  background: rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.7);
  font-size: 11.5px;
  padding: 3px 12px;
  border-radius: 0;
  border: 1px solid rgba(255,255,255,0.2);
}

.col-title {
  font-size: 13.5px;
  font-weight: 600;
  color: white;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.12);
}

.footer-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.footer-links a {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  transition: color 0.15s;
}
.footer-links a:hover { color: white; }

.qr-placeholder { margin-bottom: 16px; }
.qr-box {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 0;
  padding: 14px 20px;
}
.qr-icon { color: rgba(255,255,255,0.7); }
.qr-label { font-size: 11.5px; color: rgba(255,255,255,0.6); text-align: center; line-height: 1.5; }

.hotline-label { font-size: 12px; color: rgba(255,255,255,0.5); margin-bottom: 4px; }
.hotline-number { font-size: 16px; font-weight: 700; color: white; font-family: monospace; letter-spacing: 0.5px; }

/* 底部版权条 */
.footer-bottom {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding: 14px 0;
  font-size: 12px;
  color: rgba(255,255,255,0.4);
}
.bottom-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  grid-template-columns: unset;
  gap: 0;
}
</style>
