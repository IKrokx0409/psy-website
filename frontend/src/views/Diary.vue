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

          <!-- 日期 -->
          <div class="field-row">
            <label class="field-label">日期</label>
            <input type="date" v-model="form.date" class="date-input" :max="today" />
          </div>

          <!-- 情绪评分滑轮 -->
          <div class="field-row">
            <label class="field-label">
              今日心情
              <span class="score-badge" :style="{ background: scoreBg }">{{ form.mood_score }}</span>
              <span class="score-label-text">{{ moodLabel }}</span>
            </label>
            <div class="slider-wrap">
              <span class="slider-min">😔</span>
              <input
                type="range" min="1" max="10"
                v-model.number="form.mood_score"
                class="mood-slider"
                :style="sliderStyle"
              />
              <span class="slider-max">😊</span>
            </div>
            <div class="slider-ticks">
              <span v-for="n in 10" :key="n" :class="['tick', { active: n <= form.mood_score }]">{{ n }}</span>
            </div>
          </div>

          <!-- 情绪标签 -->
          <div class="field-row">
            <label class="field-label">情绪标签</label>
            <div class="tag-grid">
              <button
                v-for="tag in emotionOptions" :key="tag.label"
                :class="['tag-btn', { selected: form.emotions.includes(tag.label) }]"
                @click="toggleTag(tag.label)"
              >{{ tag.emoji }} {{ tag.label }}</button>
            </div>
          </div>

          <!-- 自由书写 -->
          <div class="field-row">
            <label class="field-label">今日记录</label>
            <textarea
              v-model="form.content"
              class="diary-textarea"
              placeholder="写下今天的心情……"
              rows="4"
            ></textarea>
          </div>

          <!-- 操作 -->
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

        <!-- 上半：日历 + AI 并排 -->
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

            <!-- 图例 -->
            <div class="cal-legend">
              <span v-for="l in scoreLegend" :key="l.label" class="legend-item">
                <span class="legend-dot" :style="{ background: l.color }"></span>{{ l.label }}
              </span>
            </div>
          </div>

          <!-- AI 反馈占位 -->
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

        <!-- 下半：情绪曲线 -->
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

          <div class="chart-wrap">
            <svg v-if="chartPoints.length >= 2" :viewBox="`0 0 ${SVG_W} ${SVG_H}`" class="chart-svg" preserveAspectRatio="none">
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#5f9e75" stop-opacity="0.3" />
                  <stop offset="100%" stop-color="#5f9e75" stop-opacity="0.02" />
                </linearGradient>
              </defs>
              <line v-for="v in [2,4,6,8,10]" :key="v"
                :x1="PAD_L" :y1="scoreToY(v)" :x2="SVG_W - PAD_R" :y2="scoreToY(v)"
                stroke="#e8f0ec" stroke-width="1"
              />
              <text v-for="v in [2,4,6,8,10]" :key="'l'+v"
                :x="PAD_L - 6" :y="scoreToY(v) + 4"
                font-size="10" fill="#94a3b8" text-anchor="end"
              >{{ v }}</text>
              <polygon :points="areaPoints" fill="url(#areaGrad)" />
              <polyline :points="linePoints" fill="none" stroke="#5f9e75" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />
              <circle v-for="p in chartPoints" :key="p.date" :cx="p.x" :cy="p.y" r="3.5" fill="white" stroke="#5f9e75" stroke-width="2" />
              <text v-for="p in xLabels" :key="'xl'+p.date" :x="p.x" :y="SVG_H - 3" font-size="10" fill="#94a3b8" text-anchor="middle">{{ p.label }}</text>
            </svg>
            <div v-else-if="chartLoading" class="chart-empty">
              <Loader2 :size="16" :stroke-width="1.5" class="spin" /> 加载中…
            </div>
            <div v-else class="chart-empty">
              <BarChart2 :size="24" :stroke-width="1" style="color:#c8d8cc" />
              <p>近 {{ chartRange }} 天暂无记录</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  BookHeart, CalendarDays, TrendingUp, Sparkles,
  BrainCircuit, Save, Trash2, ChevronLeft, ChevronRight,
  Loader2, BarChart2,
} from 'lucide-vue-next'
import { getDiaries, saveDiary, deleteDiary } from '@/api/diary'
import { useUserId } from '@/composables/useUserId'

// ── Constants ──────────────────────────────────────────────────────────────────
const SVG_W = 560, SVG_H = 160
const PAD_L = 36, PAD_R = 20, PAD_T = 12, PAD_B = 28
const CH = SVG_H - PAD_T - PAD_B

const userId = useUserId()
const today  = new Date().toISOString().slice(0, 10)

const emotionOptions = [
  { emoji: '😊', label: '开心' }, { emoji: '😌', label: '平静' },
  { emoji: '😰', label: '焦虑' }, { emoji: '😔', label: '悲伤' },
  { emoji: '😤', label: '烦躁' }, { emoji: '😴', label: '疲惫' },
  { emoji: '🤩', label: '兴奋' }, { emoji: '😶', label: '空白' },
  { emoji: '🥺', label: '委屈' }, { emoji: '💪', label: '充实' },
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
    saveMsg.value = '记录已保存 ✓'; saveMsgType.value = 'ok'
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
  { label: '1-2', color: '#fca5a5' }, { label: '3-4', color: '#fdba74' },
  { label: '5-6', color: '#fde68a' }, { label: '7-8', color: '#86efac' }, { label: '9-10', color: '#34d399' },
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

const setRange = async (r) => { chartRange.value = r; await loadChartData() }
const scoreToY = (score) => PAD_T + CH - ((score - 1) / 9) * CH

const chartPoints = computed(() => {
  const data = chartEntries.value
  if (data.length < 1) return []
  const minDate = data[0].date, maxDate = data[data.length - 1].date
  const spanMs = Math.max(new Date(maxDate) - new Date(minDate), 1)
  const W = SVG_W - PAD_L - PAD_R
  return data.map(e => ({ date: e.date, x: PAD_L + ((new Date(e.date) - new Date(minDate)) / spanMs) * W, y: scoreToY(e.mood_score) }))
})

const linePoints = computed(() => chartPoints.value.map(p => `${p.x},${p.y}`).join(' '))
const areaPoints = computed(() => {
  if (!chartPoints.value.length) return ''
  const first = chartPoints.value[0], last = chartPoints.value[chartPoints.value.length - 1]
  const base = SVG_H - PAD_B
  return [`${first.x},${base}`, ...chartPoints.value.map(p => `${p.x},${p.y}`), `${last.x},${base}`].join(' ')
})
const xLabels = computed(() => {
  const pts = chartPoints.value
  if (pts.length < 2) return []
  const step = Math.max(1, Math.floor(pts.length / 6))
  return pts.filter((_, i) => i === 0 || i === pts.length - 1 || i % step === 0).map(p => ({ date: p.date, x: p.x, label: p.date.slice(5) }))
})

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
})
</script>

<style scoped>
.diary-page {
  background: #f4f8f5;
  height: calc(100vh - 108px);
  overflow: hidden;
  padding: 16px 0 0;
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
  background: white;
  border: 1px solid #cfe8da;
  overflow: hidden;
  flex-shrink: 0;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  background: #f5fbf7;
  border-bottom: 1px solid #e4f0e8;
}

/* ── Editor ── */
.editor-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.field-row { padding: 10px 14px 0; }
.field-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}
.date-input {
  width: 100%;
  padding: 6px 9px;
  border: 1px solid #d0dce8;
  font-size: 12.5px;
  color: #1e293b;
  outline: none;
  box-sizing: border-box;
}
.date-input:focus { border-color: #5f9e75; }

/* Slider */
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
.score-label-text { font-size: 11.5px; color: #64748b; font-weight: 400; }
.slider-wrap { display: flex; align-items: center; gap: 8px; padding: 2px 0; }
.slider-min, .slider-max { font-size: 14px; flex-shrink: 0; }
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
.mood-slider:hover::-webkit-slider-thumb { box-shadow: 0 2px 7px rgba(95,158,117,0.45); }
.slider-ticks { display: flex; justify-content: space-between; padding: 1px 0 0; }
.tick { font-size: 9.5px; color: #cbd5e1; width: 10%; text-align: center; transition: color 0.15s; }
.tick.active { color: #5f9e75; font-weight: 600; }

/* Tags */
.tag-grid { display: flex; flex-wrap: wrap; gap: 5px; }
.tag-btn {
  padding: 3px 9px;
  border: 1px solid #d0dce8;
  background: none;
  font-size: 12px;
  color: #475569;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.12s;
}
.tag-btn:hover { border-color: #5f9e75; color: #5f9e75; }
.tag-btn.selected { background: #edf7f2; border-color: #5f9e75; color: #3a7d5a; font-weight: 600; }

/* Textarea */
.diary-textarea {
  width: 100%;
  resize: none;
  padding: 8px 10px;
  border: 1px solid #d0dce8;
  font-size: 13px;
  line-height: 1.65;
  color: #1e293b;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
}
.diary-textarea:focus { border-color: #5f9e75; }

/* Actions */
.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 10px 14px 12px;
  margin-top: auto;
}
.btn-save, .btn-delete {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  border-radius: 2px;
  transition: background 0.15s;
}
.btn-save { background: #5f9e75; color: white; }
.btn-save:hover { background: #4e8a63; }
.btn-save:disabled { background: #9fceaf; cursor: default; }
.btn-delete { background: none; border: 1px solid #fca5a5; color: #dc2626; }
.btn-delete:hover { background: #fef2f2; }
.save-msg { padding: 0 14px 8px; font-size: 12px; text-align: right; margin: 0; }
.save-msg.ok { color: #16a34a; }
.save-msg.err { color: #dc2626; }

/* ── Right col layout ── */
.right-col { gap: 14px; }
.right-top { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

/* ── Calendar ── */
.calendar-card .card-title { justify-content: flex-start; }
.cal-nav { margin-left: auto; display: flex; align-items: center; gap: 6px; }
.cal-month { font-size: 12px; font-weight: 600; color: #374151; }
.cal-arrow {
  display: flex;
  background: none;
  border: 1px solid #d0dce8;
  border-radius: 2px;
  padding: 1px 3px;
  cursor: pointer;
  color: #5f9e75;
}
.cal-arrow:hover { background: #edf7f2; }

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
  position: relative;
}
.cal-circle:hover { background: #edf7f2 !important; }
.cal-circle.has-entry { color: rgba(0,0,0,0.55); font-weight: 700; }
.cal-circle.is-today { box-shadow: 0 0 0 2px #5f9e75; }
.cal-circle.is-selected { box-shadow: 0 0 0 2px #3a7d5a, 0 0 0 4px rgba(58,125,90,0.2); }

.cal-legend {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 4px 10px 10px;
}
.legend-item { display: flex; align-items: center; gap: 3px; font-size: 10.5px; color: #64748b; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }

/* ── AI Card ── */
.coming-soon {
  margin-left: auto;
  font-size: 10.5px;
  font-weight: 400;
  background: #fff3cd;
  color: #92400e;
  padding: 1px 7px;
  border-radius: 2px;
}
.ai-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px 16px 20px;
  gap: 7px;
  text-align: center;
}
.ai-avatar {
  width: 52px; height: 52px;
  border-radius: 50%;
  background: #f0f9f4;
  border: 1px dashed #5f9e75;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5f9e75;
  margin-bottom: 2px;
}
.ai-tip { font-size: 12.5px; color: #475569; margin: 0; line-height: 1.5; }
.ai-sub { font-size: 11.5px; color: #94a3b8; margin: 0; }

/* ── Chart ── */
.chart-card { flex: 1; display: flex; flex-direction: column; }
.range-tabs { margin-left: auto; display: flex; gap: 4px; }
.range-tab {
  padding: 2px 9px;
  font-size: 11.5px;
  border: 1px solid #d0dce8;
  background: none;
  color: #64748b;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.12s;
}
.range-tab:hover { border-color: #5f9e75; color: #5f9e75; }
.range-tab.active { background: #5f9e75; color: white; border-color: #5f9e75; }
.chart-wrap { flex: 1; padding: 10px 14px 12px; display: flex; align-items: center; }
.chart-svg { width: 100%; height: 160px; display: block; }
.chart-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  width: 100%; height: 120px; gap: 6px; color: #94a3b8; font-size: 12.5px;
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
