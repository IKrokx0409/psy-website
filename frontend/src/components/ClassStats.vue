<template>
  <div class="cs-wrap">

    <!-- ── 控制栏 ── -->
    <div class="cs-controls">
      <div class="cs-control-group">
        <label class="cs-label">查看范围</label>
        <div class="cs-seg">
          <button
            :class="['cs-seg-btn', { active: scope === 'class' }]"
            @click="scope = 'class'"
          >本班</button>
          <button
            :class="['cs-seg-btn', { active: scope === 'all' }]"
            @click="scope = 'all'"
          >全部班级</button>
        </div>
      </div>

      <div class="cs-control-group">
        <label class="cs-label">情绪低落阈值</label>
        <div class="cs-threshold-row">
          <span class="cs-threshold-prefix">≤</span>
          <select v-model.number="threshold" class="cs-select">
            <option v-for="v in [2,3,4,5,6]" :key="v" :value="v">{{ v }} 分</option>
          </select>
        </div>
      </div>

      <div class="cs-spacer" />

      <div class="cs-legend">
        <span class="cs-legend-item">
          <span class="cs-dot cs-dot--empty"></span>无记录
        </span>
        <span class="cs-legend-item">
          <span class="cs-dot cs-dot--good"></span>情绪正常
        </span>
        <span class="cs-legend-item">
          <span class="cs-dot cs-dot--mid"></span>少量偏低
        </span>
        <span class="cs-legend-item">
          <span class="cs-dot cs-dot--bad"></span>偏低较多
        </span>
      </div>
    </div>

    <!-- ── 日历 + 详情 ── -->
    <div class="cs-main">

      <!-- 日历区域 -->
      <div class="cs-cal-section">

        <!-- 月份导航 -->
        <div class="cs-month-nav">
          <button class="cs-nav-btn" @click="prevMonth">
            <ChevronLeft :size="16" :stroke-width="2" />
          </button>
          <span class="cs-month-label">{{ calYear }}年{{ calMonth + 1 }}月</span>
          <button class="cs-nav-btn" @click="nextMonth">
            <ChevronRight :size="16" :stroke-width="2" />
          </button>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="cs-cal-loading">
          <Loader2 :size="22" :stroke-width="1.5" class="spin" /><span>加载中…</span>
        </div>

        <template v-else>
          <!-- 星期头 -->
          <div class="cs-cal-grid">
            <div class="cs-dow" v-for="d in ['日','一','二','三','四','五','六']" :key="d">{{ d }}</div>

            <!-- 日期格 -->
            <template v-for="(cell, i) in calCells" :key="i">
              <div v-if="!cell.date" class="cs-cell-empty" />
              <button
                v-else
                :class="[
                  'cs-cell',
                  `cs-cell--${cell.color}`,
                  { 'cs-cell--today': cell.isToday, 'cs-cell--selected': cell.isSelected }
                ]"
                @click="selectDay(cell)"
              >
                <span class="cs-cell-day">{{ cell.day }}</span>
                <span v-if="cell.stats?.diary_count" class="cs-cell-badge">
                  {{ cell.stats.diary_count }}
                </span>
              </button>
            </template>
          </div>

          <!-- 摘要行 -->
          <div class="cs-month-summary" v-if="!loading && monthlyData">
            <span>本月累计记录日记：<strong>{{ monthDiaryTotal }}</strong> 次</span>
            <span>情绪偏低记录：<strong class="cs-warn-num">{{ monthLowTotal }}</strong> 次</span>
            <span>AI 对话：<strong>{{ monthChatTotal }}</strong> 次</span>
          </div>
        </template>
      </div>

      <!-- 详情面板 -->
      <div class="cs-detail">
        <div v-if="!selectedDay" class="cs-detail-empty">
          <CalendarDays :size="40" :stroke-width="1" style="opacity:.2" />
          <span>点击左侧日历查看当日详情</span>
        </div>

        <template v-else>
          <div class="cs-detail-date">
            {{ detailDateLabel }}
            <span class="cs-detail-scope">
              {{ scope === 'class' ? '本班' : '全部班级' }} · 共 {{ monthlyData?.student_total ?? 0 }} 名学生
            </span>
          </div>

          <!-- 情绪日记卡 -->
          <div class="cs-stat-card">
            <div class="cs-stat-head">
              <BookOpen :size="16" :stroke-width="1.5" class="cs-stat-icon cs-stat-icon--diary" />
              <span class="cs-stat-title">情绪日记</span>
              <span class="cs-stat-num">
                {{ selectedDay.diary_count }}
                <span class="cs-stat-total">/ {{ monthlyData?.student_total ?? '?' }} 人</span>
              </span>
            </div>

            <div class="cs-prog-wrap">
              <div class="cs-prog-bar">
                <div
                  class="cs-prog-fill cs-prog-fill--diary"
                  :style="{ width: diaryPct + '%' }"
                />
              </div>
              <span class="cs-prog-label">{{ diaryPct }}%</span>
            </div>

            <div class="cs-stat-detail">
              今日记录日记：<strong>{{ selectedDay.diary_count }}</strong> 人
              <template v-if="selectedDay.diary_count > 0">
                ，其中情绪偏低（≤{{ threshold }}分）：
                <strong :class="selectedDay.diary_low_mood_count > 0 ? 'cs-warn' : ''">
                  {{ selectedDay.diary_low_mood_count }}
                </strong> 人
              </template>
            </div>

            <!-- 低情绪条 -->
            <div v-if="selectedDay.diary_low_mood_count > 0" class="cs-low-bar-wrap">
              <div class="cs-low-label">
                <AlertTriangle :size="12" :stroke-width="2" class="cs-warn" />
                情绪偏低占比
              </div>
              <div class="cs-prog-bar cs-prog-bar--sm">
                <div
                  class="cs-prog-fill cs-prog-fill--low"
                  :style="{ width: diaryLowPct + '%' }"
                />
              </div>
              <span class="cs-prog-label cs-warn">{{ diaryLowPct }}%</span>
            </div>
          </div>

          <!-- AI对话卡 -->
          <div class="cs-stat-card">
            <div class="cs-stat-head">
              <BotMessageSquare :size="16" :stroke-width="1.5" class="cs-stat-icon cs-stat-icon--chat" />
              <span class="cs-stat-title">AI 情绪对话</span>
              <span class="cs-stat-num">
                {{ selectedDay.chat_count }}
                <span class="cs-stat-total">/ {{ monthlyData?.student_total ?? '?' }} 人</span>
              </span>
            </div>

            <div class="cs-prog-wrap">
              <div class="cs-prog-bar">
                <div
                  class="cs-prog-fill cs-prog-fill--chat"
                  :style="{ width: chatPct + '%' }"
                />
              </div>
              <span class="cs-prog-label">{{ chatPct }}%</span>
            </div>

            <div class="cs-stat-detail">
              今日与 AI 对话：<strong>{{ selectedDay.chat_count }}</strong> 人
              <template v-if="selectedDay.chat_count > 0">
                ，其中情绪偏低（参照当日日记）：
                <strong :class="selectedDay.chat_low_mood_count > 0 ? 'cs-warn' : ''">
                  {{ selectedDay.chat_low_mood_count }}
                </strong> 人
              </template>
            </div>

            <div v-if="selectedDay.chat_count === 0" class="cs-no-data">
              今日暂无学生使用 AI 对话
            </div>
          </div>

          <div class="cs-privacy-note">
            <Lock :size="12" :stroke-width="1.5" />
            以上均为匿名聚合数据，不含具体学生信息
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  ChevronLeft, ChevronRight, Loader2, CalendarDays,
  BookOpen, BotMessageSquare, AlertTriangle, Lock,
} from 'lucide-vue-next'
import { fetchMonthlyStats } from '@/api/stats'

const props = defineProps({
  classId:   { type: Number,  required: true },
  teacherId: { type: String,  required: true },
})

// ── 控制 ─────────────────────────────────────────────────────────────────────
const scope     = ref('class')   // 'class' | 'all'
const threshold = ref(4)

// ── 日历状态 ──────────────────────────────────────────────────────────────────
const today    = new Date()
const calYear  = ref(today.getFullYear())
const calMonth = ref(today.getMonth())    // 0-indexed

const prevMonth = () => {
  if (calMonth.value === 0) { calMonth.value = 11; calYear.value-- }
  else calMonth.value--
}
const nextMonth = () => {
  if (calMonth.value === 11) { calMonth.value = 0; calYear.value++ }
  else calMonth.value++
}

// ── 数据 ──────────────────────────────────────────────────────────────────────
const loading     = ref(false)
const monthlyData = ref(null)
const selectedDay = ref(null)

const todayStr = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`

const loadData = async () => {
  loading.value = true
  selectedDay.value = null
  try {
    monthlyData.value = await fetchMonthlyStats({
      year:      calYear.value,
      month:     calMonth.value + 1,
      threshold: threshold.value,
      classId:   scope.value === 'class' ? props.classId : undefined,
      teacherId: scope.value === 'all'   ? props.teacherId : undefined,
    })
  } catch {
    monthlyData.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
watch([scope, threshold, calYear, calMonth], loadData)

// ── 日历格 ────────────────────────────────────────────────────────────────────
const statsMap = computed(() => {
  const m = {}
  for (const d of monthlyData.value?.days ?? []) m[d.date] = d
  return m
})

const calCells = computed(() => {
  const y = calYear.value
  const mo = calMonth.value
  const firstDow = new Date(y, mo, 1).getDay()
  const dim = new Date(y, mo + 1, 0).getDate()
  const cells = []

  for (let i = 0; i < firstDow; i++) cells.push({ date: null })

  for (let d = 1; d <= dim; d++) {
    const ds = `${y}-${String(mo+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const stats = statsMap.value[ds]
    cells.push({
      day: d,
      date: ds,
      stats,
      color: cellColor(stats),
      isToday:    ds === todayStr,
      isSelected: selectedDay.value?.date === ds,
    })
  }
  return cells
})

const cellColor = (stats) => {
  if (!stats || stats.diary_count === 0) return 'empty'
  if (stats.diary_low_mood_count === 0)  return 'good'
  if (stats.diary_low_mood_count <= 2)   return 'mid'
  return 'bad'
}

const selectDay = (cell) => {
  if (!cell.date) return
  selectedDay.value = cell.stats
    ? { ...cell.stats, date: cell.date }
    : { date: cell.date, diary_count: 0, diary_low_mood_count: 0, chat_count: 0, chat_low_mood_count: 0 }
}

// ── 月度汇总 ──────────────────────────────────────────────────────────────────
const monthDiaryTotal = computed(() =>
  (monthlyData.value?.days ?? []).reduce((s, d) => s + d.diary_count, 0)
)
const monthLowTotal = computed(() =>
  (monthlyData.value?.days ?? []).reduce((s, d) => s + d.diary_low_mood_count, 0)
)
const monthChatTotal = computed(() =>
  (monthlyData.value?.days ?? []).reduce((s, d) => s + d.chat_count, 0)
)

// ── 详情面板 ──────────────────────────────────────────────────────────────────
const detailDateLabel = computed(() => {
  if (!selectedDay.value) return ''
  const [y, m, d] = selectedDay.value.date.split('-')
  const dow = ['日','一','二','三','四','五','六'][new Date(+y, +m-1, +d).getDay()]
  return `${+m}月${+d}日（周${dow}）`
})

const total = computed(() => monthlyData.value?.student_total ?? 0)

const diaryPct    = computed(() => total.value ? Math.round((selectedDay.value?.diary_count ?? 0) / total.value * 100) : 0)
const chatPct     = computed(() => total.value ? Math.round((selectedDay.value?.chat_count ?? 0) / total.value * 100) : 0)
const diaryLowPct = computed(() => {
  const dc = selectedDay.value?.diary_count
  const lc = selectedDay.value?.diary_low_mood_count
  return dc ? Math.round(lc / dc * 100) : 0
})
</script>

<style scoped>
/* ── 整体 ── */
.cs-wrap {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

/* ── 控制栏 ── */
.cs-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  padding: 14px 18px;
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
}
.cs-control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cs-label {
  font-size: 12px;
  font-weight: 600;
  color: #4a8763;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.cs-seg {
  display: flex;
  border: 1px solid #d4e8db;
  border-radius: 6px;
  overflow: hidden;
}
.cs-seg-btn {
  padding: 5px 14px;
  font-size: 13px;
  border: none;
  background: none;
  color: #5a7060;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.cs-seg-btn.active {
  background: #3d6e52;
  color: white;
  font-weight: 600;
}
.cs-threshold-row {
  display: flex;
  align-items: center;
  gap: 4px;
}
.cs-threshold-prefix { font-size: 13px; color: #5a7060; font-weight: 600; }
.cs-select {
  border: 1px solid #d4e8db;
  border-radius: 5px;
  padding: 4px 8px;
  font-size: 13px;
  color: #1c2b22;
  background: #fdfaf5;
  cursor: pointer;
  outline: none;
}
.cs-spacer { flex: 1; }
.cs-legend {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.cs-legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #7a9080;
  white-space: nowrap;
}
.cs-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}
.cs-dot--empty { background: #e8e3da; }
.cs-dot--good  { background: #b8e0c8; }
.cs-dot--mid   { background: #fde68a; }
.cs-dot--bad   { background: #fca5a5; }

/* ── 主区域 ── */
.cs-main {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* ── 日历 ── */
.cs-cal-section {
  width: 320px;
  min-width: 320px;
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  padding: 16px;
}
.cs-cal-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 180px;
  color: #94a3b8;
  font-size: 13px;
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.cs-month-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.cs-nav-btn {
  background: none;
  border: 1px solid #d8d2c8;
  border-radius: 5px;
  padding: 4px 8px;
  cursor: pointer;
  color: #5a7060;
  display: flex;
  transition: background 0.15s;
}
.cs-nav-btn:hover { background: #f0ebe2; }
.cs-month-label {
  font-size: 15px;
  font-weight: 700;
  color: #1c2b22;
  font-family: var(--f-serif, serif);
  letter-spacing: 1px;
}

.cs-cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
}
.cs-dow {
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  padding: 4px 0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.cs-cell-empty { height: 38px; }

.cs-cell {
  position: relative;
  height: 38px;
  border-radius: 6px;
  border: 1.5px solid transparent;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1px;
  transition: border-color 0.15s, transform 0.1s;
}
.cs-cell:hover { border-color: #4a8763; transform: scale(1.05); }
.cs-cell--today { border-color: #4a8763 !important; border-width: 2px; }
.cs-cell--selected { border-color: #2d5a42 !important; border-width: 2px; box-shadow: 0 0 0 2px rgba(74,135,99,0.15); }

/* color variants */
.cs-cell--empty { background: #f6f2ec; }
.cs-cell--good  { background: #d1f0dd; }
.cs-cell--mid   { background: #fef3c7; }
.cs-cell--bad   { background: #fee2e2; }

.cs-cell-day  { font-size: 12.5px; font-weight: 600; color: #1c2b22; line-height: 1; }
.cs-cell-badge {
  font-size: 9.5px;
  font-weight: 700;
  color: rgba(0,0,0,0.45);
  line-height: 1;
}
.cs-cell--good .cs-cell-badge  { color: #3d6e52; }
.cs-cell--mid  .cs-cell-badge  { color: #92400e; }
.cs-cell--bad  .cs-cell-badge  { color: #b91c1c; }

.cs-month-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #e8e0d4;
  margin-top: 12px;
  font-size: 12px;
  color: #7a9080;
}
.cs-month-summary strong { color: #1c2b22; }

/* ── 详情面板 ── */
.cs-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.cs-detail-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: #b0bec5;
  font-size: 13px;
}

.cs-detail-date {
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #1c2b22;
  font-family: var(--f-serif, serif);
}
.cs-detail-scope {
  font-size: 12px;
  color: #7a9080;
  font-family: var(--f-sans);
  font-weight: 400;
}

.cs-stat-card {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.cs-stat-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cs-stat-icon { flex-shrink: 0; }
.cs-stat-icon--diary { color: #4a8763; }
.cs-stat-icon--chat  { color: #5a7ec4; }
.cs-stat-title {
  flex: 1;
  font-size: 14px;
  font-weight: 700;
  color: #1c2b22;
}
.cs-stat-num {
  font-size: 22px;
  font-weight: 800;
  color: #1c2b22;
  font-variant-numeric: tabular-nums;
}
.cs-stat-total {
  font-size: 13px;
  font-weight: 400;
  color: #94a3b8;
}

.cs-prog-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.cs-prog-bar {
  flex: 1;
  height: 8px;
  background: #e8e0d4;
  border-radius: 4px;
  overflow: hidden;
}
.cs-prog-bar--sm { height: 5px; }
.cs-prog-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}
.cs-prog-fill--diary { background: #4a8763; }
.cs-prog-fill--chat  { background: #5a7ec4; }
.cs-prog-fill--low   { background: #f59e0b; }
.cs-prog-label {
  font-size: 12px;
  color: #7a9080;
  font-weight: 600;
  min-width: 36px;
  text-align: right;
}

.cs-stat-detail {
  font-size: 13.5px;
  color: #374151;
  line-height: 1.6;
}
.cs-stat-detail strong { color: #1c2b22; }

.cs-low-bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff8ed;
  border-radius: 6px;
  border: 1px solid rgba(245,158,11,0.25);
}
.cs-low-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #92400e;
  white-space: nowrap;
}

.cs-no-data {
  font-size: 13px;
  color: #b0bec5;
  font-style: italic;
  padding: 4px 0;
}

.cs-warn     { color: #d97706; }
.cs-warn-num { color: #b91c1c; }

.cs-privacy-note {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #94a3b8;
  padding: 8px 12px;
  background: #f6f2ec;
  border-radius: 6px;
  border: 1px solid #e8e0d4;
}

/* ── 响应式 ── */
@media (max-width: 860px) {
  .cs-main { flex-direction: column; }
  .cs-cal-section { width: 100%; min-width: unset; }
  .cs-controls { gap: 12px; }
  .cs-spacer { display: none; }
}
</style>
