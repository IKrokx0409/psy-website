<template>
  <div class="sci-page">

    <!-- 页头 -->
    <div class="sci-header">
      <div class="sci-header-inner">
        <router-link to="/" class="back-link">
          <ChevronLeft :size="15" :stroke-width="2" /> 返回首页
        </router-link>
        <h1 class="sci-title">心理资源</h1>
        <p class="sci-subtitle">哈尔滨工业大学（深圳）心理健康教育与咨询中心</p>
      </div>
    </div>

    <!-- Tab 栏 -->
    <div class="sci-tabs-wrap">
      <div class="sci-tabs">
        <button
          v-for="t in TABS" :key="t.key"
          :class="['sci-tab', { active: activeTab === t.key }]"
          @click="activeTab = t.key"
        >
          <component :is="t.icon" :size="14" :stroke-width="1.5" />
          {{ t.label }}
        </button>
      </div>
    </div>

    <!-- ══ 知识库 ══════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'library'" class="sci-body">
      <div class="cat-bar">
        <button
          v-for="c in CATEGORIES" :key="c"
          :class="['cat-btn', { active: activeCat === c }]"
          @click="activeCat = c"
        >{{ c }}</button>
      </div>

      <div v-if="resLoading" class="sci-state">
        <Loader2 :size="26" :stroke-width="1.5" class="spin" /><span>加载中…</span>
      </div>
      <div v-else-if="resError" class="sci-state sci-state-error">
        <AlertCircle :size="22" /><span>加载失败</span>
      </div>
      <div v-else-if="filteredResources.length === 0" class="sci-state">
        <BookOpen :size="36" :stroke-width="1" style="opacity:.3" /><span>暂无相关文章</span>
      </div>
      <div v-else class="res-grid">
        <router-link
          v-for="r in filteredResources" :key="r.id"
          :to="`/resources/${r.id}`"
          class="res-card"
        >
          <span class="res-cat-tag">{{ r.category }}</span>
          <h3 class="res-title">{{ r.title }}</h3>
          <p class="res-summary">{{ r.summary || '暂无摘要' }}</p>
          <span class="res-more">阅读全文 →</span>
        </router-link>
      </div>
    </div>

    <!-- ══ 心理问卷 ════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'quiz'" class="sci-body">
      <div v-if="qLoading" class="sci-state">
        <Loader2 :size="26" :stroke-width="1.5" class="spin" /><span>加载中…</span>
      </div>
      <div v-else-if="qError" class="sci-state sci-state-error">
        <AlertCircle :size="22" /><span>加载失败</span>
      </div>
      <div v-else-if="questionnaires.length === 0" class="sci-state">
        <ClipboardList :size="36" :stroke-width="1" style="opacity:.3" /><span>暂无问卷</span>
      </div>

      <template v-else>
        <!-- 问卷列表 -->
        <div v-if="!activeQuiz" class="quiz-list">
          <div v-for="q in questionnaires" :key="q.id" class="quiz-card">
            <div class="quiz-card-left">
              <ClipboardList :size="28" :stroke-width="1.2" class="quiz-icon" />
            </div>
            <div class="quiz-card-body">
              <h3 class="quiz-title">{{ q.title }}</h3>
              <p class="quiz-desc">{{ q.description || '点击开始自测' }}</p>
            </div>
            <button class="quiz-start-btn" @click="startQuiz(q.id)">开始自测</button>
          </div>
        </div>

        <!-- 答题界面 -->
        <div v-else class="quiz-page">
          <button class="quiz-back-btn" @click="exitQuiz">
            <ChevronLeft :size="14" :stroke-width="2" /> 返回列表
          </button>

          <div v-if="qDetailLoading" class="sci-state">
            <Loader2 :size="26" :stroke-width="1.5" class="spin" /><span>加载中…</span>
          </div>

          <!-- 结果页 -->
          <div v-else-if="quizResult" class="quiz-result">
            <div :class="['result-level', `level-${quizResult.level}`]">
              <CheckCircle2 :size="40" :stroke-width="1.2" />
              <span class="result-label">{{ quizResult.label }}</span>
            </div>
            <p class="result-desc">{{ quizResult.desc }}</p>
            <div class="result-score">总得分：{{ totalScore }} 分</div>
            <div class="result-actions">
              <button class="quiz-retry-btn" @click="retryQuiz">重新作答</button>
              <button class="quiz-back-btn2" @click="exitQuiz">返回列表</button>
            </div>
          </div>

          <!-- 答题表单 -->
          <div v-else-if="quizDetail" class="quiz-form">
            <h2 class="quiz-form-title">{{ quizDetail.title }}</h2>
            <p v-if="quizDetail.description" class="quiz-form-desc">{{ quizDetail.description }}</p>

            <div
              v-for="(q, qi) in parsedQuestions" :key="q.id"
              :class="['q-block', { 'q-unanswered': submitted && answers[qi] === undefined }]"
            >
              <p class="q-text"><span class="q-num">{{ qi + 1 }}.</span> {{ q.text }}</p>
              <div class="q-options">
                <label
                  v-for="opt in q.options" :key="opt.text"
                  :class="['q-option', { selected: answers[qi] === opt.score }]"
                >
                  <input type="radio" :name="`q${qi}`" :value="opt.score" v-model="answers[qi]" />
                  {{ opt.text }}
                </label>
              </div>
            </div>

            <p v-if="submitted && hasUnanswered" class="q-warn">请完成所有题目后再提交</p>
            <button class="quiz-submit-btn" @click="submitQuiz">提交并查看结果</button>
          </div>
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  ChevronLeft, BookOpen, ClipboardList, Loader2, AlertCircle, CheckCircle2,
} from 'lucide-vue-next'
import { getResources } from '@/api/resources'
import { getQuestionnaires, getQuestionnaire } from '@/api/questionnaires'

const TABS = [
  { key: 'library', label: '知识库',   icon: BookOpen      },
  { key: 'quiz',    label: '心理问卷', icon: ClipboardList },
]
const CATEGORIES = ['全部', '情绪管理', '压力应对', '人际关系', '睡眠健康', '危机干预']

const activeTab = ref('library')

// ── 知识库 ────────────────────────────────────────────────────────────────
const resources  = ref([])
const resLoading = ref(true)
const resError   = ref(false)
const activeCat  = ref('全部')

const filteredResources = computed(() =>
  activeCat.value === '全部'
    ? resources.value
    : resources.value.filter(r => r.category === activeCat.value)
)

// ── 问卷 ──────────────────────────────────────────────────────────────────
const questionnaires = ref([])
const qLoading       = ref(true)
const qError         = ref(false)

onMounted(async () => {
  try { resources.value = await getResources() }
  catch { resError.value = true }
  finally { resLoading.value = false }

  try { questionnaires.value = await getQuestionnaires() }
  catch { qError.value = true }
  finally { qLoading.value = false }
})

// ── 答题状态 ──────────────────────────────────────────────────────────────
const activeQuiz     = ref(null)
const quizDetail     = ref(null)
const qDetailLoading = ref(false)
const answers        = ref({})
const submitted      = ref(false)
const quizResult     = ref(null)

const parsedQuestions = computed(() => {
  try { return JSON.parse(quizDetail.value?.questions_json || '[]') } catch { return [] }
})
const parsedScoring = computed(() => {
  try { return JSON.parse(quizDetail.value?.scoring_json || '[]') } catch { return [] }
})
const totalScore = computed(() =>
  Object.values(answers.value).reduce((s, v) => s + (v ?? 0), 0)
)
const hasUnanswered = computed(() =>
  parsedQuestions.value.some((_, i) => answers.value[i] === undefined)
)

const startQuiz = async (id) => {
  activeQuiz.value = id
  quizDetail.value = null
  answers.value = {}
  submitted.value = false
  quizResult.value = null
  qDetailLoading.value = true
  try { quizDetail.value = await getQuestionnaire(id) }
  finally { qDetailLoading.value = false }
}

const submitQuiz = () => {
  submitted.value = true
  if (hasUnanswered.value) return
  const score = totalScore.value
  const range = parsedScoring.value.find(r => score >= r.min && score <= r.max)
  quizResult.value = range
    ? { label: range.label, desc: range.desc, level: range.level }
    : { label: '已完成', desc: `总分：${score} 分`, level: 'good' }
}

const retryQuiz = () => { answers.value = {}; submitted.value = false; quizResult.value = null }
const exitQuiz  = () => { activeQuiz.value = null; quizDetail.value = null; quizResult.value = null; submitted.value = false; answers.value = {} }
</script>

<style scoped>
.sci-page { min-height: 100%; background: #f5f4f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

/* ── 页头 */
.sci-header {
  background: linear-gradient(160deg, #5f9e75 0%, #4d8764 100%);
  padding: 56px 32px 48px;
  border-bottom: 3px solid rgba(255,255,255,0.2);
  box-shadow: 0 2px 6px rgba(30,100,60,0.3);
}
.sci-header-inner { max-width: 900px; margin: 0 auto; }
.back-link {
  display: inline-flex; align-items: center; gap: 4px;
  color: rgba(255,255,255,0.6); text-decoration: none; font-size: 13px;
  margin-bottom: 28px; transition: color 0.15s;
}
.back-link:hover { color: rgba(255,255,255,0.9); }
.sci-title {
  font-family: 'SimSun','宋体','STSong',Georgia,serif;
  font-size: 40px; font-weight: 900; color: #fff;
  letter-spacing: 8px; margin: 0 0 10px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.sci-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 0; letter-spacing: 1px; }

/* ── Tab */
.sci-tabs-wrap { background: white; border-bottom: 1px solid #d8d2c8; position: sticky; top: 0; z-index: 10; }
.sci-tabs { max-width: 900px; margin: 0 auto; padding: 0 32px; display: flex; }
.sci-tab {
  display: flex; align-items: center; gap: 6px;
  padding: 16px 24px; background: none; border: none;
  font-size: 14px; color: #5a5040; cursor: pointer;
  font-weight: 500; position: relative; transition: color 0.15s;
}
.sci-tab::after {
  content: ''; position: absolute; bottom: -1px; left: 0; right: 0;
  height: 2px; background: #5f9e75; transform: scaleX(0); transition: transform 0.2s;
}
.sci-tab:hover { color: #5f9e75; }
.sci-tab.active { color: #3d7a56; font-weight: 600; }
.sci-tab.active::after { transform: scaleX(1); }

/* ── Body */
.sci-body { max-width: 900px; margin: 0 auto; padding: 32px 32px 80px; }

.sci-state { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 80px 0; color: #94a3b8; font-size: 14px; }
.sci-state-error { color: #b91c1c; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 分类筛选 */
.cat-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px; }
.cat-btn { padding: 6px 18px; border-radius: 20px; border: 1.5px solid #d0c9bc; background: white; font-size: 13px; color: #5a5040; cursor: pointer; transition: all 0.15s; }
.cat-btn:hover { border-color: #5f9e75; color: #5f9e75; }
.cat-btn.active { background: #5f9e75; border-color: #5f9e75; color: white; }

/* ── 知识库卡片 */
.res-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.res-card {
  display: flex; flex-direction: column; gap: 10px;
  background: white; border: 1px solid #d8d2c8; padding: 24px;
  text-decoration: none; transition: border-color 0.15s, box-shadow 0.15s;
}
.res-card:hover { border-color: #5f9e75; box-shadow: 0 4px 16px rgba(60,120,80,0.1); }
.res-cat-tag { font-size: 11.5px; color: #5f9e75; font-weight: 500; letter-spacing: 0.5px; }
.res-title { font-family: 'SimSun','宋体',Georgia,serif; font-size: 16px; font-weight: 600; color: #1e1a14; margin: 0; line-height: 1.5; }
.res-summary { font-size: 13.5px; color: #5a5040; line-height: 1.7; margin: 0; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.res-more { font-size: 12.5px; color: #5f9e75; font-weight: 500; margin-top: auto; }

/* ── 问卷列表 */
.quiz-list { display: flex; flex-direction: column; gap: 12px; }
.quiz-card { display: flex; align-items: center; gap: 20px; background: white; border: 1px solid #d8d2c8; padding: 24px 28px; transition: border-color 0.15s, box-shadow 0.15s; }
.quiz-card:hover { border-color: #5f9e75; box-shadow: 0 4px 16px rgba(60,120,80,0.08); }
.quiz-card-left { flex-shrink: 0; }
.quiz-icon { color: #5f9e75; }
.quiz-card-body { flex: 1; }
.quiz-title { font-family: 'SimSun','宋体',Georgia,serif; font-size: 17px; font-weight: 600; color: #1e1a14; margin: 0 0 6px; }
.quiz-desc { font-size: 13.5px; color: #7a6e5a; margin: 0; line-height: 1.6; }
.quiz-start-btn { flex-shrink: 0; background: #5f9e75; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: 600; cursor: pointer; border-radius: 2px; transition: background 0.15s; }
.quiz-start-btn:hover { background: #4d8764; }

/* ── 答题页 */
.quiz-back-btn { display: inline-flex; align-items: center; gap: 5px; background: none; border: 1.5px solid #d0c9bc; color: #5a5040; padding: 8px 16px; font-size: 13px; cursor: pointer; border-radius: 2px; margin-bottom: 24px; transition: background 0.15s; }
.quiz-back-btn:hover { background: #f0ece4; }

.quiz-form { background: white; border: 1px solid #d8d2c8; padding: 36px 40px; }
.quiz-form-title { font-family: 'SimSun','宋体',Georgia,serif; font-size: 22px; font-weight: 700; color: #1e1a14; margin: 0 0 10px; letter-spacing: 1px; }
.quiz-form-desc { font-size: 14px; color: #7a6e5a; line-height: 1.7; margin: 0 0 28px; }

.q-block { margin-bottom: 28px; padding-bottom: 24px; border-bottom: 1px solid #ece8e0; }
.q-block:last-of-type { border-bottom: none; }
.q-block.q-unanswered .q-text { color: #b91c1c; }
.q-text { font-size: 15px; color: #2a241a; line-height: 1.7; margin: 0 0 14px; }
.q-num { font-weight: 700; color: #5f9e75; margin-right: 4px; }

.q-options { display: flex; flex-direction: column; gap: 8px; }
.q-option { display: flex; align-items: center; gap: 10px; padding: 10px 16px; border: 1.5px solid #e0dbd0; cursor: pointer; font-size: 14px; color: #3a3020; transition: border-color 0.15s, background 0.15s; }
.q-option:hover { border-color: #5f9e75; background: #f5fbf7; }
.q-option.selected { border-color: #5f9e75; background: #edf7f2; color: #1e3a2e; font-weight: 500; }
.q-option input { accent-color: #5f9e75; }

.q-warn { font-size: 13px; color: #b91c1c; margin: 0 0 16px; }
.quiz-submit-btn { background: #5f9e75; color: white; border: none; padding: 12px 36px; font-size: 15px; font-weight: 600; cursor: pointer; border-radius: 2px; transition: background 0.15s; }
.quiz-submit-btn:hover { background: #4d8764; }

/* ── 结果页 */
.quiz-result { background: white; border: 1px solid #d8d2c8; padding: 60px 40px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 16px; }
.result-level { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.level-good     svg { color: #5f9e75; }
.level-mild     svg { color: #f59e0b; }
.level-moderate svg { color: #f97316; }
.level-severe   svg { color: #ef4444; }
.result-label { font-family: 'SimSun','宋体',Georgia,serif; font-size: 28px; font-weight: 700; color: #1e1a14; }
.result-desc  { font-size: 15px; color: #5a5040; line-height: 1.8; max-width: 480px; margin: 0; }
.result-score { font-size: 13px; color: #8a8070; }
.result-actions { display: flex; gap: 12px; }
.quiz-retry-btn { background: #5f9e75; color: white; border: none; padding: 10px 28px; font-size: 14px; font-weight: 600; cursor: pointer; border-radius: 2px; transition: background 0.15s; }
.quiz-retry-btn:hover { background: #4d8764; }
.quiz-back-btn2 { background: none; border: 1.5px solid #d0c9bc; color: #5a5040; padding: 10px 28px; font-size: 14px; cursor: pointer; border-radius: 2px; transition: background 0.15s; }
.quiz-back-btn2:hover { background: #f0ece4; }

@media (max-width: 640px) {
  .res-grid { grid-template-columns: 1fr; }
  .sci-body { padding: 24px 16px 60px; }
  .quiz-form { padding: 24px 20px; }
  .quiz-card { flex-wrap: wrap; }
}
</style>
