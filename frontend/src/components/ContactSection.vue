<template>
  <section class="contact-section">
    <div class="inner">
      <div class="section-title-wrap">
        <h2 class="section-title">联系我们</h2>
        <p class="section-sub">预约咨询、紧急援助或其他事宜，欢迎通过以下方式联系</p>
      </div>

      <div class="contact-grid">
        <div class="contact-card" v-for="item in contacts" :key="item.title">
          <div class="contact-icon"><component :is="item.icon" :size="28" :stroke-width="1.5" /></div>
          <div class="contact-title">{{ item.title }}</div>
          <div class="contact-body">
            <div v-for="line in item.lines" :key="line" class="contact-line">{{ line }}</div>
          </div>
        </div>
      </div>

      <div class="appointment-banner">
        <div class="banner-text">
          <strong>预约线下心理咨询</strong>
          <span>专业老师一对一倾听，保密、温暖、不评判</span>
        </div>
        <router-link to="/appointment" class="appt-btn">立即预约 →</router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { MapPin, Phone, Clock, Mail } from 'lucide-vue-next'

const contacts = [
  {
    icon: MapPin,
    title: '中心地址',
    lines: ['深圳市南山区学苑大道 1688 号', '哈工大深圳校区 学生服务中心 3 楼 301 室'],
  },
  {
    icon: Phone,
    title: '联系电话',
    lines: ['预约咨询：0755-2603-3001', '危机援助（24h）：0755-2603-3002'],
  },
  {
    icon: Clock,
    title: '工作时间',
    lines: ['周一 ~ 周五 09:00–12:00', '周一 ~ 周五 14:00–17:00', '（节假日除外）'],
  },
  {
    icon: Mail,
    title: '联系邮箱',
    lines: ['mhc@hitsz.edu.cn', '微信公众号：HITSZ心理中心'],
  },
]
</script>

<style scoped>
.contact-section {
  background: #e8f8ff;
  padding: 64px 0;
  border-top: 1px solid #d0f0fb;
}
.inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.section-title-wrap {
  text-align: center;
  margin-bottom: 40px;
}
.section-title {
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}
.section-sub {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.contact-card {
  background: white;
  border: 1px solid #d0f0fb;
  border-radius: 0;
  padding: 24px 20px;
  text-align: center;
  transition: transform 0.15s, box-shadow 0.15s;
}
.contact-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 157, 224,0.1);
}

.contact-icon { display: flex; align-items: center; justify-content: center; margin-bottom: 10px; color: #009DE0; }
.contact-title {
  font-size: 14px;
  font-weight: 600;
  color: #009DE0;
  margin-bottom: 10px;
}
.contact-line {
  font-size: 13px;
  color: #374151;
  line-height: 1.7;
}

/* 预约横幅 */
.appointment-banner {
  background: #009DE0;
  border-radius: 0;
  padding: 22px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.banner-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: white;
}
.banner-text strong { font-size: 16px; font-weight: 600; }
.banner-text span { font-size: 13.5px; opacity: 0.82; }

.appt-btn {
  display: inline-block;
  background: white;
  color: #009DE0;
  padding: 10px 26px;
  border-radius: 2px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition: transform 0.15s;
}
.appt-btn:hover { transform: translateY(-1px); }
</style>
