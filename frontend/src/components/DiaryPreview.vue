<template>
  <section class="diary-preview">
    <div class="inner">

      <!-- 左：图表预览 -->
      <div class="chart-side">
        <div class="chart-header">
          <span class="chart-label">本周情绪追踪</span>
          <span v-if="!isLoggedIn" class="chart-badge">示例数据</span>
          <span v-else-if="loadingDiary" class="chart-badge">加载中…</span>
          <span v-else class="chart-badge chart-badge--real">近 7 天 · 实时</span>
        </div>

        <!-- 骨架屏 -->
        <div v-if="isLoggedIn && loadingDiary" class="chart-skeleton">
          <div v-for="i in 7" :key="i" class="skeleton-bar"></div>
        </div>

        <!-- 无记录提示 -->
        <div v-else-if="isLoggedIn && !loadingDiary && hasNoEntries" class="no-entries">
          <PenLine :size="32" :stroke-width="1" style="opacity:.3" />
          <p>{{ fetchError ? '数据加载失败' : '还没有情绪记录' }}</p>
          <router-link v-if="!fetchError" to="/diary" class="no-entries-link">去写第一篇日记 →</router-link>
        </div>

        <!-- 柱状图 -->
        <template v-else>
          <div class="chart-bars">
            <div v-for="day in displayData" :key="day.label" class="bar-col">
              <div class="bar-wrap">
                <div
                  class="bar-fill"
                  :style="{ height: day.val + '%', background: day.color, opacity: day.empty ? 0.15 : 1 }"
                ></div>
              </div>
              <div class="bar-emoji">{{ day.empty ? '' : day.emoji }}</div>
              <div class="bar-label">{{ day.label }}</div>
            </div>
          </div>
          <div class="legend">
            <span v-for="l in legend" :key="l.name" class="legend-item">
              <span class="legend-dot" :style="{ background: l.color }"></span>{{ l.name }}
            </span>
          </div>
        </template>

        <!-- 未登录蒙层 -->
        <div v-if="!isLoggedIn" class="chart-overlay">
          <router-link to="/login" class="overlay-cta">
            <LogIn :size="14" :stroke-width="1.5" />
            登录后查看你的真实记录
          </router-link>
        </div>
      </div>

      <!-- 右：文案 + 入口 -->
      <div class="text-side">
        <span class="feature-label">情绪日记</span>
        <h2 class="feature-title">记录情绪<br>洞察自己</h2>
        <p class="feature-desc">
          每天花 2 分钟记录当下的情绪状态。通过长期追踪，发现情绪规律，
          找到压力的来源，学会与自己的内心对话。
        </p>
        <ul class="feature-points">
          <li><BarChart2 :size="15" :stroke-width="1.5" /> 可视化周 / 月情绪趋势图</li>
          <li><Lock :size="15" :stroke-width="1.5" /> 数据本地存储，完全私密</li>
          <li><PenLine :size="15" :stroke-width="1.5" /> 支持自由文字记录与情绪打标</li>
          <li><Bell :size="15" :stroke-width="1.5" /> 每日提醒，养成记录习惯</li>
        </ul>
        <router-link to="/diary" class="diary-btn">
          {{ isLoggedIn ? '继续记录情绪' : '开始记录情绪' }}
          <ArrowRight :size="15" :stroke-width="2" />
        </router-link>
      </div>

    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { BarChart2, Lock, PenLine, Bell, LogIn, ArrowRight } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useUserId } from '@/composables/useUserId'
import { getDiaries } from '@/api/diary'

const { isLoggedIn } = useAuth()

const mockData = [
  { label: '周一', val: 60, emoji: '😐', color: '#f59e0b', empty: false },
  { label: '周二', val: 45, emoji: '😔', color: '#ef4444', empty: false },
  { label: '周三', val: 70, emoji: '🙂', color: '#10b981', empty: false },
  { label: '周四', val: 80, emoji: '😊', color: '#10b981', empty: false },
  { label: '周五', val: 55, emoji: '😐', color: '#f59e0b', empty: false },
  { label: '周六', val: 90, emoji: '😄', color: '#5f9e75', empty: false },
  { label: '周日', val: 75, emoji: '🙂', color: '#10b981', empty: false },
]

const realData     = ref([])
const loadingDiary = ref(isLoggedIn.value)
const fetchError   = ref(false)

const scoreToColor = (s) => {
  if (s <= 3) return '#ef4444'
  if (s <= 6) return '#f59e0b'
  if (s <= 8) return '#10b981'
  return '#5f9e75'
}
const scoreToEmoji = (s) => {
  if (s <= 3) return '😔'
  if (s <= 5) return '😐'
  if (s <= 7) return '🙂'
  if (s <= 9) return '😊'
  return '😄'
}
const fmtDate  = (d) => { const mm = String(d.getMonth()+1).padStart(2,'0'); const dd = String(d.getDate()).padStart(2,'0'); return `${d.getFullYear()}-${mm}-${dd}` }
const dayLabel = (d) => ['周日','周一','周二','周三','周四','周五','周六'][d.getDay()]

onMounted(async () => {
  if (!isLoggedIn.value) return
  loadingDiary.value = true
  try {
    const today = new Date()
    const start = new Date(today); start.setDate(today.getDate() - 6)
    const entries = await getDiaries(useUserId(), fmtDate(start), fmtDate(today))
    const map = Object.fromEntries(entries.map(e => [e.date, e]))
    realData.value = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(start); d.setDate(start.getDate() + i)
      const key = fmtDate(d)
      const entry = map[key]
      if (entry) {
        const s = entry.mood_score
        return { label: dayLabel(d), val: s * 10, emoji: scoreToEmoji(s), color: scoreToColor(s), empty: false }
      }
      return { label: dayLabel(d), val: 100, emoji: '', color: '#e2e8f0', empty: true }
    })
  } catch {
    fetchError.value = true
  } finally {
    loadingDiary.value = false
  }
})

const hasNoEntries = computed(() => !loadingDiary.value && (fetchError.value || realData.value.every(d => d.empty)))
const displayData  = computed(() => isLoggedIn.value ? realData.value : mockData)

const legend = [
  { name: '愉悦', color: '#5f9e75' },
  { name: '平静', color: '#10b981' },
  { name: '一般', color: '#f59e0b' },
  { name: '低落', color: '#ef4444' },
]
</script>

<style scoped>
.diary-preview {
  background: linear-gradient(135deg, #2d5a42 0%, #3d6e52 55%, #4a8763 100%);
  padding: var(--sp-16) 0;
  position: relative;
}

.diary-preview::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
}

.inner {
  max-width: var(--container);
  margin: 0 auto;
  padding: 0 var(--sp-6);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 56px;
  align-items: center;
  position: relative;
  z-index: 1;
}

/* ── 图表侧 ────────────────────────────────────────────────── */
.chart-side {
  background: white;
  border-radius: var(--r-xl);
  padding: var(--sp-6);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.22);
  position: relative;
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  margin-bottom: var(--sp-5);
}
.chart-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text-dark);
  letter-spacing: 0.3px;
}

.chart-badge {
  font-size: 11px;
  font-weight: 600;
  background: #f1f5f9;
  color: #94a3b8;
  padding: 2px 8px;
  border-radius: var(--r-pill);
}
.chart-badge--real {
  background: var(--c-green-pale);
  color: var(--c-green-mid);
}

/* 骨架屏 */
.chart-skeleton {
  display: flex;
  gap: var(--sp-3);
  align-items: flex-end;
  height: 140px;
  margin-bottom: var(--sp-3);
}
.skeleton-bar {
  flex: 1;
  height: 60%;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: var(--r-sm);
}
@keyframes shimmer { to { background-position: -200% 0; } }

/* 无记录 */
.no-entries {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-8) 0;
  color: #94a3b8;
  font-size: 14px;
}
.no-entries p { margin: 0; }
.no-entries-link {
  color: var(--c-green-mid);
  font-size: 13px;
  text-decoration: none;
  font-weight: 500;
}
.no-entries-link:hover { text-decoration: underline; }

/* 柱状图 */
.chart-bars {
  display: flex;
  gap: var(--sp-2);
  align-items: flex-end;
  height: 140px;
  margin-bottom: var(--sp-2);
}
.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.bar-wrap {
  width: 100%;
  background: #f1f5f9;
  border-radius: var(--r-sm);
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  height: 100px;
}
.bar-fill {
  width: 100%;
  border-radius: var(--r-xs) var(--r-xs) 0 0;
  transition: height 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.bar-emoji { font-size: 14px; min-height: 18px; }
.bar-label { font-size: 11px; color: #94a3b8; }

.legend { display: flex; gap: var(--sp-4); flex-wrap: wrap; margin-top: var(--sp-3); }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11.5px; color: #64748b; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }

/* 未登录蒙层 */
.chart-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--r-xl);
}
.overlay-cta {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  background: var(--c-green-base);
  color: white;
  padding: 11px 24px;
  border-radius: var(--r-sm);
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  box-shadow: var(--shadow-md);
  transition: background var(--t-base), transform var(--t-base);
}
.overlay-cta:hover { background: var(--c-green-mid); transform: translateY(-1px); }

/* ── 文案侧 ────────────────────────────────────────────────── */
.feature-label {
  display: inline-block;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.28);
  color: rgba(255,255,255,0.9);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: var(--r-pill);
  margin-bottom: var(--sp-4);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.feature-title {
  font-size: 36px;
  font-weight: 700;
  font-family: var(--f-serif);
  color: white;
  line-height: 1.3;
  margin: 0 0 var(--sp-4);
  letter-spacing: 2px;
  text-shadow: 0 2px 16px rgba(0,0,0,0.15);
}

.feature-desc {
  font-size: 14.5px;
  color: rgba(255,255,255,0.75);
  line-height: 1.8;
  margin: 0 0 var(--sp-5);
}

.feature-points {
  list-style: none;
  margin: 0 0 var(--sp-8);
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
}
.feature-points li {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: 14px;
  color: rgba(255,255,255,0.82);
}
.feature-points li svg { color: rgba(255,255,255,0.65); flex-shrink: 0; }

.diary-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  background: white;
  color: #2d5a42;
  padding: 13px 28px;
  border-radius: var(--r-sm);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  transition: box-shadow var(--t-base), transform var(--t-base);
  box-shadow: var(--shadow-lg);
  letter-spacing: 0.3px;
}
.diary-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 36px rgba(0,0,0,0.25); }

@media (max-width: 768px) {
  .inner {
    grid-template-columns: 1fr;
    gap: var(--sp-8);
    padding: 0 var(--sp-5);
  }
  .feature-title { font-size: 28px; }
  .diary-preview { padding: var(--sp-10) 0; }
}

@media (max-width: 480px) {
  .feature-title { font-size: 24px; }
  .feature-points li { font-size: 13px; }
}
</style>
