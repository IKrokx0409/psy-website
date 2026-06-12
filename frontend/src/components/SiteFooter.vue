<template>
  <footer class="site-footer">
    <div class="footer-main">
      <div class="inner">
        <!-- 品牌列 -->
        <div class="footer-col brand-col">
          <div class="footer-brand">
            <BrainCircuit :size="18" :stroke-width="1.5" />
            大学生心理健康支持平台
          </div>
          <p class="footer-intro">
            哈尔滨工业大学（深圳）大学生心理健康自助支持平台，
            提供心理资源、情绪疏导与预约咨询服务，与同学们共同守护心理健康。
          </p>
          <div class="footer-tags">
            <span>专业</span>
            <span>温暖</span>
            <span>保密</span>
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
          <div class="qr-block">
            <img src="/wechat-qr.png" alt="小嗨森微信公众号二维码" class="qr-img" />
            <div class="qr-label">扫码关注 · 小嗨森</div>
          </div>
          <div class="hotline">
            <div class="hotline-label">预约咨询电话</div>
            <div class="hotline-number">0755-26400952</div>
          </div>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="inner bottom-inner">
        <span>© 2026 HITSZ 大学生心理健康支持平台</span>
        <span>粤ICP备XXXXXXXX号</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { BrainCircuit } from 'lucide-vue-next'
</script>

<style scoped>
.site-footer {
  background: #1a3827;
  color: rgba(255,255,255,0.65);
}

.footer-main {
  padding: var(--sp-16) 0 var(--sp-10);
  border-top: 1px solid rgba(255,255,255,0.06);
}

.inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr;
  gap: var(--sp-10);
}

/* 品牌 */
.footer-brand {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: 16px;
  font-weight: 700;
  color: white;
  margin-bottom: var(--sp-3);
  font-family: var(--f-serif);
  letter-spacing: 1px;
}

.footer-intro {
  font-size: 12.5px;
  line-height: 1.75;
  color: rgba(255,255,255,0.45);
  margin: 0 0 var(--sp-4);
}

.footer-tags {
  display: flex;
  gap: var(--sp-2);
}
.footer-tags span {
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.6);
  font-size: 11px;
  font-weight: 600;
  padding: 3px 12px;
  border-radius: var(--r-pill);
  border: 1px solid rgba(255,255,255,0.12);
  letter-spacing: 0.8px;
}

/* 列标题 */
.col-title {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255,255,255,0.85);
  margin-bottom: var(--sp-4);
  padding-bottom: var(--sp-2);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.footer-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}
.footer-links a {
  font-size: 13px;
  color: rgba(255,255,255,0.45);
  text-decoration: none;
  transition: color var(--t-base);
  display: flex;
  align-items: center;
}
.footer-links a:hover { color: rgba(255,255,255,0.85); }

/* QR 占位 */
.qr-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--sp-2);
  margin-bottom: var(--sp-4);
}
.qr-img {
  width: 100px;
  height: 100px;
  border-radius: var(--r-sm);
  display: block;
}
.qr-label {
  font-size: 11px;
  color: rgba(255,255,255,0.45);
  line-height: 1.6;
}

/* 热线 */
.hotline-label { font-size: 11.5px; color: rgba(255,255,255,0.35); margin-bottom: var(--sp-1); }
.hotline-number {
  font-size: 17px;
  font-weight: 700;
  color: white;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
}

/* 底部版权条 */
.footer-bottom {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: var(--sp-4) 0;
  font-size: 11.5px;
  color: rgba(255,255,255,0.3);
}
.bottom-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  grid-template-columns: unset;
  gap: 0;
}

@media (max-width: 900px) {
  .inner { grid-template-columns: 1fr 1fr; gap: var(--sp-8); }
}

@media (max-width: 600px) {
  .inner { grid-template-columns: 1fr; gap: var(--sp-6); }
  .footer-main { padding: var(--sp-10) 0 var(--sp-6); }
  .qr-block { flex-direction: row; align-items: center; }
  .bottom-inner { flex-direction: column; gap: var(--sp-2); text-align: center; }
}
</style>
