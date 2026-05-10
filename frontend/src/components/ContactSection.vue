<template>
  <section class="contact-section">
    <div class="inner">
      <div class="section-header">
        <span class="section-label">联系</span>
        <h2 class="section-title">联系我们</h2>
        <p class="section-sub">预约咨询、紧急援助或其他事宜，欢迎通过以下方式联系</p>
      </div>

      <div class="contact-grid">
        <div class="contact-card" v-for="item in contacts" :key="item.title">
          <div class="contact-icon-wrap">
            <component :is="item.icon" :size="22" :stroke-width="1.5" />
          </div>
          <div class="contact-title">{{ item.title }}</div>
          <div class="contact-body">
            <div v-for="line in item.lines" :key="line" class="contact-line">{{ line }}</div>
          </div>
        </div>
      </div>

      <div class="appointment-banner">
        <div class="banner-deco" aria-hidden="true">
          <svg width="220" height="80" viewBox="0 0 220 80" fill="none">
            <circle cx="0"   cy="40" r="60"  fill="white" fill-opacity="0.04"/>
            <circle cx="220" cy="40" r="50"  fill="white" fill-opacity="0.04"/>
            <circle cx="110" cy="0"  r="40"  fill="white" fill-opacity="0.03"/>
          </svg>
        </div>
        <div class="banner-content">
          <div class="banner-text">
            <strong>预约线下心理咨询</strong>
            <span>专业老师一对一倾听，保密、温暖、不评判</span>
          </div>
          <router-link to="/appointment" class="appt-btn">
            立即预约
            <ArrowRight :size="14" :stroke-width="2.5" />
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { MapPin, Phone, Clock, MessageCircle, ArrowRight } from 'lucide-vue-next'

const contacts = [
  { icon: MapPin,          title: '中心地址',   lines: ['哈工大（深圳）校区', 'H401A'] },
  { icon: Phone,           title: '联系电话',   lines: ['预约咨询：0755-26400952'] },
  { icon: Clock,           title: '工作时间',   lines: ['周一至周日', '8:30–11:30  /  13:30–17:00'] },
  { icon: MessageCircle,   title: '微信公众号', lines: ['小嗨森'] },
]
</script>

<style scoped>
.contact-section {
  background: var(--c-green-pale);
  padding: var(--sp-16) 0;
  border-top: 1px solid #c8e3d4;
}

.inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
}

/* 章节头 */
.section-header {
  text-align: center;
  margin-bottom: var(--sp-10);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sp-3);
}

.section-label {
  display: inline-block;
  background: var(--c-green-pale);
  color: var(--c-green-deep);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: var(--r-pill);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--c-text-dark);
  font-family: var(--f-serif);
  letter-spacing: 1.5px;
  margin: 0;
}

.section-sub {
  font-size: 14px;
  color: var(--c-text-muted);
  margin: 0;
}

/* 联系卡网格 */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--sp-4);
  margin-bottom: var(--sp-8);
}

.contact-card {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  padding: var(--sp-6) var(--sp-5);
  text-align: center;
  transition: transform var(--t-base), box-shadow var(--t-base);
  box-shadow: var(--shadow-xs);
}
.contact-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.contact-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: var(--r-md);
  background: var(--c-green-pale);
  color: var(--c-green-mid);
  margin: 0 auto var(--sp-3);
}

.contact-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--c-green-deep);
  margin-bottom: var(--sp-2);
  letter-spacing: 0.5px;
}

.contact-line {
  font-size: 12.5px;
  color: var(--c-text-body);
  line-height: 1.8;
}

/* 预约横幅 */
.appointment-banner {
  background: linear-gradient(135deg, #2d5a42 0%, #4a8763 100%);
  border-radius: var(--r-xl);
  padding: var(--sp-6) var(--sp-8);
  position: relative;
  overflow: hidden;
}

.banner-deco {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.banner-deco svg {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  preserveAspectRatio: none;
}

.banner-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-5);
}

.banner-text {
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
  color: white;
}
.banner-text strong { font-size: 17px; font-weight: 700; letter-spacing: 0.5px; }
.banner-text span   { font-size: 13.5px; opacity: 0.78; }

.appt-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  background: white;
  color: var(--c-green-deep);
  padding: 12px 28px;
  border-radius: var(--r-sm);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
  transition: transform var(--t-base), box-shadow var(--t-base);
  box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  letter-spacing: 0.3px;
}
.appt-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(0,0,0,0.22); }
</style>
