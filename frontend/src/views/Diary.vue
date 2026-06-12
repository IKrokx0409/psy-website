<template>
  <div class="diary-page">
    <div class="diary-inner">

      <!-- ── 左侧：日历 ── -->
      <div class="left-sidebar">
        <div class="card calendar-card">
          <div class="cal-header">
            <CalendarDays :size="13" :stroke-width="1.5" class="cal-icon" />
            <span class="cal-title-text">情绪日历</span>
            <div class="cal-nav">
              <button class="cal-arrow" @click="prevMonth"><ChevronLeft :size="12" /></button>
              <span class="cal-month">{{ calYear }}.{{ String(calMonth + 1).padStart(2,'0') }}</span>
              <button class="cal-arrow" @click="nextMonth"><ChevronRight :size="12" /></button>
            </div>
          </div>

          <div class="cal-grid">
            <div class="cal-dow" v-for="d in ['日','一','二','三','四','五','六']" :key="d">{{ d }}</div>
            <div v-for="(cell, i) in calCells" :key="i" class="cal-cell-wrap">
              <button
                v-if="cell.date"
                :class="['cal-circle', { 'has-entry': !!cell.color, 'is-today': cell.isToday, 'is-selected': cell.isSelected }]"
                :style="cell.color ? { '--bloom': cell.color } : {}"
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

          <div class="cal-footer">
            <div class="cal-stat" v-if="Object.keys(entriesMap).length">
              <span class="stat-num">{{ Object.keys(entriesMap).length }}</span>
              <span class="stat-label">本月记录</span>
            </div>
            <div class="cal-stat" v-if="avgScore">
              <span class="stat-num" :style="{ color: SCORE_COLORS[Math.round(avgScore) - 1] }">{{ avgScore }}</span>
              <span class="stat-label">平均心情</span>
            </div>
          </div>
        </div>

        <button
          :class="['chart-toggle-btn', { active: showChart }]"
          @click="showChart = !showChart"
        >
          <TrendingUp :size="13" :stroke-width="1.5" />
          {{ showChart ? '隐藏情绪曲线' : '查看情绪曲线' }}
        </button>
      </div>

      <!-- ── 中列：编辑器 ── -->
      <div class="center-col">
        <div class="card editor-card">

          <div class="editor-header">
            <div class="date-display">
              <span class="date-day-num">{{ parseInt((form.date || today).slice(8)) }}</span>
              <div class="date-meta">
                <span class="date-month-year">{{ (form.date || today).slice(0,4) + ' 年 ' + parseInt((form.date || today).slice(5,7)) + ' 月' }}</span>
                <span class="date-weekday">{{ ['周日','周一','周二','周三','周四','周五','周六'][new Date((form.date || today) + 'T12:00:00').getDay()] }}</span>
              </div>
            </div>
            <div class="header-actions">
              <BookHeart :size="14" :stroke-width="1.5" class="header-icon" />
              <input type="date" v-model="form.date" class="date-inline" :max="today" />
            </div>
          </div>

          <div class="fields-scroll">

            <!-- 情绪评分 -->
            <div class="field-row">
              <div class="mood-display-row">
                <div class="mood-score-block" :style="{ '--mood-color': scoreBg }">
                  <span class="mood-numeral">{{ form.mood_score }}</span>
                  <span class="mood-label-text">{{ moodLabel }}</span>
                </div>
                <div class="slider-section">
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
              <label class="field-label">
                今日记录
                <span class="char-count" v-if="form.content">{{ form.content.length }} 字</span>
              </label>
              <textarea
                v-model="form.content"
                class="diary-textarea"
                placeholder="写下今天发生了什么，你的感受……"
              ></textarea>
            </div>

          </div>

          <div class="editor-actions">
            <button class="btn-delete" v-if="currentEntryId" @click="handleDelete">
              <Trash2 :size="11" :stroke-width="1.5" /> 删除
            </button>
            <div class="actions-right">
              <p v-if="saveMsg" class="save-msg" :class="saveMsgType">{{ saveMsg }}</p>
              <button class="btn-save" @click="handleSave" :disabled="saving">
                <Save :size="11" :stroke-width="1.5" />
                {{ saving ? '保存中…' : (currentEntryId ? '更新' : '保存') }}
              </button>
            </div>
          </div>

        </div>
      </div>

      <!-- ── 右列：AI 卡片 ── -->
      <div class="right-col">

        <!-- AI 今日回声 -->
        <div class="card ai-echo-card">
          <div class="card-title">
            <Sparkles :size="13" :stroke-width="1.5" />
            AI 今日回声
          </div>
          <div class="ai-body">

            <template v-if="aiLoading">
              <div class="thinking-avatar">
                <BrainCircuit :size="20" :stroke-width="1" />
              </div>
              <div class="thinking-text">
                <p class="thinking-title">AI 正在感受你的情绪</p>
                <p class="thinking-sub">{{ thinkingHint }}</p>
              </div>
              <div class="thinking-dots"><span></span><span></span><span></span></div>
            </template>

            <template v-else-if="aiEmotional">
              <div class="ai-sections">
                <div class="ai-section">
                  <div class="ai-response-text markdown-body" v-html="renderMd(aiEmotional)"></div>
                </div>
              </div>
              <button class="ai-re-btn" @click="analyzeEmotion">
                <RefreshCw :size="10" :stroke-width="1.5" /> 重新回应
              </button>
              <p v-if="aiError" class="ai-error">{{ aiError }}</p>
            </template>

            <template v-else>
              <div class="ai-avatar">
                <BrainCircuit :size="22" :stroke-width="1" />
              </div>
              <p class="ai-tip">
                {{ form.content.trim() ? '今天的心情已记录，让 AI 来倾听。' : '保存今日记录后，AI 将为你回声。' }}
              </p>
              <button class="ai-fetch-btn" @click="analyzeEmotion">
                <Sparkles :size="11" :stroke-width="1.5" /> 获取情绪回应
              </button>
              <p v-if="aiError" class="ai-error">{{ aiError }}</p>
            </template>

          </div>
        </div>

        <!-- AI 七日总结 -->
        <div class="card ai-weekly-card">
          <div class="card-title">
            <BarChart2 :size="13" :stroke-width="1.5" />
            七日情绪总结
          </div>
          <div class="weekly-body">
            <template v-if="aiLoading">
              <div class="weekly-loading">
                <Loader2 :size="13" :stroke-width="1.5" class="spin" />
                <span>{{ thinkingHint }}</span>
              </div>
            </template>
            <template v-else-if="aiWeekly">
              <div class="ai-response-text markdown-body" v-html="renderMd(aiWeekly)"></div>
            </template>
            <template v-else>
              <div class="weekly-empty">
                <BarChart2 :size="26" :stroke-width="1" class="icon-muted" />
                <p>完成今日记录后<br/>AI 将总结近7天情绪变化</p>
              </div>
            </template>
          </div>
        </div>

      </div>

      <!-- ── 底部：情绪曲线 ── -->
      <div v-if="showChart" class="chart-strip">
        <div class="card chart-card">
          <div class="card-title">
            <TrendingUp :size="13" :stroke-width="1.5" />
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

                <line v-for="v in GRID_VALUES" :key="v"
                  :x1="PAD_L" :y1="scoreToY(v)" :x2="chartSvgW - PAD_R" :y2="scoreToY(v)"
                  :stroke="v === 5 ? '#c4d8cc' : '#e8f0ec'"
                  :stroke-width="v === 5 ? 1.5 : 1"
                  stroke-dasharray="4 3"
                />
                <text v-for="v in GRID_VALUES" :key="'l'+v"
                  :x="PAD_L - 8" :y="scoreToY(v) + 4"
                  font-size="10" fill="#b0bec5" text-anchor="end"
                >{{ v }}</text>

                <polygon :points="areaPoints" fill="url(#areaGrad)" />
                <polyline :points="linePoints" fill="none" stroke="#5f9e75" stroke-width="2"
                  stroke-linejoin="round" stroke-linecap="round"
                  filter="url(#lineShadow)"
                />
                <circle
                  v-for="p in chartPoints" :key="p.date"
                  :cx="p.x" :cy="p.y" r="4"
                  fill="white" stroke="#5f9e75" stroke-width="2"
                  class="chart-dot"
                  @mouseenter="showTooltip(p, $event)"
                />
                <text v-for="p in xLabels" :key="'xl'+p.date"
                  :x="p.x" :y="SVG_H - 3"
                  font-size="10" fill="#b0bec5" text-anchor="middle"
                >{{ p.label }}</text>
              </svg>

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
              <Loader2 :size="13" :stroke-width="1.5" class="spin" />
              <span>加载中…</span>
            </div>
            <div v-else class="chart-empty">
              <TrendingUp :size="20" :stroke-width="1" class="icon-muted" />
              <p class="empty-title">近 {{ chartRange }} 天暂无记录</p>
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
  Loader2, BarChart2, RefreshCw,
} from 'lucide-vue-next'
import { getDiaries, saveDiary, deleteDiary, getAIDiaryResponse } from '@/api/diary'
import { useUserId } from '@/composables/useUserId'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
const renderMd = (text) => text ? md.render(text) : ''

// ── Constants ──────────────────────────────────────────────────────────────────
const SVG_H = 88
const PAD_L = 36, PAD_R = 20, PAD_T = 10, PAD_B = 22
const CH = SVG_H - PAD_T - PAD_B
const GRID_VALUES = [2, 4, 6, 8, 10]

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

const avgScore = computed(() => {
  const vals = Object.values(entriesMap.value).map(e => e.mood_score).filter(Boolean)
  if (!vals.length) return null
  return (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1)
})

// ── AI Response ────────────────────────────────────────────────────────────────
const aiEmotional = ref('')
const aiWeekly    = ref('')
const aiLoading   = ref(false)
const aiError     = ref('')

const THINKING_HINTS = [
  '正在阅读你的日记…',
  '梳理近7天的情绪脉络…',
  '思考最合适的回应…',
  '快好了，稍等一下…',
]
const thinkingHint = ref(THINKING_HINTS[0])
let thinkingTimer = null

const startThinkingHints = () => {
  let i = 0
  thinkingTimer = setInterval(() => {
    i = (i + 1) % THINKING_HINTS.length
    thinkingHint.value = THINKING_HINTS[i]
  }, 4000)
}
const stopThinkingHints = () => {
  if (thinkingTimer) { clearInterval(thinkingTimer); thinkingTimer = null }
  thinkingHint.value = THINKING_HINTS[0]
}

const getLast7DiaryList = async () => {
  const end   = form.value.date || today
  const start = new Date(new Date(end).getTime() - 6 * 86400000).toISOString().slice(0, 10)
  try { return await getDiaries(userId, start, end) } catch { return [] }
}

const analyzeEmotion = async () => {
  if (aiLoading.value) return
  aiLoading.value = true
  aiError.value   = ''
  startThinkingHints()
  try {
    const weekList = await getLast7DiaryList()
    const result = await getAIDiaryResponse({
      user_id:          userId,
      today_diary:      form.value.content,
      today_mood_score: form.value.mood_score,
      today_mood_label: moodLabel.value,
      today_emotions:   form.value.emotions,
      date:             form.value.date || today,
      week_diaries:     weekList,
    })
    aiEmotional.value = result.emotional_response || ''
    aiWeekly.value    = result.weekly_summary || ''
  } catch {
    aiError.value = '获取失败，请检查后端连接'
  } finally {
    aiLoading.value = false
    stopThinkingHints()
  }
}

// ── Editor ─────────────────────────────────────────────────────────────────────
const form = ref({ date: today, mood_score: 6, emotions: [], content: '' })
const currentEntryId = ref(null)
const saving = ref(false), saveMsg = ref(''), saveMsgType = ref('ok')
const showChart = ref(false)

const toggleTag = (label) => {
  const idx = form.value.emotions.indexOf(label)
  if (idx === -1) form.value.emotions.push(label)
  else form.value.emotions.splice(idx, 1)
}

watch(() => form.value.date, async (d) => {
  if (!d) return
  aiEmotional.value = ''
  aiWeekly.value    = ''
  aiError.value     = ''
  currentEntryId.value = null
  try {
    const entries = await getDiaries(userId, d, d)
    if (entries.length) loadFormFromEntry(entries[0])
    else { form.value.mood_score = 6; form.value.emotions = []; form.value.content = '' }
  } catch { /* silent */ }
})

const loadFormFromEntry = (entry) => {
  form.value.date       = entry.date
  form.value.mood_score = entry.mood_score
  form.value.emotions   = [...(entry.emotions || [])]
  form.value.content    = entry.content || ''
  currentEntryId.value  = entry.id

  if (entry.ai_feedback) {
    try {
      const cached = JSON.parse(entry.ai_feedback)
      aiEmotional.value = cached.emotional_response || ''
      aiWeekly.value    = cached.weekly_summary || ''
    } catch {
      aiEmotional.value = entry.ai_feedback
      aiWeekly.value    = ''
    }
    aiError.value = ''
  } else if (entry.content && entry.date === today) {
    analyzeEmotion()
  }
}

const handleSave = async () => {
  saving.value = true; saveMsg.value = ''
  try {
    const jsonData = JSON.stringify({ date: form.value.date, mood_score: form.value.mood_score, mood_label: moodLabel.value, emotions: form.value.emotions, content: form.value.content, timestamp: new Date().toISOString() })
    const saved = await saveDiary({ user_id: userId, date: form.value.date, mood_score: form.value.mood_score, mood_label: moodLabel.value, emotions: form.value.emotions, content: form.value.content, json_data: jsonData })
    currentEntryId.value = saved.id
    saveMsg.value = '记录已保存'; saveMsgType.value = 'ok'
    await loadAllData()
    aiEmotional.value = ''
    aiWeekly.value    = ''
    analyzeEmotion()
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
const calYear  = ref(new Date().getFullYear())
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
  const svgRect  = svg.getBoundingClientRect()
  const wrapRect = wrap.getBoundingClientRect()
  const scaleX = svgRect.width / chartSvgW.value
  const scaleY = svgRect.height / SVG_H
  const dotX = p.x * scaleX + (svgRect.left - wrapRect.left)
  const dotY = p.y * scaleY + (svgRect.top - wrapRect.top)
  tooltip.value = {
    visible: true,
    cssX: `${dotX}px`,
    cssY: `${dotY - 58}px`,
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
    const endDate   = today
    const startDate = new Date(new Date(today).getTime() - chartRange.value * 86400000).toISOString().slice(0, 10)
    chartEntries.value = await getDiaries(userId, startDate, endDate)
  } catch { /* silent */ }
  finally { chartLoading.value = false }
}

watch([calYear, calMonth], loadAllData)
onMounted(async () => {
  await loadAllData()
  const todayEntry = entriesMap.value[today]
  if (todayEntry) loadFormFromEntry(todayEntry)

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
onUnmounted(() => { resizeObserver?.disconnect(); resizeObserver = null; stopThinkingHints() })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap');

.diary-page {
  background: var(--c-beige);
  height: 100%;
  overflow: hidden;
  padding: 16px 0 0;
  font-family: var(--f-sans);
  box-sizing: border-box;
  color: var(--c-text-dark);
}

/* Grid */
.diary-inner {
  max-width: 1280px;
  height: 100%;
  margin: 0 auto;
  padding: 0 28px 16px;
  display: grid;
  grid-template-columns: 224px 1fr 284px;
  grid-template-rows: 1fr auto;
  gap: 12px;
  box-sizing: border-box;
}

.left-sidebar { grid-column: 1; grid-row: 1; overflow: hidden; display: flex; flex-direction: column; }
.center-col   { grid-column: 2; grid-row: 1; overflow: hidden; display: flex; flex-direction: column; }
.right-col    { grid-column: 3; grid-row: 1 / 3; overflow: hidden; display: flex; flex-direction: column; gap: 12px; }
.chart-strip  { grid-column: 1 / 3; grid-row: 2; }

/* ── Cards ── */
.card {
  background: #ffffff;
  border: 1px solid var(--c-beige-border);
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 9px 14px;
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: #3d6e52;
  background: #fdfaf5;
  border-bottom: 1px solid #ede8e0;
  flex-shrink: 0;
}

/* ── Calendar ── */
.calendar-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.cal-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px 9px;
  border-bottom: 1px solid #ede8e0;
  background: #fdfaf5;
  flex-shrink: 0;
}

.cal-icon { color: #7a9080; flex-shrink: 0; }

.cal-title-text {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: #3d6e52;
}

.cal-nav { margin-left: auto; display: flex; align-items: center; gap: 5px; }

.cal-month {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  color: #374151;
  letter-spacing: 0.06em;
  min-width: 52px;
  text-align: center;
}

.cal-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1px solid #ddd6cc;
  border-radius: 5px;
  padding: 2px 4px;
  cursor: pointer;
  color: #4a8763;
  transition: all 0.15s;
  line-height: 1;
}
.cal-arrow:hover { background: #f5ead8; border-color: #c9a96e; color: #4a8763; }

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  padding: 8px 6px 4px;
  gap: 2px;
}

.cal-dow {
  text-align: center;
  font-size: 9.5px;
  color: #94a3b8;
  padding: 2px 0 5px;
  font-weight: 600;
  letter-spacing: 0.06em;
}

.cal-cell-wrap { display: flex; align-items: center; justify-content: center; }
.cal-empty-cell { width: 26px; height: 26px; }

.cal-circle {
  width: 26px; height: 26px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 10.5px;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.12s;
  flex-shrink: 0;
  font-weight: 400;
  font-family: 'DM Mono', monospace;
}

.cal-circle:hover { background: #edf7f2; color: #1c2b22; }

.cal-circle.has-entry {
  background: radial-gradient(circle, var(--bloom) 0%, var(--bloom) 68%, transparent 100%);
  color: rgba(0,0,0,0.6);
  font-weight: 700;
}

.cal-circle.is-today {
  box-shadow: 0 0 0 1.5px #4a8763;
  color: #4a8763;
}
.cal-circle.is-today.has-entry { color: rgba(0,0,0,0.6); }

.cal-circle.is-selected {
  box-shadow: 0 0 0 2px #3d6e52, 0 0 0 4px rgba(46,92,65,0.15);
}
.cal-circle.is-selected:not(.has-entry) { color: #3d6e52; }

.cal-legend {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 4px 7px;
  padding: 6px 8px 8px;
  border-top: 1px solid #ede8e0;
}

.legend-item { display: flex; align-items: center; gap: 4px; font-size: 9.5px; color: #64748b; }
.legend-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

.cal-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-around;
  padding: 8px 12px 12px;
  border-top: 1px solid #ede8e0;
  background: #fdfaf5;
}

.cal-stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }

.stat-num {
  font-family: 'Cormorant Garamond', serif;
  font-size: 26px;
  font-weight: 600;
  color: #3d6e52;
  line-height: 1;
}

.stat-label { font-size: 9.5px; color: #94a3b8; letter-spacing: 0.06em; }

/* ── Editor ── */
.editor-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 18px 10px;
  border-bottom: 1px solid #ede8e0;
  background: #fdfaf5;
  flex-shrink: 0;
  gap: 12px;
}

.date-display {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.date-day-num {
  font-family: 'Cormorant Garamond', serif;
  font-size: 48px;
  font-weight: 600;
  line-height: 1;
  color: #3d6e52;
  letter-spacing: -0.02em;
}

.date-meta { display: flex; flex-direction: column; gap: 1px; }
.date-month-year { font-size: 12px; color: #6b7f6e; font-weight: 500; }
.date-weekday { font-size: 11px; color: #94a3b8; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-left: auto;
}

.header-icon { color: #94a3b8; flex-shrink: 0; }

.date-inline {
  padding: 4px 10px;
  border: 1px solid #ddd6cc;
  border-radius: 6px;
  font-size: 11.5px;
  color: #3d4f4a;
  outline: none;
  font-family: 'DM Mono', monospace;
  background: #f5f0e8;
  cursor: pointer;
  letter-spacing: 0.04em;
}
.date-inline:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.12); }

.fields-scroll {
  flex: 1;
  overflow-y: auto;
  overscroll-behavior: contain;
  display: flex;
  flex-direction: column;
}
.fields-scroll::-webkit-scrollbar { width: 3px; }
.fields-scroll::-webkit-scrollbar-thumb { background: #cfe8da; border-radius: 2px; }

.field-row { padding: 12px 18px 0; }
.field-row--grow { flex: 1; display: flex; flex-direction: column; padding-bottom: 12px; }
.field-divider { margin: 10px 18px 0; border-top: 1px solid #ede8e0; }

.field-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: #6b7f6e;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.char-count {
  margin-left: auto;
  font-size: 10px;
  color: #94a3b8;
  letter-spacing: 0;
  text-transform: none;
  font-weight: 400;
  font-family: 'DM Mono', monospace;
}

/* Mood row */
.mood-display-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mood-score-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  min-width: 58px;
  color: var(--mood-color, #4a8763);
  transition: color 0.3s;
}

.mood-numeral {
  font-family: 'Cormorant Garamond', serif;
  font-size: 52px;
  font-weight: 600;
  line-height: 1;
  color: inherit;
}

.mood-label-text {
  font-family: var(--f-sans);
  font-size: 9.5px;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin-top: 3px;
  text-transform: none;
}

.slider-section { flex: 1; min-width: 0; }

.slider-wrap { display: flex; align-items: center; gap: 10px; }
.slider-end { font-size: 10.5px; color: #94a3b8; flex-shrink: 0; width: 24px; }
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
.tick {
  font-size: 9.5px;
  color: #d1dbe4;
  width: 10%;
  text-align: center;
  transition: color 0.15s;
  font-family: 'DM Mono', monospace;
}
.tick.active { color: #5f9e75; font-weight: 600; }

/* Tags */
.tag-grid { display: flex; flex-wrap: wrap; gap: 6px; }

.tag-btn {
  padding: 4px 11px;
  border: 1px solid #ddd6cc;
  background: #fdfaf5;
  font-size: 12px;
  color: #6b7f6e;
  cursor: pointer;
  border-radius: 9999px;
  transition: all var(--t-fast);
  font-family: inherit;
}
.tag-btn:hover { border-color: #4a8763; color: #3d6e52; background: #f5fbf7; }

.tag-btn.tag-pos.selected {
  background: #edf7f2;
  border-color: #5f9e75;
  color: #2e6649;
  font-weight: 600;
}
.tag-btn.tag-neg.selected {
  background: #fdf2f4;
  border-color: #e88ca0;
  color: #b84563;
  font-weight: 600;
}
.tag-btn.tag-neu.selected {
  background: #f1f4f8;
  border-color: #8ba3b8;
  color: #4b6478;
  font-weight: 600;
}

/* Textarea */
.diary-textarea {
  width: 100%;
  flex: 1;
  resize: none;
  padding: 9px 11px;
  border: 1px solid #ddd6cc;
  border-radius: var(--r-sm);
  font-size: 13.5px;
  line-height: 1.75;
  color: #1c2b22;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  min-height: 80px;
  background: #fdfaf5;
  transition: border-color 0.15s, box-shadow 0.15s;
  caret-color: #4a8763;
}
.diary-textarea::placeholder { color: #b8ad9e; }
.diary-textarea:focus {
  border-color: #4a8763;
  box-shadow: 0 0 0 2px rgba(74,135,99,0.1);
}

/* Actions bar */
.editor-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 10px 18px 12px;
  border-top: 1px solid #ede8e0;
  flex-shrink: 0;
  background: #fdfaf5;
}

.actions-right { display: flex; align-items: center; gap: 10px; }

.btn-save, .btn-delete {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 18px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  border-radius: var(--r-sm);
  transition: all var(--t-base);
  font-family: inherit;
  letter-spacing: 0.04em;
}

.btn-save { background: #3d6e52; color: white; }
.btn-save:hover { background: #2d5a42; }
.btn-save:disabled { background: #7eab93; cursor: default; }

.btn-delete { background: none; border: 1px solid #e8c4c4; color: #b84545; }
.btn-delete:hover { background: #fdf2f2; }

.save-msg { font-size: 12px; margin: 0; }
.save-msg.ok { color: #16a34a; }
.save-msg.err { color: #dc2626; }

/* ── AI Cards ── */
.ai-echo-card, .ai-weekly-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 14px 16px;
  gap: 10px;
  text-align: center;
  overflow-y: auto;
}
.ai-body::-webkit-scrollbar { width: 3px; }
.ai-body::-webkit-scrollbar-thumb { background: #cfe8da; border-radius: 2px; }

.ai-avatar {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: #f0f9f4;
  border: 1px dashed #7bb896;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5f9e75;
  flex-shrink: 0;
}

.ai-tip { font-size: 12px; color: #475569; margin: 0; line-height: 1.6; }

.ai-fetch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: #3d6e52;
  color: white;
  border: none;
  border-radius: var(--r-pill);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  letter-spacing: 0.04em;
  transition: background var(--t-fast);
  flex-shrink: 0;
}
.ai-fetch-btn:hover { background: #2d5a42; }

.ai-sections {
  width: 100%;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background: #fdfaf5;
  border: 1px solid #ede8e0;
  border-radius: var(--r-sm);
  box-sizing: border-box;
}
.ai-sections::-webkit-scrollbar { width: 3px; }
.ai-sections::-webkit-scrollbar-thumb { background: #cfe8da; border-radius: 2px; }

.ai-section { padding: 9px 11px; }
.ai-response-text { font-size: 12.5px; color: #3d4f4a; line-height: 1.8; margin: 0; text-align: left; }
.ai-response-text.markdown-body p { margin: 0 0 8px; }
.ai-response-text.markdown-body p:last-child { margin-bottom: 0; }
.ai-response-text.markdown-body ul,
.ai-response-text.markdown-body ol { padding-left: 18px; margin: 6px 0; }
.ai-response-text.markdown-body li { margin: 4px 0; }
.ai-response-text.markdown-body strong { font-weight: 600; color: #2d4039; }
.ai-response-text.markdown-body h1,
.ai-response-text.markdown-body h2,
.ai-response-text.markdown-body h3 { font-weight: 600; margin: 10px 0 4px; color: #2d4039; }
.ai-response-text.markdown-body h3 { font-size: 13px; }
.ai-response-text.markdown-body blockquote { border-left: 3px solid #a8d5b8; padding-left: 10px; color: #5a7a6a; margin: 6px 0; }

.ai-re-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: none;
  border: 1px solid #c8dfd3;
  color: #5f9e75;
  border-radius: var(--r-pill);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--t-fast);
  flex-shrink: 0;
}
.ai-re-btn:hover { background: #f0f9f4; border-color: #4a8763; color: #3d6e52; }
.ai-error { font-size: 11.5px; color: #dc2626; margin: 0; }

/* Thinking */
.thinking-avatar {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: #f0f9f4;
  border: 1px solid #7bb896;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5f9e75;
  animation: ai-pulse 2s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes ai-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(95,158,117,0.35); }
  50%       { box-shadow: 0 0 0 9px rgba(95,158,117,0); }
}

.thinking-text { text-align: center; }
.thinking-title { font-size: 12px; font-weight: 600; color: #3d6e52; margin: 0 0 4px; }
.thinking-sub { font-size: 11px; color: #7a9080; margin: 0; min-height: 16px; }

.thinking-dots { display: flex; gap: 5px; }
.thinking-dots span { width: 6px; height: 6px; border-radius: 50%; background: #5f9e75; animation: dot-bounce 1.4s ease-in-out infinite; }
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%           { transform: scale(1);   opacity: 1; }
}

/* Weekly */
.weekly-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
}
.weekly-body::-webkit-scrollbar { width: 3px; }
.weekly-body::-webkit-scrollbar-thumb { background: #cfe8da; border-radius: 2px; }

.weekly-loading { display: flex; align-items: center; gap: 8px; color: #7a9080; font-size: 12px; }
.weekly-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 8px;
  text-align: center;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.6;
}

/* ── Chart ── */
.chart-strip { display: flex; flex-direction: column; }
.chart-card { display: flex; flex-direction: column; }

.range-tabs { margin-left: auto; display: flex; gap: 4px; }
.range-tab {
  padding: 2px 9px;
  font-size: 11px;
  border: 1px solid #ddd6cc;
  background: none;
  color: #7a9080;
  cursor: pointer;
  border-radius: var(--r-pill);
  transition: all var(--t-fast);
  font-family: inherit;
}
.range-tab:hover { border-color: #4a8763; color: #3d6e52; background: #f5fbf7; }
.range-tab.active { background: #3d6e52; color: white; border-color: #3d6e52; }

.chart-wrap {
  padding: 8px 12px 6px;
  display: flex;
  align-items: center;
  position: relative;
}

.chart-svg { width: 100%; height: 88px; display: block; overflow: visible; }
.chart-dot { cursor: pointer; transition: r 0.12s; }
.chart-dot:hover { r: 6; }

.chart-tooltip {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-md);
  padding: 5px 10px;
  box-shadow: var(--shadow-md);
  pointer-events: none;
  transform: translateX(-50%);
  white-space: nowrap;
  z-index: 10;
}
.tt-date { font-size: 10px; color: #94a3b8; font-family: 'DM Mono', monospace; }
.tt-score { font-size: 15px; font-weight: 700; line-height: 1.2; font-family: 'Cormorant Garamond', serif; }
.tt-label { font-size: 10.5px; color: #64748b; }

.chart-empty {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88px;
  gap: 8px;
  color: #94a3b8;
}
.empty-title { font-size: 12px; color: #7a9caa; margin: 0; font-weight: 500; }

.icon-muted { color: #c8d8cc; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 查看情绪曲线 按钮 ── */
.chart-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 0;
  margin-top: 8px;
  width: 100%;
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: #4a8763;
  cursor: pointer;
  font-family: var(--f-sans);
  letter-spacing: 0.04em;
  transition: all var(--t-fast);
  flex-shrink: 0;
  box-shadow: var(--shadow-xs);
}
.chart-toggle-btn:hover { background: #f5fbf7; border-color: #5f9e75; color: #3d6e52; }
.chart-toggle-btn.active { background: #3d6e52; color: white; border-color: #3d6e52; }

/* ── 响应式 ── */
@media (max-width: 900px) {
  .diary-inner {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    height: auto;
    padding: 12px 16px 24px;
  }
  .left-sidebar { grid-column: 1; grid-row: auto; overflow: visible; }
  .center-col   { grid-column: 1; grid-row: auto; overflow: visible; }
  .right-col    { grid-column: 1; grid-row: auto; overflow: visible; }
  .chart-strip  { grid-column: 1; grid-row: auto; }
  .diary-page   { overflow: auto; }
}

@media (max-width: 480px) {
  .diary-inner { padding: 8px 12px 20px; gap: 10px; }
  .editor-header { flex-wrap: wrap; gap: 8px; }
  .date-day-num { font-size: 36px; }
  .mood-display-row { flex-direction: column; gap: 12px; }
  .mood-score-block { width: auto; min-width: 80px; }
}
</style>
