<template>
  <div class="diary-page">
    <div class="diary-inner">

      <!-- ── 左列：编辑器 ── -->
      <div class="left-col">
        <div class="card editor-card">
          <div class="card-title">
            <BookHeart :size="15" :stroke-width="1.5" />
            情绪记录
          </div>

          <div class="fields-scroll">

            <!-- 日期 -->
            <div class="field-row">
              <label class="field-label">日期</label>
              <input type="date" v-model="form.date" class="date-input" :max="today" />
            </div>

            <div class="field-divider"></div>

            <!-- 情绪评分 -->
            <div class="field-row">
              <label class="field-label">
                今日心情
                <span class="score-badge" :style="{ background: scoreBg }">{{ form.mood_score }}</span>
                <span class="score-label-text">{{ moodLabel }}</span>
              </label>
              <div class="slider-wrap">
                <span class="slider-end">低落</span>
                <input
                  type="range" min="1" max="10"
                  v-model.number="form.mood_score"
                  class="mood-slider"
                  :style="sliderStyle"
                />
                <span class="slider-end">愉悦</span>
              </div>
              <div class="slider-ticks">
                <span v-for="n in 10" :key="n" :class="['tick', { active: n <= form.mood_score }]">{{ n }}</span>
              </div>
            </div>

            <div class="field-divider"></div>

            <!-- 情绪标签 -->
            <div class="field-row">
              <label class="field-label">情绪标签</label>
              <div class="tag-grid">
                <button
                  v-for="tag in emotionOptions" :key="tag.label"
                  :class="['tag-btn', `tag-${tag.type}`, { selected: form.emotions.includes(tag.label) }]"
                  @click="toggleTag(tag.label)"
                >{{ tag.label }}</button>
              </div>
            </div>

            <div class="field-divider"></div>

            <!-- 今日记录 -->
            <div class="field-row field-row--grow">
              <label class="field-label">今日记录</label>
              <textarea
                v-model="form.content"
                class="diary-textarea"
                placeholder="写下今天的心情……"
              ></textarea>
            </div>

          </div>

          <div class="editor-actions">
            <button class="btn-delete" v-if="currentEntryId" @click="handleDelete">
              <Trash2 :size="12" :stroke-width="1.5" /> 删除
            </button>
            <button class="btn-save" @click="handleSave" :disabled="saving">
              <Save :size="12" :stroke-width="1.5" />
              {{ saving ? '保存中…' : (currentEntryId ? '更新' : '保存') }}
            </button>
          </div>
          <p v-if="saveMsg" class="save-msg" :class="saveMsgType">{{ saveMsg }}</p>
        </div>
      </div>

      <!-- ── 右列 ── -->
      <div class="right-col">

        <div class="right-top">

          <!-- 日历 -->
          <div class="card calendar-card">
            <div class="card-title">
              <CalendarDays :size="15" :stroke-width="1.5" />
              情绪日历
              <div class="cal-nav">
                <button class="cal-arrow" @click="prevMonth"><ChevronLeft :size="13" /></button>
                <span class="cal-month">{{ calYear }}.{{ String(calMonth + 1).padStart(2,'0') }}</span>
                <button class="cal-arrow" @click="nextMonth"><ChevronRight :size="13" /></button>
              </div>
            </div>

            <div class="cal-grid">
              <div class="cal-dow" v-for="d in ['日','一','二','三','四','五','六']" :key="d">{{ d }}</div>
              <div v-for="(cell, i) in calCells" :key="i" class="cal-cell-wrap">
                <button
                  v-if="cell.date"
                  :class="['cal-circle', { 'has-entry': !!cell.color, 'is-today': cell.isToday, 'is-selected': cell.isSelected }]"
                  :style="cell.color ? { background: cell.color } : {}"
                  @click="loadEntry(cell.date)"
                >{{ cell.day }}</button>
                <span v-else class="cal-empty-cell"></span>
              </div>
            </div>

            <div class="cal-legend">
              <span v-for="l in scoreLegend" :key="l.label" class="legend-item">
                <span class="legend-dot" :style="{ background: l.color }"></span>{{ l.label }}
              </span>
            </div>
          </div>

          <!-- AI 反馈 -->
          <div class="card ai-card">
            <div class="card-title">
              <Sparkles :size="15" :stroke-width="1.5" />
              AI 心理反馈
              <span class="coming-soon">即将上线</span>
            </div>
            <div class="ai-body">
              <div class="ai-avatar">
                <BrainCircuit :size="28" :stroke-width="1" />
              </div>
              <p class="ai-tip">AI 将根据您的情绪记录，提供个性化的心理支持建议。</p>
              <p class="ai-sub">正在接入 HiAgent 工作流，敬请期待。</p>
            </div>
          </div>

        </div>

        <!-- 情绪曲线 -->
        <div class="card chart-card">
          <div class="card-title">
            <TrendingUp :size="15" :stroke-width="1.5" />
            情绪曲线
            <div class="range-tabs">
              <button
                v-for="r in [7, 30, 90]" :key="r"
                :class="['range-tab', { active: chartRange === r }]"
                @click="setRange(r)"
              >{{ r }}天</button>
            </div>
          </div>

          <div class="chart-wrap" ref="chartWrapRef">
            <template v-if="chartPoints.length >= 2">
              <svg
                :viewBox="`0 0 ${chartSvgW} ${SVG_H}`"
                class="chart-svg"
                preserveAspectRatio="none"
                @mouseleave="tooltip.visible = false"
              >
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#5f9e75" stop-opacity="0.18" />
                    <stop offset="100%" stop-color="#5f9e75" stop-opacity="0.01" />
                  </linearGradient>
                  <filter id="lineShadow" x="-5%" y="-80%" width="110%" height="260%">
                    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#5f9e75" flood-opacity="0.18" />
                  </filter>
                </defs>

                <!-- 网格线 -->
                <line v-for="v in GRID_VALUES" :key="v"
                  :x1="PAD_L" :y1="scoreToY(v)" :x2="chartSvgW - PAD_R" :y2="scoreToY(v)"
                  :stroke="v === 5 ? '#c4d8cc' : '#e8f0ec'"
                  :stroke-width="v === 5 ? 1.5 : 1"
                  stroke-dasharray="4 3"
                />

                <!-- Y 轴标签 -->
                <text v-for="v in GRID_VALUES" :key="'l'+v"
                  :x="PAD_L - 8" :y="scoreToY(v) + 4"
                  font-size="10" fill="#b0bec5" text-anchor="end"
                >{{ v }}</text>

                <!-- 面积填充 -->
                <polygon :points="areaPoints" fill="url(#areaGrad)" />

                <!-- 折线 -->
                <polyline :points="linePoints" fill="none" stroke="#5f9e75" stroke-width="2"
                  stroke-linejoin="round" stroke-linecap="round"
                  filter="url(#lineShadow)"
                />

                <!-- 数据点 -->
                <circle
                  v-for="p in chartPoints" :key="p.date"
                  :cx="p.x" :cy="p.y" r="5"
                  fill="white" stroke="#5f9e75" stroke-width="2.5"
                  class="chart-dot"
                  @mouseenter="showTooltip(p, $event)"
                />

                <!-- X 轴标签 -->
                <text v-for="p in xLabels" :key="'xl'+p.date"
                  :x="p.x" :y="SVG_H - 4"
                  font-size="10" fill="#b0bec5" text-anchor="middle"
                >{{ p.label }}</text>
              </svg>

              <!-- 悬浮提示 -->
              <div
                v-if="tooltip.visible"
                class="chart-tooltip"
                :style="{ left: tooltip.cssX, top: tooltip.cssY }"
              >
                <span class="tt-date">{{ tooltip.date }}</span>
                <span class="tt-score" :style="{ color: SCORE_COLORS[tooltip.score - 1] }">{{ tooltip.score }} 分</span>
                <span class="tt-label">{{ MOOD_LABELS[tooltip.score - 1] }}</span>
              </div>
            </template>

            <div v-else-if="chartLoading" class="chart-empty">
              <Loader2 :size="18" :stroke-width="1.5" class="spin" />
              <span>加载中…</span>
            </div>
            <div v-else class="chart-empty">
              <BarChart2 :size="32" :stroke-width="1" style="color:#c8d8cc" />
              <p class="empty-title">近 {{ chartRange }} 天暂无记录</p>
              <p class="empty-sub">开始记录，您的情绪变化将在这里呈现</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import {
  BookHeart, CalendarDays, TrendingUp, Sparkles,
  BrainCircuit, Save, Trash2, ChevronLeft, ChevronRight,
  Loader2, BarChart2,
} from 'lucide-vue-next'
import { getDiaries, saveDiary, deleteDiary } from '@/api/diary'
import { useUserId } from '@/composables/useUserId'

// ── Constants ──────────────────────────────────────────────────────────────────
const SVG_H = 200
const PAD_L = 36, PAD_R = 20, PAD_T = 14, PAD_B = 28
const CH = SVG_H - PAD_T - PAD_B
const GRID_VALUES = [2, 4, 6, 8, 10]

// 动态宽度：ResizeObserver 测量 chart-wrap 实际宽度，使 viewBox 精确匹配渲染尺寸，避免文字变形
const chartSvgW = ref(560)

const userId = useUserId()
const today  = new Date().toISOString().slice(0, 10)

const emotionOptions = [
  { label: '开心', type: 'pos' },
  { label: '平静', type: 'pos' },
  { label: '兴奋', type: 'pos' },
  { label: '充实', type: 'pos' },
  { label: '焦虑', type: 'neg' },
  { label: '悲伤', type: 'neg' },
  { label: '烦躁', type: 'neg' },
  { label: '疲惫', type: 'neg' },
  { label: '委屈', type: 'neg' },
  { label: '空白', type: 'neu' },
]

const MOOD_LABELS = ['很难受','难受','有些低落','有点低落','一般','还不错','较好','很好','非常好','极佳']
const SCORE_COLORS = ['#ef4444','#f97316','#f59e0b','#eab308','#84cc16','#22c55e','#10b981','#14b8a6','#0ea5e9','#6366f1']

const scoreBg   = computed(() => SCORE_COLORS[form.value.mood_score - 1])
const moodLabel = computed(() => MOOD_LABELS[form.value.mood_score - 1])
const sliderStyle = computed(() => {
  const pct = ((form.value.mood_score - 1) / 9) * 100
  return { background: `linear-gradient(to right, ${scoreBg.value} 0%, ${scoreBg.value} ${pct}%, #e2e8f0 ${pct}%, #e2e8f0 100%)` }
})

// ── Editor ─────────────────────────────────────────────────────────────────────
const form = ref({ date: today, mood_score: 6, emotions: [], content: '' })
const currentEntryId = ref(null)
const saving = ref(false), saveMsg = ref(''), saveMsgType = ref('ok')

const toggleTag = (label) => {
  const idx = form.value.emotions.indexOf(label)
  if (idx === -1) form.value.emotions.push(label)
  else form.value.emotions.splice(idx, 1)
}

watch(() => form.value.date, async (d) => {
  if (!d) return
  currentEntryId.value = null
  try {
    const entries = await getDiaries(userId, d, d)
    if (entries.length) loadFormFromEntry(entries[0])
    else { form.value.mood_score = 6; form.value.emotions = []; form.value.content = '' }
  } catch { /* silent */ }
})

const loadFormFromEntry = (entry) => {
  form.value.date = entry.date
  form.value.mood_score = entry.mood_score
  form.value.emotions = [...(entry.emotions || [])]
  form.value.content = entry.content || ''
  currentEntryId.value = entry.id
}

const handleSave = async () => {
  saving.value = true; saveMsg.value = ''
  try {
    const jsonData = JSON.stringify({ date: form.value.date, mood_score: form.value.mood_score, mood_label: moodLabel.value, emotions: form.value.emotions, content: form.value.content, timestamp: new Date().toISOString() })
    const saved = await saveDiary({ user_id: userId, date: form.value.date, mood_score: form.value.mood_score, mood_label: moodLabel.value, emotions: form.value.emotions, content: form.value.content, json_data: jsonData })
    currentEntryId.value = saved.id
    saveMsg.value = '记录已保存'; saveMsgType.value = 'ok'
    await loadAllData()
  } catch { saveMsg.value = '保存失败，请检查后端连接'; saveMsgType.value = 'err' }
  finally { saving.value = false; setTimeout(() => { saveMsg.value = '' }, 3000) }
}

const handleDelete = async () => {
  if (!currentEntryId.value) return
  try {
    await deleteDiary(currentEntryId.value)
    form.value = { date: today, mood_score: 6, emotions: [], content: '' }
    currentEntryId.value = null
    await loadAllData()
  } catch { /* silent */ }
}

// ── Calendar ───────────────────────────────────────────────────────────────────
const calYear = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth())
const entriesMap = ref({})

const prevMonth = () => { if (calMonth.value === 0) { calYear.value--; calMonth.value = 11 } else calMonth.value-- }
const nextMonth = () => { if (calMonth.value === 11) { calYear.value++; calMonth.value = 0 } else calMonth.value++ }

const scoreToColor = (score) => {
  if (!score) return null
  if (score <= 2) return '#fca5a5'
  if (score <= 4) return '#fdba74'
  if (score <= 6) return '#fde68a'
  if (score <= 8) return '#86efac'
  return '#34d399'
}
const scoreLegend = [
  { label: '1–2', color: '#fca5a5' }, { label: '3–4', color: '#fdba74' },
  { label: '5–6', color: '#fde68a' }, { label: '7–8', color: '#86efac' }, { label: '9–10', color: '#34d399' },
]

const calCells = computed(() => {
  const year = calYear.value, month = calMonth.value
  const first = new Date(year, month, 1).getDay()
  const days  = new Date(year, month + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < first; i++) cells.push({ date: null })
  for (let d = 1; d <= days; d++) {
    const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const entry = entriesMap.value[dateStr]
    cells.push({ day: d, date: dateStr, color: entry ? scoreToColor(entry.mood_score) : null, isToday: dateStr === today, isSelected: dateStr === form.value.date })
  }
  return cells
})

const loadEntry = (date) => {
  const entry = entriesMap.value[date]
  if (entry) loadFormFromEntry(entry)
  else { form.value.date = date; form.value.mood_score = 6; form.value.emotions = []; form.value.content = ''; currentEntryId.value = null }
}

// ── Chart ──────────────────────────────────────────────────────────────────────
const chartRange = ref(30), chartEntries = ref([]), chartLoading = ref(false)
const chartWrapRef = ref(null)
const tooltip = ref({ visible: false, cssX: '0px', cssY: '0px', date: '', score: 0 })

const setRange = async (r) => { chartRange.value = r; await loadChartData() }
const scoreToY = (score) => PAD_T + CH - ((score - 1) / 9) * CH

const chartPoints = computed(() => {
  const data = chartEntries.value
  if (data.length < 1) return []
  const minDate = data[0].date, maxDate = data[data.length - 1].date
  const spanMs = Math.max(new Date(maxDate) - new Date(minDate), 1)
  const W = chartSvgW.value - PAD_L - PAD_R
  return data.map(e => ({
    date: e.date,
    score: e.mood_score,
    x: PAD_L + ((new Date(e.date) - new Date(minDate)) / spanMs) * W,
    y: scoreToY(e.mood_score),
  }))
})

const linePoints = computed(() => chartPoints.value.map(p => `${p.x},${p.y}`).join(' '))

const areaPoints = computed(() => {
  const pts = chartPoints.value
  if (!pts.length) return ''
  const base = SVG_H - PAD_B
  return [`${pts[0].x},${base}`, ...pts.map(p => `${p.x},${p.y}`), `${pts[pts.length-1].x},${base}`].join(' ')
})

const xLabels = computed(() => {
  const pts = chartPoints.value
  if (pts.length < 2) return []
  const step = Math.max(1, Math.floor(pts.length / 6))
  return pts.filter((_, i) => i === 0 || i === pts.length - 1 || i % step === 0)
    .map(p => ({ date: p.date, x: p.x, label: p.date.slice(5) }))
})

const showTooltip = (p, event) => {
  const svg = event.target.closest('svg')
  const wrap = chartWrapRef.value
  if (!svg || !wrap) return
  const svgRect = svg.getBoundingClientRect()
  const wrapRect = wrap.getBoundingClientRect()
  // viewBox 与实际宽度匹配，scaleX ≈ 1；保留精确计算以防 padding 偏差
  const scaleX = svgRect.width / chartSvgW.value
  const scaleY = svgRect.height / SVG_H
  const dotX = p.x * scaleX + (svgRect.left - wrapRect.left)
  const dotY = p.y * scaleY + (svgRect.top - wrapRect.top)
  tooltip.value = {
    visible: true,
    cssX: `${dotX}px`,
    cssY: `${dotY - 64}px`,
    date: p.date.slice(5),
    score: p.score,
  }
}

let resizeObserver = null

// ── Data ───────────────────────────────────────────────────────────────────────
const loadAllData = async () => {
  const y = calYear.value, m = calMonth.value
  const start = `${y}-${String(m+1).padStart(2,'0')}-01`
  const end   = `${y}-${String(m+1).padStart(2,'0')}-${new Date(y, m+1, 0).getDate()}`
  try {
    const entries = await getDiaries(userId, start, end)
    const map = {}; entries.forEach(e => { map[e.date] = e }); entriesMap.value = map
  } catch { /* silent */ }
  await loadChartData()
}

const loadChartData = async () => {
  chartLoading.value = true
  try {
    const endDate = today
    const startDate = new Date(new Date(today).getTime() - chartRange.value * 86400000).toISOString().slice(0, 10)
    chartEntries.value = await getDiaries(userId, startDate, endDate)
  } catch { /* silent */ }
  finally { chartLoading.value = false }
}

watch([calYear, calMonth], loadAllData)
onMounted(async () => {
  await loadAllData()
  const entries = await getDiaries(userId, today, today).catch(() => [])
  if (entries.length) loadFormFromEntry(entries[0])

  // 测量 chart-wrap 宽度，使 viewBox 精确匹配，消除文字拉伸
  if (chartWrapRef.value) {
    const measure = () => {
      const w = chartWrapRef.value?.clientWidth
      if (w) chartSvgW.value = Math.max(200, w - 28)
    }
    measure()
    resizeObserver = new ResizeObserver(measure)
    resizeObserver.observe(chartWrapRef.value)
  }
})
onUnmounted(() => { resizeObserver?.disconnect() })
</script>

<style scoped>
/* ── 基础 ── */
.diary-page {
  background: #f6f2ec;
  height: 100%;
  overflow: hidden;
  padding: 16px 0 0;
  font-family: var(--f-sans, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif);
  box-sizing: border-box;
}
.diary-inner {
  max-width: 1280px;
  height: 100%;
  margin: 0 auto;
  padding: 0 32px 16px;
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 16px;
  box-sizing: border-box;
}
.left-col, .right-col { overflow: hidden; display: flex; flex-direction: column; }

/* ── Cards ── */
.card {
  background: #ffffff;
  border: 1px solid #e8e0d4;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(30, 40, 25, 0.08), 0 1px 3px rgba(30, 40, 25, 0.05);
  overflow: hidden;
  flex-shrink: 0;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 11px 16px;
  font-size: 12.5px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #3d6e52;
  background: #fdfaf5;
  border-bottom: 1px solid #ede8e0;
}

/* ── 编辑器 ── */
.editor-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.fields-scroll {
  flex: 1;
  overflow-y: auto;
  overscroll-behavior: contain;
  display: flex;
  flex-direction: column;
}
.fields-scroll::-webkit-scrollbar { width: 4px; }
.fields-scroll::-webkit-scrollbar-thumb { background: #cfe8da; border-radius: 2px; }

.field-row { padding: 12px 16px 0; }
.field-row--grow {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-bottom: 12px;
}
.field-divider {
  margin: 10px 16px 0;
  border-top: 1px solid #ede8e0;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #6b7f6e;
  margin-bottom: 7px;
  text-transform: uppercase;
}

.date-input {
  width: 100%;
  padding: 7px 10px;
  border: 1px solid #ddd6cc;
  border-radius: 4px;
  font-size: 13px;
  color: #1c2b22;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  background: #fdfaf5;
}
.date-input:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.12); }

/* 滑轨 */
.score-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px; height: 22px;
  border-radius: 50%;
  color: white;
  font-size: 12px;
  font-weight: 700;
  transition: background 0.2s;
  flex-shrink: 0;
}
.score-label-text {
  font-size: 11.5px;
  color: #64748b;
  font-weight: 400;
  letter-spacing: 0;
  text-transform: none;
}
.slider-wrap { display: flex; align-items: center; gap: 10px; padding: 2px 0; }
.slider-end {
  font-size: 11px;
  color: #94a3b8;
  letter-spacing: 0;
  text-transform: none;
  font-weight: 500;
  flex-shrink: 0;
  width: 26px;
}
.slider-end:last-child { text-align: right; }
.mood-slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 5px;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  transition: background 0.2s;
}
.mood-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px; height: 20px;
  border-radius: 50%;
  background: white;
  border: 2.5px solid #5f9e75;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.mood-slider::-moz-range-thumb {
  width: 20px; height: 20px;
  border-radius: 50%;
  background: white;
  border: 2.5px solid #5f9e75;
  cursor: pointer;
}
.mood-slider:hover::-webkit-slider-thumb { box-shadow: 0 2px 8px rgba(95,158,117,0.4); }
.slider-ticks { display: flex; justify-content: space-between; padding: 2px 0 0; }
.tick { font-size: 9.5px; color: #d1dbe4; width: 10%; text-align: center; transition: color 0.15s; }
.tick.active { color: #5f9e75; font-weight: 600; }

/* 情绪标签 */
.tag-grid { display: flex; flex-wrap: wrap; gap: 5px; }
.tag-btn {
  padding: 4px 11px;
  border: 1px solid #ddd6cc;
  background: #fdfaf5;
  font-size: 12px;
  color: #6b7f6e;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.12s;
  font-family: inherit;
  letter-spacing: 0.01em;
}
.tag-btn:hover { border-color: #4a8763; color: #3d6e52; background: #f5fbf7; }

/* 积极：绿色 */
.tag-btn.tag-pos.selected { background: #edf7f2; border-color: #5f9e75; color: #2e6649; font-weight: 600; }
/* 消极：玫红 */
.tag-btn.tag-neg.selected { background: #fdf2f4; border-color: #e88ca0; color: #b84563; font-weight: 600; }
/* 中性：灰蓝 */
.tag-btn.tag-neu.selected { background: #f1f4f8; border-color: #8ba3b8; color: #4b6478; font-weight: 600; }

/* 文本域 */
.diary-textarea {
  width: 100%;
  flex: 1;
  resize: none;
  padding: 9px 11px;
  border: 1px solid #ddd6cc;
  border-radius: 4px;
  font-size: 13.5px;
  line-height: 1.75;
  color: #1c2b22;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  min-height: 80px;
  background: #fdfaf5;
}
.diary-textarea::placeholder { color: #b8ad9e; }
.diary-textarea:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.1); }

/* 操作栏 */
.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 11px 16px 13px;
  border-top: 1px solid #ede8e0;
  flex-shrink: 0;
  background: #fdfaf5;
}
.btn-save, .btn-delete {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 18px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  transition: all 0.15s;
  font-family: inherit;
  letter-spacing: 0.02em;
}
.btn-save { background: #3d6e52; color: white; letter-spacing: 0.04em; }
.btn-save:hover { background: #2d5a42; }
.btn-save:disabled { background: #7eab93; cursor: default; }
.btn-delete { background: none; border: 1px solid #e8c4c4; color: #b84545; }
.btn-delete:hover { background: #fdf2f2; }
.save-msg { padding: 0 16px 8px; font-size: 12px; text-align: right; margin: 0; }
.save-msg.ok { color: #16a34a; }
.save-msg.err { color: #dc2626; }

/* ── 右列 ── */
.right-col { gap: 14px; }
.right-top { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

/* ── 日历 ── */
.calendar-card .card-title { justify-content: flex-start; }
.cal-nav { margin-left: auto; display: flex; align-items: center; gap: 6px; }
.cal-month { font-size: 12px; font-weight: 600; color: #374151; letter-spacing: 0.02em; }
.cal-arrow {
  display: flex;
  background: none;
  border: 1px solid #ddd6cc;
  border-radius: 3px;
  padding: 1px 3px;
  cursor: pointer;
  color: #4a8763;
}
.cal-arrow:hover { background: #f5ead8; border-color: #c9a96e; }

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding: 8px 10px 4px;
  gap: 2px;
}
.cal-dow {
  text-align: center;
  font-size: 10.5px;
  color: #94a3b8;
  padding: 2px 0 4px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.cal-cell-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px 0;
}
.cal-empty-cell { width: 28px; height: 28px; }
.cal-circle {
  width: 28px; height: 28px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 11.5px;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.12s;
  flex-shrink: 0;
  font-weight: 500;
  font-family: inherit;
}
.cal-circle:hover { background: #edf7f2 !important; }
.cal-circle.has-entry { color: rgba(0,0,0,0.55); font-weight: 700; }
.cal-circle.is-today { box-shadow: 0 0 0 2px #4a8763; }
.cal-circle.is-selected { box-shadow: 0 0 0 2px #3d6e52, 0 0 0 4px rgba(46,92,65,0.15); }

.cal-legend {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 4px 10px 10px;
}
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 10.5px; color: #64748b; }
.legend-dot { width: 7px; height: 7px; border-radius: 50%; }

/* ── AI 卡片 ── */
.coming-soon {
  margin-left: auto;
  font-size: 10.5px;
  font-weight: 500;
  background: #f5ead8;
  color: #8a6030;
  padding: 2px 8px;
  border-radius: 3px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.ai-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 16px 22px;
  gap: 8px;
  text-align: center;
}
.ai-avatar {
  width: 52px; height: 52px;
  border-radius: 50%;
  background: #f0f9f4;
  border: 1px dashed #7bb896;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5f9e75;
  margin-bottom: 2px;
}
.ai-tip { font-size: 12.5px; color: #475569; margin: 0; line-height: 1.6; }
.ai-sub { font-size: 11.5px; color: #94a3b8; margin: 0; }

/* ── 情绪曲线 ── */
.chart-card { flex: 1; display: flex; flex-direction: column; }
.range-tabs { margin-left: auto; display: flex; gap: 4px; }
.range-tab {
  padding: 2px 10px;
  font-size: 11.5px;
  border: 1px solid #ddd6cc;
  background: none;
  color: #7a9080;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.12s;
  font-family: inherit;
}
.range-tab:hover { border-color: #4a8763; color: #3d6e52; background: #f5fbf7; }
.range-tab.active { background: #3d6e52; color: white; border-color: #3d6e52; }

.chart-wrap {
  flex: 1;
  padding: 12px 14px 10px;
  display: flex;
  align-items: center;
  position: relative;
}
.chart-svg { width: 100%; height: 200px; display: block; overflow: visible; }
.chart-dot { cursor: pointer; transition: r 0.12s; }
.chart-dot:hover { r: 7; }

/* 悬浮提示 */
.chart-tooltip {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  background: white;
  border: 1px solid #e8e0d4;
  border-radius: 5px;
  padding: 6px 12px;
  box-shadow: 0 6px 18px rgba(30,40,25,0.12);
  pointer-events: none;
  transform: translateX(-50%);
  white-space: nowrap;
  z-index: 10;
}
.tt-date { font-size: 10.5px; color: #94a3b8; }
.tt-score { font-size: 16px; font-weight: 700; line-height: 1.2; }
.tt-label { font-size: 11px; color: #64748b; }

/* 空状态 */
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 160px;
  gap: 6px;
  color: #94a3b8;
}
.empty-title { font-size: 13px; color: #7a9caa; margin: 0; font-weight: 500; }
.empty-sub { font-size: 11.5px; color: #b0c4cc; margin: 0; }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
