<template>
  <div class="cc-page">

    <!-- 页头 -->
    <div class="cc-header">
      <div class="cc-header-inner">
        <div class="cc-header-left">
          <BookOpen :size="22" :stroke-width="1.5" />
          <span>心理课</span>
        </div>
        <div v-if="isTeacher" class="cc-header-right">
          <button class="btn-primary" @click="openCourseForm()">
            <Plus :size="14" :stroke-width="2" /> 新建课程
          </button>
        </div>
        <div v-else class="cc-my-id">
          我的学生 ID：<code>{{ userId }}</code>
          <span class="cc-id-hint">（将此 ID 告知教师以加入班级）</span>
        </div>
      </div>
    </div>

    <div class="cc-body">

      <!-- 加载/错误 -->
      <div v-if="loading" class="cc-state"><Loader2 :size="28" class="spin" /><span>加载中…</span></div>
      <div v-else-if="error"  class="cc-state cc-state-err"><AlertCircle :size="20" /><span>{{ error }}</span></div>

      <!-- 教师视图：课程列表 -->
      <template v-else-if="isTeacher">
        <div v-if="courses.length === 0" class="cc-state">
          <BookOpen :size="40" :stroke-width="1" style="opacity:.25" />
          <span>暂无课程，点击右上角新建</span>
        </div>
        <div v-for="course in courses" :key="course.id" class="course-card">
          <div class="course-card-head">
            <div class="course-info">
              <div class="course-name">{{ course.name }}</div>
              <div class="course-meta">{{ course.semester }}</div>
            </div>
            <div class="course-actions">
              <button class="btn-sm btn-ghost" @click="openClassForm(course)">
                <Plus :size="13" :stroke-width="2" /> 新建班级
              </button>
              <button class="btn-sm btn-danger" @click="doDeleteCourse(course)">
                <Trash2 :size="13" :stroke-width="2" />
              </button>
            </div>
          </div>
          <div v-if="course.description" class="course-desc">{{ course.description }}</div>

          <!-- 该课程下的班级 -->
          <div class="class-list">
            <div v-if="classesByCourse[course.id]?.length === 0" class="class-empty">暂无班级</div>
            <router-link
              v-for="cls in classesByCourse[course.id]"
              :key="cls.id"
              :to="`/course/${cls.id}`"
              class="class-item"
            >
              <div class="class-item-left">
                <Users :size="15" :stroke-width="1.5" class="class-icon" />
                <span class="class-name">{{ cls.name }}</span>
              </div>
              <div class="class-item-stats">
                <span><Users :size="12" /> {{ cls.member_count }} 人</span>
                <span><FileText :size="12" /> {{ cls.assignment_count }} 个作业</span>
                <span><MessageSquare :size="12" /> {{ cls.thread_count }} 条讨论</span>
              </div>
              <ChevronRight :size="15" class="class-chevron" />
            </router-link>
          </div>
        </div>
      </template>

      <!-- 学生视图：我的班级 -->
      <template v-else>
        <div v-if="myClasses.length === 0" class="cc-state">
          <BookOpen :size="40" :stroke-width="1" style="opacity:.25" />
          <span>你还没有加入任何课程，请联系教师添加</span>
        </div>
        <router-link
          v-for="cls in myClasses"
          :key="cls.id"
          :to="`/course/${cls.id}`"
          class="student-class-card"
        >
          <div class="sc-left">
            <div class="sc-name">{{ cls.name }}</div>
            <div class="sc-meta">{{ cls.assignment_count }} 个作业 · {{ cls.thread_count }} 条讨论</div>
          </div>
          <ChevronRight :size="18" class="sc-chevron" />
        </router-link>
      </template>

    </div>

    <!-- 新建课程弹窗 -->
    <Transition name="modal">
      <div v-if="courseFormVisible" class="modal-overlay" @click.self="courseFormVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>新建课程</span>
            <button class="modal-close" @click="courseFormVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>课程名称</label>
              <input v-model="courseForm.name" class="form-input" placeholder="如：大学生心理健康教育" />
            </div>
            <div class="form-group">
              <label>学期</label>
              <input v-model="courseForm.semester" class="form-input" placeholder="如：2025-2026-2" />
            </div>
            <div class="form-group">
              <label>课程简介 <span class="optional">（选填）</span></label>
              <textarea v-model="courseForm.description" class="form-textarea" rows="3" placeholder="课程介绍…" />
            </div>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="courseFormVisible = false">取消</button>
            <button class="btn-primary" :disabled="saving" @click="saveCourse">
              {{ saving ? '保存中…' : '确认创建' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 新建班级弹窗 -->
    <Transition name="modal">
      <div v-if="classFormVisible" class="modal-overlay" @click.self="classFormVisible = false">
        <div class="modal">
          <div class="modal-head">
            <span>在「{{ classFormCourse?.name }}」下新建班级</span>
            <button class="modal-close" @click="classFormVisible = false"><X :size="16" /></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>班级名称</label>
              <input v-model="classForm.name" class="form-input" placeholder="如：计算机2301班" />
            </div>
          </div>
          <div class="modal-foot">
            <button class="btn-cancel" @click="classFormVisible = false">取消</button>
            <button class="btn-primary" :disabled="saving" @click="saveClass">
              {{ saving ? '保存中…' : '确认创建' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  BookOpen, Plus, Trash2, Users, FileText, MessageSquare,
  ChevronRight, X, Loader2, AlertCircle,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useUserId } from '@/composables/useUserId'
import {
  getCourses, createCourse, deleteCourse,
  getClasses, createClass,
  getMyClasses,
} from '@/api/courses'

const { isTeacher } = useAuth()
const userId = useUserId()
const router = useRouter()

const loading = ref(true)
const error   = ref('')
const saving  = ref(false)

// ── 教师数据 ──────────────────────────────────────────────────────────────────
const courses         = ref([])
const classesByCourse = reactive({})

const loadTeacher = async () => {
  courses.value = await getCourses(userId)
  for (const c of courses.value) {
    classesByCourse[c.id] = await getClasses(c.id)
  }
}

// ── 学生数据 ──────────────────────────────────────────────────────────────────
const myClasses = ref([])

onMounted(async () => {
  try {
    if (isTeacher.value) {
      await loadTeacher()
    } else {
      myClasses.value = await getMyClasses(userId)
    }
  } catch (e) {
    error.value = '加载失败，请检查后端服务'
  } finally {
    loading.value = false
  }
})

// ── 新建课程 ──────────────────────────────────────────────────────────────────
const courseFormVisible = ref(false)
const courseForm = reactive({ name: '', semester: '', description: '' })

const openCourseForm = () => {
  Object.assign(courseForm, { name: '', semester: '', description: '' })
  courseFormVisible.value = true
}

const saveCourse = async () => {
  if (!courseForm.name.trim() || !courseForm.semester.trim()) return
  saving.value = true
  try {
    const c = await createCourse({
      name: courseForm.name.trim(),
      semester: courseForm.semester.trim(),
      description: courseForm.description.trim() || null,
      teacher_id: userId,
    })
    courses.value.unshift(c)
    classesByCourse[c.id] = []
    courseFormVisible.value = false
  } finally {
    saving.value = false
  }
}

const doDeleteCourse = async (course) => {
  if (!confirm(`确认删除课程「${course.name}」及其所有班级？`)) return
  await deleteCourse(course.id)
  courses.value = courses.value.filter(c => c.id !== course.id)
  delete classesByCourse[course.id]
}

// ── 新建班级 ──────────────────────────────────────────────────────────────────
const classFormVisible = ref(false)
const classFormCourse  = ref(null)
const classForm = reactive({ name: '' })

const openClassForm = (course) => {
  classFormCourse.value = course
  classForm.name = ''
  classFormVisible.value = true
}

const saveClass = async () => {
  if (!classForm.name.trim()) return
  saving.value = true
  try {
    const cls = await createClass(classFormCourse.value.id, {
      name: classForm.name.trim(),
      teacher_id: userId,
    })
    classesByCourse[classFormCourse.value.id].push(cls)
    classFormVisible.value = false
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.cc-page { background: #f6f2ec; min-height: 100vh; }

.cc-header {
  background: linear-gradient(160deg, #2d5a42 0%, #4a8763 100%);
  padding: 20px 0;
  color: white;
}
.cc-header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.cc-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  font-family: var(--f-serif, serif);
  letter-spacing: 1px;
}
.cc-my-id {
  font-size: 13px;
  color: rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  gap: 8px;
}
.cc-my-id code {
  background: rgba(255,255,255,0.2);
  padding: 2px 8px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
  color: white;
}
.cc-id-hint { font-size: 12px; opacity: 0.65; }

.cc-body {
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px 24px;
}

.cc-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: #94a3b8;
  font-size: 14px;
}
.cc-state-err { color: #b84545; }

/* ── 课程卡片 ── */
.course-card {
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  margin-bottom: 20px;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}
.course-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0ebe2;
  gap: 12px;
}
.course-name { font-size: 16px; font-weight: 700; color: #1c2b22; }
.course-meta { font-size: 12px; color: #7a9080; margin-top: 2px; }
.course-desc { padding: 8px 20px 0; font-size: 13px; color: #64748b; }
.course-actions { display: flex; gap: 8px; flex-shrink: 0; }

/* ── 班级列表 ── */
.class-list { padding: 8px 12px 12px; display: flex; flex-direction: column; gap: 4px; }
.class-empty { font-size: 13px; color: #b0bec5; padding: 8px 8px; }
.class-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--r-md);
  border: 1px solid #ede8e0;
  background: var(--c-beige-card);
  text-decoration: none;
  color: inherit;
  transition: background var(--t-base), border-color var(--t-base);
}
.class-item:hover { background: #f5ead8; border-color: #c9a96e; }
.class-item-left { display: flex; align-items: center; gap: 7px; flex: 1; }
.class-icon { color: #4a8763; }
.class-name { font-size: 14px; font-weight: 600; color: #1c2b22; }
.class-item-stats {
  display: flex;
  gap: 14px;
  font-size: 12px;
  color: #7a9080;
  margin-right: 8px;
}
.class-item-stats span { display: flex; align-items: center; gap: 4px; }
.class-chevron { color: #b0bec5; }

/* ── 学生班级卡片 ── */
.student-class-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: white;
  border: 1px solid var(--c-beige-border);
  border-radius: var(--r-lg);
  margin-bottom: 12px;
  text-decoration: none;
  color: inherit;
  box-shadow: var(--shadow-xs);
  transition: border-color var(--t-base), background var(--t-base), transform var(--t-base);
}
.student-class-card:hover { border-color: #4a8763; background: #f5fbf7; transform: translateY(-1px); }
.student-class-card:hover { border-color: #4a8763; background: #f5fbf7; }
.sc-name { font-size: 16px; font-weight: 700; color: #1c2b22; }
.sc-meta { font-size: 13px; color: #7a9080; margin-top: 4px; }
.sc-chevron { color: #b0bec5; }

/* ── 按钮 ── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: var(--c-green-deep);
  color: white;
  border: none;
  border-radius: var(--r-sm);
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--t-base);
}
.btn-primary:hover:not(:disabled) { background: #2d5a42; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-sm {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: var(--r-xs);
  font-size: 12.5px;
  cursor: pointer;
  transition: background var(--t-base);
  border: 1px solid;
}
.btn-ghost { background: none; border-color: #d4e8db; color: #3d6e52; }
.btn-ghost:hover { background: #f0fbf4; }
.btn-danger { background: none; border-color: #e8c4c4; color: #b84545; }
.btn-danger:hover { background: #fdf2f2; }

/* ── 弹窗 ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 24px;
}
.modal {
  background: white;
  border-radius: var(--r-xl);
  width: 100%;
  max-width: 480px;
  box-shadow: var(--shadow-xl);
}
.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e8e0d4;
  font-size: 15px;
  font-weight: 600;
  color: #1c2b22;
}
.modal-close { background: none; border: none; cursor: pointer; color: #94a3b8; display: flex; }
.modal-close:hover { color: #374151; }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.modal-foot { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 20px; border-top: 1px solid #e8e0d4; }

.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 12.5px; font-weight: 600; color: #4a8763; letter-spacing: 0.04em; text-transform: uppercase; }
.optional { font-weight: 400; color: #94a3b8; text-transform: none; }
.form-input, .form-textarea {
  border: 1px solid #ddd6cc;
  border-radius: 4px;
  padding: 8px 10px;
  font-size: 13.5px;
  color: #1c2b22;
  background: #fdfaf5;
  font-family: inherit;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}
.form-input:focus, .form-textarea:focus { border-color: #4a8763; box-shadow: 0 0 0 2px rgba(74,135,99,0.12); }
.form-textarea { resize: vertical; }

.btn-cancel {
  padding: 8px 18px;
  border: 1.5px solid #d4e8db;
  border-radius: var(--r-sm);
  background: white;
  color: #3d6e52;
  font-size: 13.5px;
  cursor: pointer;
}
.btn-cancel:hover { background: #f0fbf4; }

/* 弹窗动画 */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform 0.2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: translateY(12px); }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .cc-body { padding: 16px; }
  .cc-header-inner { padding: 0 16px; flex-wrap: wrap; gap: 8px; }
  .cc-my-id { font-size: 12px; }
  .cc-id-hint { display: none; }
  .course-card-head { flex-wrap: wrap; }
  .course-actions { width: 100%; justify-content: flex-end; }
  .modal-overlay { padding: 16px; }
  .modal { max-width: 100%; }
}
</style>
