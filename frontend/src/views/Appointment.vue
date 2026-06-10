<template>
  <div class="appt-page">

    <!-- 页头 -->
    <div class="appt-header">
      <div class="appt-header-inner">
        <router-link to="/" class="back-link">
          <ChevronLeft :size="15" :stroke-width="2" /> 返回首页
        </router-link>
        <h1 class="appt-title">预约咨询</h1>
        <p class="appt-subtitle">专业、保密、温暖的一对一心理咨询</p>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="appt-body">
      <div class="appt-inner">

        <!-- 说明卡 -->
        <div class="info-card">
          <div class="info-card-icon">
            <CalendarDays :size="28" :stroke-width="1.2" />
          </div>
          <div class="info-card-text">
            <h2 class="info-card-title">线下一对一咨询预约</h2>
            <p class="info-card-desc">
              无论是学业压力、情绪困扰还是人际关系，
              我们的专业咨询师将为你提供保密、温暖、不评判的倾听空间。
            </p>
          </div>
        </div>

        <!-- 联系方式网格 -->
        <div class="contact-grid">
          <div class="contact-card">
            <div class="contact-card-icon">
              <Phone :size="20" :stroke-width="1.5" />
            </div>
            <div class="contact-card-label">电话预约</div>
            <div class="contact-card-value">0755-26400952</div>
            <div class="contact-card-hint">工作时间内拨打</div>
          </div>

          <div class="contact-card">
            <div class="contact-card-icon">
              <Clock :size="20" :stroke-width="1.5" />
            </div>
            <div class="contact-card-label">服务时间</div>
            <div class="contact-card-value">周一至周日</div>
            <div class="contact-card-hint">8:30–11:30 · 13:30–17:00</div>
          </div>

          <div class="contact-card">
            <div class="contact-card-icon">
              <MapPin :size="20" :stroke-width="1.5" />
            </div>
            <div class="contact-card-label">中心地址</div>
            <div class="contact-card-value">H401A</div>
            <div class="contact-card-hint">哈工大（深圳）校区</div>
          </div>
        </div>

        <!-- 流程说明 -->
        <div class="steps-section">
          <h3 class="steps-title">预约流程</h3>
          <div class="steps-list">
            <div class="step-item" v-for="(step, i) in steps" :key="i">
              <div class="step-num">{{ i + 1 }}</div>
              <div class="step-content">
                <div class="step-name">{{ step.name }}</div>
                <div class="step-desc">{{ step.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="appt-footer">
          <router-link to="/" class="back-btn">
            <ChevronLeft :size="14" :stroke-width="2" /> 返回首页
          </router-link>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { CalendarDays, Phone, Clock, MapPin, ChevronLeft } from 'lucide-vue-next'

const steps = [
  { name: '电话或到访预约', desc: '拨打预约电话或直接前往咨询中心说明来访意图' },
  { name: '填写基本信息', desc: '简要说明困扰情况，由工作人员安排合适的咨询师' },
  { name: '确认咨询时间', desc: '工作人员将与您确认具体咨询时间和地点' },
  { name: '开始咨询', desc: '按约前往 H401A，与咨询师进行一对一保密咨询' },
]
</script>

<style scoped>
.appt-page {
  min-height: 100%;
  background: var(--c-beige);
  font-family: var(--f-sans);
}

/* ── 页头 */
.appt-header {
  background: linear-gradient(160deg, #2d5a42 0%, #4a8763 100%);
  padding: 56px 32px 48px;
  border-bottom: 3px solid rgba(255,255,255,0.2);
  box-shadow: 0 2px 6px rgba(30,100,60,0.3);
}
.appt-header-inner { max-width: 760px; margin: 0 auto; }
.back-link {
  display: inline-flex; align-items: center; gap: 4px;
  color: rgba(255,255,255,0.6); text-decoration: none; font-size: 13px;
  margin-bottom: 28px; transition: color var(--t-base);
}
.back-link:hover { color: rgba(255,255,255,0.9); }
.appt-title {
  font-family: var(--f-serif);
  font-size: 40px; font-weight: 900; color: #fff;
  letter-spacing: 6px; margin: 0 0 10px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.appt-subtitle { font-size: 14px; color: rgba(255,255,255,0.6); margin: 0; letter-spacing: 1px; }

/* ── Body */
.appt-body { padding: 48px 32px 80px; }
.appt-inner { max-width: 760px; margin: 0 auto; }

/* ── 信息卡 */
.info-card {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-5);
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-xl);
  padding: var(--sp-6) var(--sp-8);
  margin-bottom: var(--sp-6);
  box-shadow: var(--shadow-sm);
}
.info-card-icon {
  width: 56px; height: 56px;
  border-radius: var(--r-lg);
  background: var(--c-green-pale);
  color: var(--c-green-mid);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.info-card-title {
  font-size: 17px; font-weight: 700; color: var(--c-text-dark);
  margin: 0 0 var(--sp-2);
}
.info-card-desc { font-size: 14px; color: var(--c-text-muted); margin: 0; line-height: 1.75; }

/* ── 联系方式网格 */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--sp-4);
  margin-bottom: var(--sp-8);
}
.contact-card {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  padding: var(--sp-6) var(--sp-5);
  text-align: center;
  box-shadow: var(--shadow-xs);
  transition: transform var(--t-base), box-shadow var(--t-base);
}
.contact-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.contact-card-icon {
  width: 48px; height: 48px;
  border-radius: var(--r-md);
  background: var(--c-green-pale);
  color: var(--c-green-mid);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto var(--sp-3);
}
.contact-card-label { font-size: 11.5px; color: var(--c-text-muted); font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: var(--sp-1); }
.contact-card-value { font-size: 15px; font-weight: 700; color: var(--c-green-deep); margin-bottom: var(--sp-1); }
.contact-card-hint { font-size: 12px; color: var(--c-text-muted); }

/* ── 流程 */
.steps-section {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-xl);
  padding: var(--sp-6) var(--sp-8);
  margin-bottom: var(--sp-6);
  box-shadow: var(--shadow-xs);
}
.steps-title { font-size: 14px; font-weight: 700; color: var(--c-green-deep); letter-spacing: 1px; text-transform: uppercase; margin: 0 0 var(--sp-5); }
.steps-list { display: flex; flex-direction: column; gap: var(--sp-4); }
.step-item { display: flex; align-items: flex-start; gap: var(--sp-4); }
.step-num {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--c-green-deep);
  color: white;
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 2px;
}
.step-name { font-size: 14px; font-weight: 600; color: var(--c-text-dark); margin-bottom: 3px; }
.step-desc { font-size: 13px; color: var(--c-text-muted); line-height: 1.65; }

/* ── 底部 */
.appt-footer { padding-top: var(--sp-5); border-top: 1px solid var(--c-beige-border); }
.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--c-beige);
  border: 1px solid var(--c-beige-border);
  color: var(--c-text-body);
  padding: 9px 20px;
  border-radius: var(--r-sm);
  text-decoration: none; font-size: 13.5px; font-weight: 500;
  transition: background var(--t-base), border-color var(--t-base);
}
.back-btn:hover { background: #eee8de; border-color: #c8b89a; }

@media (max-width: 640px) {
  .appt-header { padding: 40px 20px 36px; }
  .appt-title  { font-size: 28px; }
  .appt-body   { padding: 28px 16px 60px; }
  .contact-grid { grid-template-columns: 1fr; }
  .info-card { flex-direction: column; align-items: center; text-align: center; }
}
</style>
