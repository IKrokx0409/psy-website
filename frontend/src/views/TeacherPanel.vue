<template>
  <div class="tp-page">

    <!-- 页头 -->
    <div class="tp-header">
      <div class="tp-header-inner">
        <div class="tp-header-title">
          <ShieldCheck :size="22" :stroke-width="1.5" />
          <span>教师管理后台</span>
        </div>
        <!-- 主 Tab -->
        <div class="tp-main-tabs">
          <button
            v-for="t in MAIN_TABS" :key="t.key"
            :class="['tp-main-tab', { active: activeTab === t.key }]"
            @click="activeTab = t.key"
          >
            <component :is="t.icon" :size="15" :stroke-width="1.5" />
            {{ t.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ 树洞审核 ═══════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'treehole'" class="tp-body">

      <!-- 状态筛选 -->
      <div class="tp-filter-bar">
        <button
          v-for="f in TREEHOLE_FILTERS" :key="f.key"
          :class="['tp-filter-btn', { active: thFilter === f.key }]"
          @click="thFilter = f.key; loadPosts()"
        >
          {{ f.label }}
          <span v-if="thCounts[f.key] > 0" class="tp-badge">{{ thCounts[f.key] }}</span>
        </button>
      </div>

      <!-- 加载/错误 -->
      <div v-if="thLoading" class="tp-state">
        <Loader2 :size="24" :stroke-width="1.5" class="spin" />
        <span>加载中…</span>
      </div>
      <div v-else-if="thError" class="tp-state tp-state-error">
        <AlertCircle :size="20" :stroke-width="1.5" />
        <span>加载失败，请检查后端服务</span>
      </div>

      <!-- 帖子列表 -->
      <div v-else-if="thPosts.length === 0" class="tp-state">
        <MessageSquare :size="36" :stroke-width="1" style="opacity:.3" />
        <span>暂无帖子</span>
      </div>
      <div v-else class="tp-table-wrap">
        <table class="tp-table">
          <thead>
            <tr>
              <th style="width:60px">ID</th>
              <th style="width:120px">匿名昵称</th>
              <th>内容</th>
              <th style="width:100px">标签</th>
              <th style="width:90px">状态</th>
              <th style="width:130px">时间</th>
              <th style="width:160px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="post in thPosts" :key="post.id">
              <td class="td-id">#{{ post.id }}</td>
              <td>
                <span class="td-name">{{ post.anonymous_name }}</span>
              </td>
              <td>
                <p class="td-content">{{ post.content }}</p>
              </td>
              <td>
                <span v-for="tag in post.tags" :key="tag" class="td-tag">{{ tag }}</span>
              </td>
              <td>
                <span :class="['td-status', `status-${post.status}`]">
                  {{ STATUS_LABEL[post.status] || post.status }}
                </span>
              </td>
              <td class="td-time">{{ fmtDate(post.created_at) }}</td>
              <td>
                <div class="td-actions">
                  <template v-if="post.status === 'pending'">
                    <button class="act-btn act-approve" @click="doReview(post, 'approve')">通过</button>
                    <button class="act-btn act-reject" @click="doReview(post, 'reject')">拒绝</button>
                  </template>
                  <template v-else-if="post.status === 'delete_requested'">
                    <button class="act-btn act-approve" @click="doDelete(post)">确认删除</button>
                    <button class="act-btn act-neutral" @click="doReview(post, 'approve')">恢复发布</button>
                  </template>
                  <template v-else>
                    <button class="act-btn act-reject" @click="doDelete(post)">删除</button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ 公告管理 ═══════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'announcements'" class="tp-body">

      <div class="ann-toolbar">
        <span class="ann-count">共 {{ annList.length }} 条公告</span>
        <button class="ann-new-btn" @click="openAnnForm(null)">
          <Plus :size="15" :stroke-width="2" /> 新建公告
        </button>
      </div>

      <div v-if="annLoading" class="tp-state">
        <Loader2 :size="24" :stroke-width="1.5" class="spin" />
        <span>加载中…</span>
      </div>
      <div v-else-if="annError" class="tp-state tp-state-error">
        <AlertCircle :size="20" :stroke-width="1.5" />
        <span>加载失败，请检查后端服务</span>
      </div>
      <div v-else-if="annList.length === 0" class="tp-state">
        <Megaphone :size="36" :stroke-width="1" style="opacity:.3" />
        <span>暂无公告，点击右上角新建</span>
      </div>
      <div v-else class="tp-table-wrap">
        <table class="tp-table">
          <thead>
            <tr>
              <th style="width:60px">ID</th>
              <th>标题</th>
              <th style="width:100px">分类</th>
              <th style="width:110px">发布日期</th>
              <th style="width:90px">状态</th>
              <th style="width:130px">创建时间</th>
              <th style="width:180px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ann in annList" :key="ann.id">
              <td class="td-id">#{{ ann.id }}</td>
              <td><span class="td-ann-title">{{ ann.title }}</span></td>
              <td><span class="td-cat">{{ ann.category }}</span></td>
              <td class="td-time">{{ ann.published_at || '—' }}</td>
              <td>
                <span :class="['td-status', ann.is_published ? 'status-approved' : 'status-rejected']">
                  {{ ann.is_published ? '已发布' : '未发布' }}
                </span>
              </td>
              <td class="td-time">{{ fmtDate(ann.created_at) }}</td>
              <td>
                <div class="td-actions">
                  <button class="act-btn act-neutral" @click="openAnnForm(ann)">编辑</button>
                  <button
                    :class="['act-btn', ann.is_published ? 'act-reject' : 'act-approve']"
                    @click="togglePublish(ann)"
                  >{{ ann.is_published ? '下线' : '发布' }}</button>
                  <button class="act-btn act-reject" @click="doDeleteAnn(ann)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ 知识库管理 ════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'resources'" class="tp-body">
      <div class="ann-toolbar">
        <span class="ann-count">共 {{ resList.length }} 篇文章</span>
        <button class="ann-new-btn" @click="openResForm(null)">
          <Plus :size="15" :stroke-width="2" /> 新建文章
        </button>
      </div>
      <div v-if="resLoading" class="tp-state"><Loader2 :size="24" :stroke-width="1.5" class="spin" /><span>加载中…</span></div>
      <div v-else-if="resError" class="tp-state tp-state-error"><AlertCircle :size="20" /><span>加载失败</span></div>
      <div v-else-if="resList.length === 0" class="tp-state"><Library :size="36" :stroke-width="1" style="opacity:.3" /><span>暂无文章</span></div>
      <div v-else class="tp-table-wrap">
        <table class="tp-table">
          <thead><tr>
            <th style="width:60px">ID</th><th>标题</th>
            <th style="width:100px">分类</th><th style="width:90px">状态</th>
            <th style="width:130px">创建时间</th><th style="width:160px">操作</th>
          </tr></thead>
          <tbody>
            <tr v-for="r in resList" :key="r.id">
              <td class="td-id">#{{ r.id }}</td>
              <td><span class="td-ann-title">{{ r.title }}</span></td>
              <td><span class="td-cat">{{ r.category }}</span></td>
              <td><span :class="['td-status', r.is_published ? 'status-approved' : 'status-rejected']">{{ r.is_published ? '已发布' : '未发布' }}</span></td>
              <td class="td-time">{{ fmtDate(r.created_at) }}</td>
              <td><div class="td-actions">
                <button class="act-btn act-neutral" @click="openResForm(r)">编辑</button>
                <button :class="['act-btn', r.is_published ? 'act-reject' : 'act-approve']" @click="toggleResPublish(r)">{{ r.is_published ? '下线' : '发布' }}</button>
                <button class="act-btn act-reject" @click="doDeleteRes(r)">删除</button>
              </div></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ 问卷管理 ════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'quizzes'" class="tp-body">
      <div class="ann-toolbar">
        <span class="ann-count">共 {{ quizList.length }} 份问卷</span>
        <button class="ann-new-btn" @click="openQuizForm(null)">
          <Plus :size="15" :stroke-width="2" /> 新建问卷
        </button>
      </div>
      <div v-if="quizLoading" class="tp-state"><Loader2 :size="24" :stroke-width="1.5" class="spin" /><span>加载中…</span></div>
      <div v-else-if="quizError" class="tp-state tp-state-error"><AlertCircle :size="20" /><span>加载失败</span></div>
      <div v-else-if="quizList.length === 0" class="tp-state"><ClipboardList :size="36" :stroke-width="1" style="opacity:.3" /><span>暂无问卷</span></div>
      <div v-else class="tp-table-wrap">
        <table class="tp-table">
          <thead><tr>
            <th style="width:60px">ID</th><th>标题</th>
            <th style="width:90px">状态</th><th style="width:130px">创建时间</th><th style="width:160px">操作</th>
          </tr></thead>
          <tbody>
            <tr v-for="q in quizList" :key="q.id">
              <td class="td-id">#{{ q.id }}</td>
              <td><span class="td-ann-title">{{ q.title }}</span></td>
              <td><span :class="['td-status', q.is_published ? 'status-approved' : 'status-rejected']">{{ q.is_published ? '已发布' : '未发布' }}</span></td>
              <td class="td-time">{{ fmtDate(q.created_at) }}</td>
              <td><div class="td-actions">
                <button class="act-btn act-neutral" @click="openQuizForm(q)">编辑</button>
                <button :class="['act-btn', q.is_published ? 'act-reject' : 'act-approve']" @click="toggleQuizPublish(q)">{{ q.is_published ? '下线' : '发布' }}</button>
                <button class="act-btn act-reject" @click="doDeleteQuiz(q)">删除</button>
              </div></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ 知识库文章弹窗 ════════════════════════════════════════════════════ -->
    <Transition name="tp-modal">
      <div v-if="resFormVisible" class="tp-overlay" @click.self="resFormVisible = false">
        <div class="tp-modal tp-modal--wide">
          <div class="tp-modal-head">
            <span>{{ resFormData.id ? '编辑文章' : '新建文章' }}</span>
            <button class="tp-close-btn" @click="resFormVisible = false"><X :size="18" /></button>
          </div>
          <div class="tp-form-group">
            <label class="tp-label">标题</label>
            <input v-model="resFormData.title" class="tp-input" placeholder="文章标题" maxlength="200" />
          </div>
          <div class="tp-form-row">
            <div class="tp-form-group" style="flex:1">
              <label class="tp-label">分类</label>
              <select v-model="resFormData.category" class="tp-select">
                <option v-for="c in RES_CATEGORIES" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="tp-form-group tp-form-group--inline" style="flex-shrink:0;align-self:flex-end;padding-bottom:18px">
              <label class="tp-label" style="margin:0">立即发布</label>
              <label class="tp-toggle">
                <input type="checkbox" v-model="resFormData.is_published" />
                <span class="tp-toggle-track"></span>
              </label>
            </div>
          </div>
          <div class="tp-form-group">
            <label class="tp-label">摘要 <span class="tp-optional">（选填，显示在卡片上）</span></label>
            <textarea v-model="resFormData.summary" class="tp-textarea" rows="2" maxlength="500" placeholder="简短描述文章内容…"></textarea>
          </div>
          <div class="tp-form-group">
            <div class="tp-body-label-row">
              <label class="tp-label">正文 <span class="tp-optional">（Markdown 格式）</span></label>
              <button class="tp-preview-toggle" type="button" @click="resBodyPreview = !resBodyPreview">{{ resBodyPreview ? '编辑' : '预览' }}</button>
            </div>
            <div v-if="resBodyPreview" class="tp-body-preview" v-html="renderResPreview"></div>
            <textarea v-else v-model="resFormData.content" class="tp-textarea" rows="12" placeholder="Markdown 正文…"></textarea>
          </div>
          <p v-if="resFormError" class="tp-form-error">{{ resFormError }}</p>
          <div class="tp-modal-foot">
            <button class="tp-cancel-btn" @click="resFormVisible = false">取消</button>
            <button class="tp-save-btn" :disabled="resFormSaving || !resFormData.title.trim()" @click="saveRes">
              <Loader2 v-if="resFormSaving" :size="14" :stroke-width="1.5" class="spin" />
              <Save v-else :size="14" :stroke-width="1.5" />
              {{ resFormSaving ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══ 问卷编辑弹窗 ════════════════════════════════════════════════════ -->
    <Transition name="tp-modal">
      <div v-if="quizFormVisible" class="tp-overlay" @click.self="quizFormVisible = false">
        <div class="tp-modal tp-modal--wide">
          <div class="tp-modal-head">
            <span>{{ quizFormData.id ? '编辑问卷' : '新建问卷' }}</span>
            <button class="tp-close-btn" @click="quizFormVisible = false"><X :size="18" /></button>
          </div>

          <div class="tp-form-group">
            <label class="tp-label">问卷标题</label>
            <input v-model="quizFormData.title" class="tp-input" placeholder="例：PHQ-9 抑郁自测量表" maxlength="200" />
          </div>
          <div class="tp-form-group">
            <label class="tp-label">说明 <span class="tp-optional">（选填）</span></label>
            <textarea v-model="quizFormData.description" class="tp-textarea" rows="2" placeholder="向用户说明问卷用途…"></textarea>
          </div>

          <!-- 题目编辑器 -->
          <div class="quiz-section-label">
            题目
            <button class="quiz-add-btn" @click="addQuestion"><Plus :size="12" /> 添加题目</button>
          </div>
          <div v-for="(q, qi) in quizQuestions" :key="qi" class="quiz-q-block">
            <div class="quiz-q-header">
              <span class="quiz-q-num">第 {{ qi + 1 }} 题</span>
              <button class="quiz-rm-btn" @click="removeQuestion(qi)" v-if="quizQuestions.length > 1"><Trash2 :size="13" /></button>
            </div>
            <input v-model="q.text" class="tp-input" placeholder="题目内容" style="margin-bottom:10px" />
            <div v-for="(opt, oi) in q.options" :key="oi" class="quiz-opt-row">
              <input v-model="opt.text" class="tp-input quiz-opt-text" placeholder="选项文字" />
              <input v-model.number="opt.score" type="number" class="tp-input quiz-opt-score" placeholder="分值" min="0" />
              <button class="quiz-rm-btn" @click="removeOption(qi, oi)" v-if="q.options.length > 1"><Trash2 :size="13" /></button>
            </div>
            <button class="quiz-add-btn quiz-add-opt-btn" @click="addOption(qi)"><Plus :size="12" /> 添加选项</button>
          </div>

          <!-- 计分规则 -->
          <div class="quiz-section-label" style="margin-top:20px">
            计分区间
            <button class="quiz-add-btn" @click="addScoring"><Plus :size="12" /> 添加区间</button>
          </div>
          <div v-for="(s, si) in quizScoring" :key="si" class="quiz-score-row">
            <input v-model.number="s.min" type="number" class="tp-input quiz-score-num" placeholder="最低分" min="0" />
            <span class="quiz-score-sep">—</span>
            <input v-model.number="s.max" type="number" class="tp-input quiz-score-num" placeholder="最高分" min="0" />
            <input v-model="s.label" class="tp-input quiz-score-label" placeholder="结果标签" />
            <select v-model="s.level" class="tp-select quiz-score-level">
              <option v-for="lv in LEVEL_OPTIONS" :key="lv" :value="lv">{{ lv }}</option>
            </select>
            <input v-model="s.desc" class="tp-input quiz-score-desc" placeholder="结果描述" />
            <button class="quiz-rm-btn" @click="removeScoring(si)" v-if="quizScoring.length > 1"><Trash2 :size="13" /></button>
          </div>

          <div class="tp-form-group tp-form-group--inline" style="margin-top:16px">
            <label class="tp-label" style="margin:0">立即发布</label>
            <label class="tp-toggle">
              <input type="checkbox" v-model="quizFormData.is_published" />
              <span class="tp-toggle-track"></span>
            </label>
          </div>

          <p v-if="quizFormError" class="tp-form-error">{{ quizFormError }}</p>
          <div class="tp-modal-foot">
            <button class="tp-cancel-btn" @click="quizFormVisible = false">取消</button>
            <button class="tp-save-btn" :disabled="quizFormSaving || !quizFormData.title.trim()" @click="saveQuiz">
              <Loader2 v-if="quizFormSaving" :size="14" class="spin" />
              <Save v-else :size="14" />
              {{ quizFormSaving ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══ 公告编辑弹窗 ═══════════════════════════════════════════════════ -->
    <Transition name="tp-modal">
      <div v-if="annFormVisible" class="tp-overlay" @click.self="annFormVisible = false">
        <div class="tp-modal">
          <div class="tp-modal-head">
            <span>{{ annFormData.id ? '编辑公告' : '新建公告' }}</span>
            <button class="tp-close-btn" @click="annFormVisible = false">
              <X :size="18" />
            </button>
          </div>

          <div class="tp-form-group">
            <label class="tp-label">标题</label>
            <input v-model="annFormData.title" class="tp-input" placeholder="请输入公告标题" maxlength="200" />
          </div>

          <div class="tp-form-group">
            <label class="tp-label">分类</label>
            <select v-model="annFormData.category" class="tp-select">
              <option value="中心公告">中心公告</option>
              <option value="活动预告">活动预告</option>
              <option value="心理讲座">心理讲座</option>
            </select>
          </div>

          <div class="tp-form-group">
            <label class="tp-label">发布日期</label>
            <input v-model="annFormData.published_at" type="date" class="tp-input" />
          </div>

          <div class="tp-form-group">
            <label class="tp-label">封面图 URL <span class="tp-optional">（选填）</span></label>
            <input v-model="annFormData.cover_image" class="tp-input" placeholder="https://example.com/image.jpg" />
          </div>

          <div class="tp-form-group">
            <div class="tp-body-label-row">
              <label class="tp-label">正文 <span class="tp-optional">（Markdown 格式）</span></label>
              <button
                class="tp-preview-toggle"
                type="button"
                @click="bodyPreview = !bodyPreview"
              >{{ bodyPreview ? '编辑' : '预览' }}</button>
            </div>
            <div v-if="bodyPreview" class="tp-body-preview" v-html="renderBodyPreview"></div>
            <textarea
              v-else
              v-model="annFormData.body"
              class="tp-textarea"
              rows="10"
              placeholder="支持 Markdown：**加粗**、## 标题、- 列表、| 表格 |、![图片](url)……"
            ></textarea>
            <div class="tp-char-count">{{ annFormData.body?.length || 0 }} 字</div>
          </div>

          <div class="tp-form-group tp-form-group--inline">
            <label class="tp-label">立即发布</label>
            <label class="tp-toggle">
              <input type="checkbox" v-model="annFormData.is_published" />
              <span class="tp-toggle-track"></span>
            </label>
          </div>

          <p v-if="annFormError" class="tp-form-error">{{ annFormError }}</p>

          <div class="tp-modal-foot">
            <button class="tp-cancel-btn" @click="annFormVisible = false">取消</button>
            <button
              class="tp-save-btn"
              :disabled="annFormSaving || !annFormData.title.trim()"
              @click="saveAnn"
            >
              <Loader2 v-if="annFormSaving" :size="14" :stroke-width="1.5" class="spin" />
              <Save v-else :size="14" :stroke-width="1.5" />
              {{ annFormSaving ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ShieldCheck, TreePine, Megaphone, Loader2, AlertCircle,
  MessageSquare, Plus, X, Save, Library, ClipboardList, Trash2,
} from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'
import {
  adminGetPosts, reviewPost, adminDeletePost,
  adminGetAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement,
} from '@/api/admin'
import {
  getAdminResources, createResource, updateResource, deleteResource,
} from '@/api/resources'
import {
  getAdminQuestionnaires, createQuestionnaire, updateQuestionnaire, deleteQuestionnaire,
} from '@/api/questionnaires'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

// ── 主 Tab ────────────────────────────────────────────────────────────────────
const MAIN_TABS = [
  { key: 'treehole',      label: '树洞审核',  icon: TreePine      },
  { key: 'announcements', label: '公告管理',  icon: Megaphone     },
  { key: 'resources',     label: '知识库管理', icon: Library       },
  { key: 'quizzes',       label: '问卷管理',  icon: ClipboardList },
]
const activeTab = ref('treehole')

// ── 树洞 ──────────────────────────────────────────────────────────────────────
const TREEHOLE_FILTERS = [
  { key: '',                label: '全部'     },
  { key: 'pending',         label: '待审核'   },
  { key: 'approved',        label: '已通过'   },
  { key: 'rejected',        label: '已拒绝'   },
  { key: 'delete_requested',label: '申请删除' },
]
const STATUS_LABEL = {
  pending:          '待审核',
  approved:         '已通过',
  rejected:         '已拒绝',
  delete_requested: '申请删除',
}

const thFilter  = ref('')
const thPosts   = ref([])
const thLoading = ref(true)
const thError   = ref(false)
const thCounts  = reactive({ pending: 0, approved: 0, rejected: 0, delete_requested: 0 })

const loadPosts = async () => {
  thLoading.value = true
  thError.value   = false
  try {
    // 全量拉取一次用于计算角标，筛选视图也从全量计算
    const all = await adminGetPosts()
    thCounts.pending          = all.filter(p => p.status === 'pending').length
    thCounts.approved         = all.filter(p => p.status === 'approved').length
    thCounts.rejected         = all.filter(p => p.status === 'rejected').length
    thCounts.delete_requested = all.filter(p => p.status === 'delete_requested').length
    thPosts.value = thFilter.value ? all.filter(p => p.status === thFilter.value) : all
  } catch {
    thError.value = true
  } finally {
    thLoading.value = false
  }
}

const doReview = async (post, action) => {
  try {
    const res = await reviewPost(post.id, action)
    post.status = res.status
    // 重新刷新角标
    thCounts.pending          = thPosts.value.filter(p => p.status === 'pending').length
    thCounts.approved         = thPosts.value.filter(p => p.status === 'approved').length
    thCounts.rejected         = thPosts.value.filter(p => p.status === 'rejected').length
    thCounts.delete_requested = thPosts.value.filter(p => p.status === 'delete_requested').length
  } catch (e) {
    alert(e?.response?.data?.detail || '操作失败')
  }
}

const doDelete = async (post) => {
  if (!confirm(`确认删除帖子 #${post.id}？`)) return
  try {
    await adminDeletePost(post.id)
    thPosts.value = thPosts.value.filter(p => p.id !== post.id)
  } catch (e) {
    alert(e?.response?.data?.detail || '删除失败')
  }
}

// ── 公告 ──────────────────────────────────────────────────────────────────────
const annList    = ref([])
const annLoading = ref(true)
const annError   = ref(false)

const loadAnnouncements = async () => {
  annLoading.value = true
  annError.value   = false
  try {
    annList.value = await adminGetAnnouncements()
  } catch {
    annError.value = true
  } finally {
    annLoading.value = false
  }
}

const togglePublish = async (ann) => {
  try {
    const updated = await updateAnnouncement(ann.id, { is_published: !ann.is_published })
    Object.assign(ann, updated)
  } catch (e) {
    alert(e?.response?.data?.detail || '操作失败')
  }
}

const doDeleteAnn = async (ann) => {
  if (!confirm(`确认删除公告「${ann.title}」？`)) return
  try {
    await deleteAnnouncement(ann.id)
    annList.value = annList.value.filter(a => a.id !== ann.id)
  } catch (e) {
    alert(e?.response?.data?.detail || '删除失败')
  }
}

// ── 公告表单弹窗 ──────────────────────────────────────────────────────────────
const annFormVisible = ref(false)
const annFormSaving  = ref(false)
const annFormError   = ref('')
const bodyPreview    = ref(false)
const annFormData    = reactive({
  id: null,
  title: '',
  category: '中心公告',
  published_at: '',
  is_published: true,
  body: '',
  cover_image: '',
})

const renderBodyPreview = computed(() => md.render(annFormData.body || ''))

const openAnnForm = (ann) => {
  annFormError.value = ''
  bodyPreview.value = false
  if (ann) {
    Object.assign(annFormData, {
      id: ann.id,
      title: ann.title,
      category: ann.category,
      published_at: ann.published_at || '',
      is_published: ann.is_published,
      body: ann.body || '',
      cover_image: ann.cover_image || '',
    })
  } else {
    Object.assign(annFormData, {
      id: null,
      title: '',
      category: '中心公告',
      published_at: new Date().toISOString().slice(0, 10),
      is_published: true,
      body: '',
      cover_image: '',
    })
  }
  annFormVisible.value = true
}

const saveAnn = async () => {
  annFormError.value = ''
  annFormSaving.value = true
  const payload = {
    title:        annFormData.title.trim(),
    category:     annFormData.category,
    published_at: annFormData.published_at || null,
    is_published: annFormData.is_published,
    body:         annFormData.body || null,
    cover_image:  annFormData.cover_image || null,
  }
  try {
    if (annFormData.id) {
      const updated = await updateAnnouncement(annFormData.id, payload)
      const idx = annList.value.findIndex(a => a.id === annFormData.id)
      if (idx !== -1) annList.value[idx] = updated
    } else {
      const created = await createAnnouncement(payload)
      annList.value.unshift(created)
    }
    annFormVisible.value = false
  } catch (e) {
    annFormError.value = e?.response?.data?.detail || '保存失败，请重试'
  } finally {
    annFormSaving.value = false
  }
}

// ── 工具 ──────────────────────────────────────────────────────────────────────
const fmtDate = (isoStr) => {
  if (!isoStr) return '—'
  return new Date(isoStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

// ── 知识库 ────────────────────────────────────────────────────────────────────
const resList    = ref([])
const resLoading = ref(true)
const resError   = ref(false)

const loadResources = async () => {
  resLoading.value = true; resError.value = false
  try { resList.value = await getAdminResources() }
  catch { resError.value = true }
  finally { resLoading.value = false }
}

const resFormVisible = ref(false)
const resFormSaving  = ref(false)
const resFormError   = ref('')
const resBodyPreview = ref(false)
const resFormData    = reactive({ id: null, title: '', category: '情绪管理', summary: '', content: '', is_published: true })
const RES_CATEGORIES = ['情绪管理', '压力应对', '人际关系', '睡眠健康', '危机干预']
const renderResPreview = computed(() => md.render(resFormData.content || ''))

const openResForm = (r) => {
  resFormError.value = ''; resBodyPreview.value = false
  Object.assign(resFormData, r
    ? { id: r.id, title: r.title, category: r.category, summary: r.summary || '', content: r.content || '', is_published: r.is_published }
    : { id: null, title: '', category: '情绪管理', summary: '', content: '', is_published: true })
  resFormVisible.value = true
}

const saveRes = async () => {
  resFormError.value = ''; resFormSaving.value = true
  const payload = { title: resFormData.title.trim(), category: resFormData.category, summary: resFormData.summary || null, content: resFormData.content || null, is_published: resFormData.is_published }
  try {
    if (resFormData.id) {
      const u = await updateResource(resFormData.id, payload)
      const i = resList.value.findIndex(r => r.id === resFormData.id)
      if (i !== -1) resList.value[i] = u
    } else {
      resList.value.unshift(await createResource(payload))
    }
    resFormVisible.value = false
  } catch (e) { resFormError.value = e?.response?.data?.detail || '保存失败' }
  finally { resFormSaving.value = false }
}

const doDeleteRes = async (r) => {
  if (!confirm(`确认删除文章「${r.title}」？`)) return
  try { await deleteResource(r.id); resList.value = resList.value.filter(x => x.id !== r.id) }
  catch (e) { alert(e?.response?.data?.detail || '删除失败') }
}

const toggleResPublish = async (r) => {
  try { const u = await updateResource(r.id, { is_published: !r.is_published }); Object.assign(r, u) }
  catch (e) { alert(e?.response?.data?.detail || '操作失败') }
}

// ── 问卷管理 ──────────────────────────────────────────────────────────────────
const quizList    = ref([])
const quizLoading = ref(true)
const quizError   = ref(false)

const loadQuizzes = async () => {
  quizLoading.value = true; quizError.value = false
  try { quizList.value = await getAdminQuestionnaires() }
  catch { quizError.value = true }
  finally { quizLoading.value = false }
}

const quizFormVisible = ref(false)
const quizFormSaving  = ref(false)
const quizFormError   = ref('')
const quizFormData    = reactive({ id: null, title: '', description: '', is_published: true })
const quizQuestions   = ref([])   // [{ text, options: [{ text, score }] }]
const quizScoring     = ref([])   // [{ min, max, label, desc, level }]
const LEVEL_OPTIONS   = ['good', 'mild', 'moderate', 'severe']

const openQuizForm = (q) => {
  quizFormError.value = ''
  if (q) {
    Object.assign(quizFormData, { id: q.id, title: q.title, description: q.description || '', is_published: q.is_published })
    try { quizQuestions.value = JSON.parse(q.questions_json || '[]') } catch { quizQuestions.value = [] }
    try { quizScoring.value   = JSON.parse(q.scoring_json   || '[]') } catch { quizScoring.value   = [] }
  } else {
    Object.assign(quizFormData, { id: null, title: '', description: '', is_published: true })
    quizQuestions.value = [{ text: '', options: [{ text: '', score: 0 }, { text: '', score: 1 }] }]
    quizScoring.value   = [{ min: 0, max: 10, label: '正常', desc: '', level: 'good' }]
  }
  quizFormVisible.value = true
}

const addQuestion  = () => quizQuestions.value.push({ text: '', options: [{ text: '', score: 0 }] })
const removeQuestion = (i) => quizQuestions.value.splice(i, 1)
const addOption    = (qi) => quizQuestions.value[qi].options.push({ text: '', score: 0 })
const removeOption = (qi, oi) => quizQuestions.value[qi].options.splice(oi, 1)
const addScoring   = () => quizScoring.value.push({ min: 0, max: 0, label: '', desc: '', level: 'good' })
const removeScoring = (i) => quizScoring.value.splice(i, 1)

const saveQuiz = async () => {
  quizFormError.value = ''; quizFormSaving.value = true
  const payload = {
    title: quizFormData.title.trim(),
    description: quizFormData.description || null,
    questions_json: JSON.stringify(quizQuestions.value),
    scoring_json:   JSON.stringify(quizScoring.value),
    is_published: quizFormData.is_published,
  }
  try {
    if (quizFormData.id) {
      const u = await updateQuestionnaire(quizFormData.id, payload)
      const i = quizList.value.findIndex(q => q.id === quizFormData.id)
      if (i !== -1) quizList.value[i] = u
    } else {
      quizList.value.unshift(await createQuestionnaire(payload))
    }
    quizFormVisible.value = false
  } catch (e) { quizFormError.value = e?.response?.data?.detail || '保存失败' }
  finally { quizFormSaving.value = false }
}

const doDeleteQuiz = async (q) => {
  if (!confirm(`确认删除问卷「${q.title}」？`)) return
  try { await deleteQuestionnaire(q.id); quizList.value = quizList.value.filter(x => x.id !== q.id) }
  catch (e) { alert(e?.response?.data?.detail || '删除失败') }
}

const toggleQuizPublish = async (q) => {
  try { const u = await updateQuestionnaire(q.id, { is_published: !q.is_published }); Object.assign(q, u) }
  catch (e) { alert(e?.response?.data?.detail || '操作失败') }
}

// ── 初始化 ────────────────────────────────────────────────────────────────────
onMounted(() => {
  loadPosts()
  loadAnnouncements()
  loadResources()
  loadQuizzes()
})
</script>

<style scoped>
/* ── 基底 ────────────────────────────────────────────────────────────────── */
.tp-page {
  min-height: 100%;
  background: #edf7f2;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── 页头 ────────────────────────────────────────────────────────────────── */
.tp-header {
  background: #5f9e75;
  box-shadow: 0 2px 8px rgba(30, 80, 50, 0.2);
}
.tp-header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  gap: 40px;
  height: 56px;
}
.tp-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.tp-main-tabs {
  display: flex;
  height: 100%;
  gap: 4px;
}
.tp-main-tab {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 0 20px;
  height: 100%;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.75);
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
  box-sizing: border-box;
}
.tp-main-tab:hover { color: white; background: rgba(0,0,0,0.1); }
.tp-main-tab.active { color: white; border-bottom-color: white; font-weight: 600; }

/* ── Body ────────────────────────────────────────────────────────────────── */
.tp-body {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 32px 48px;
}

/* ── 状态筛选 ────────────────────────────────────────────────────────────── */
.tp-filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.tp-filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 20px;
  border: 1.5px solid #bdd4c8;
  background: white;
  color: #5a8a6a;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.tp-filter-btn:hover { border-color: #5f9e75; color: #5f9e75; }
.tp-filter-btn.active {
  background: #5f9e75;
  border-color: #5f9e75;
  color: white;
}
.tp-badge {
  background: #e53e3e;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 10px;
  line-height: 1.4;
}
.tp-filter-btn.active .tp-badge { background: rgba(255,255,255,0.25); }

/* ── 状态提示 ────────────────────────────────────────────────────────────── */
.tp-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 0;
  color: #6aa880;
  font-size: 14px;
}
.tp-state-error { color: #e53e3e; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 表格 ────────────────────────────────────────────────────────────────── */
.tp-table-wrap {
  background: white;
  border-radius: 8px;
  border: 1px solid #cfe8da;
  overflow: hidden;
}
.tp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}
.tp-table th {
  background: #edf7f2;
  color: #4d7a62;
  font-weight: 600;
  padding: 11px 14px;
  text-align: left;
  border-bottom: 1px solid #ddeee5;
  white-space: nowrap;
}
.tp-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #edf7f2;
  vertical-align: top;
  color: #2d4a38;
}
.tp-table tr:last-child td { border-bottom: none; }
.tp-table tr:hover td { background: #f5fbf7; }

.td-id     { color: #94a3b8; font-size: 12.5px; }
.td-name   { font-size: 12.5px; font-weight: 600; color: #5f9e75; background: #edf6f1; padding: 2px 10px; border-radius: 12px; white-space: nowrap; }
.td-content { margin: 0; line-height: 1.6; color: #3d5a48; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.td-tag { display: inline-block; font-size: 11.5px; background: #edf6f1; color: #5f9e75; padding: 2px 8px; border-radius: 10px; margin: 2px 2px 0 0; }
.td-time { font-size: 12px; color: #88b898; white-space: nowrap; }
.td-ann-title { font-weight: 500; color: #1e3a2e; }
.td-cat { font-size: 12px; background: #e8f5ec; color: #4d8764; padding: 2px 10px; border-radius: 10px; white-space: nowrap; }

.td-status { display: inline-block; font-size: 12px; padding: 3px 10px; border-radius: 10px; white-space: nowrap; font-weight: 500; }
.status-pending          { background: #fef9c3; color: #a16207; }
.status-approved         { background: #dcfce7; color: #166534; }
.status-rejected         { background: #fee2e2; color: #991b1b; }
.status-delete_requested { background: #ffedd5; color: #9a3412; }

/* ── 操作按钮 ────────────────────────────────────────────────────────────── */
.td-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.act-btn {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid;
  transition: opacity 0.15s, background 0.15s;
  white-space: nowrap;
}
.act-btn:hover { opacity: 0.82; }
.act-approve { background: #dcfce7; border-color: #86efac; color: #166534; }
.act-reject  { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }
.act-neutral { background: #edf7f2; border-color: #bdd4c8; color: #4d8764; }

/* ── 公告工具栏 ──────────────────────────────────────────────────────────── */
.ann-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.ann-count { font-size: 13px; color: #6aa880; }
.ann-new-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #5f9e75;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.ann-new-btn:hover { background: #4d8764; }

/* ── 公告弹窗 ────────────────────────────────────────────────────────────── */
.tp-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 24px;
}
.tp-modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 520px;
  padding: 28px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}
.tp-modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  font-size: 16px;
  font-weight: 600;
  color: #1e3a2e;
}
.tp-close-btn {
  background: none;
  border: none;
  color: #6aa880;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  transition: background 0.15s, color 0.15s;
}
.tp-close-btn:hover { background: #edf7f2; color: #1e3a2e; }

.tp-form-group { margin-bottom: 18px; }
.tp-form-group--inline { display: flex; align-items: center; gap: 12px; }
.tp-label {
  display: block;
  font-size: 12.5px;
  color: #4d7a62;
  margin-bottom: 6px;
  font-weight: 500;
}
.tp-form-group--inline .tp-label { margin-bottom: 0; }
.tp-input {
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid #bdd4c8;
  border-radius: 8px;
  font-size: 14px;
  color: #1e3a2e;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.tp-input:focus { outline: none; border-color: #5f9e75; }
.tp-select {
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid #bdd4c8;
  border-radius: 8px;
  font-size: 14px;
  color: #1e3a2e;
  background: white;
  cursor: pointer;
}
.tp-select:focus { outline: none; border-color: #5f9e75; }

/* Toggle switch */
.tp-toggle { position: relative; display: inline-block; width: 40px; height: 22px; cursor: pointer; }
.tp-toggle input { opacity: 0; width: 0; height: 0; }
.tp-toggle-track {
  position: absolute;
  inset: 0;
  background: #cbd5e1;
  border-radius: 11px;
  transition: background 0.2s;
}
.tp-toggle-track::before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.tp-toggle input:checked + .tp-toggle-track { background: #5f9e75; }
.tp-toggle input:checked + .tp-toggle-track::before { transform: translateX(18px); }

.tp-optional { color: #94a3b8; font-weight: 400; }
.tp-body-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.tp-preview-toggle {
  font-size: 12px;
  color: #5f9e75;
  background: none;
  border: 1px solid #bdd4c8;
  border-radius: 6px;
  padding: 3px 10px;
  cursor: pointer;
  transition: background 0.15s;
}
.tp-preview-toggle:hover { background: #edf7f2; }
.tp-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #bdd4c8;
  border-radius: 8px;
  font-size: 13.5px;
  color: #1e3a2e;
  box-sizing: border-box;
  resize: vertical;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  line-height: 1.6;
  transition: border-color 0.2s;
}
.tp-textarea:focus { outline: none; border-color: #5f9e75; }
.tp-textarea::placeholder { color: #94a3b8; font-family: -apple-system, sans-serif; }
.tp-char-count { font-size: 11.5px; color: #94a3b8; text-align: right; margin-top: 4px; }
.tp-body-preview {
  border: 1.5px solid #bdd4c8;
  border-radius: 8px;
  padding: 14px 16px;
  min-height: 160px;
  font-size: 14px;
  line-height: 1.75;
  color: #1e3a2e;
  background: #f5fbf7;
  overflow-y: auto;
  max-height: 360px;
}
.tp-body-preview :deep(h1),
.tp-body-preview :deep(h2),
.tp-body-preview :deep(h3) { font-weight: 700; margin: 1em 0 0.4em; color: #1e3a2e; }
.tp-body-preview :deep(h2) { font-size: 16px; border-bottom: 1px solid #cfe8da; padding-bottom: 4px; }
.tp-body-preview :deep(p)  { margin: 0 0 0.8em; }
.tp-body-preview :deep(ul),
.tp-body-preview :deep(ol) { padding-left: 1.4em; margin: 0 0 0.8em; }
.tp-body-preview :deep(strong) { color: #1e3a2e; }
.tp-body-preview :deep(table) { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 0.8em; }
.tp-body-preview :deep(th) { background: #edf7f2; padding: 7px 10px; border: 1px solid #cfe8da; text-align: left; }
.tp-body-preview :deep(td) { padding: 7px 10px; border: 1px solid #e0f0e8; }
.tp-body-preview :deep(blockquote) { border-left: 3px solid #5f9e75; padding: 8px 12px; background: #f0f9f4; color: #4d8764; margin: 0 0 0.8em; border-radius: 0 6px 6px 0; }
.tp-form-error { font-size: 12.5px; color: #e53e3e; margin: 0 0 12px; }

.tp-modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid #cfe8da;
  padding-top: 18px;
}
.tp-cancel-btn {
  padding: 8px 20px;
  border: 1.5px solid #bdd4c8;
  border-radius: 8px;
  background: white;
  color: #4d7a62;
  font-size: 13.5px;
  cursor: pointer;
  transition: background 0.15s;
}
.tp-cancel-btn:hover { background: #edf7f2; }
.tp-save-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 22px;
  border: none;
  border-radius: 8px;
  background: #5f9e75;
  color: white;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.tp-save-btn:hover:not(:disabled) { background: #4d8764; }
.tp-save-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* ── 宽弹窗 */
.tp-modal--wide { max-width: 760px; max-height: 85vh; overflow-y: auto; }

/* ── 表单行 */
.tp-form-row { display: flex; gap: 16px; align-items: flex-start; }

/* ── 问卷编辑器 */
.quiz-section-label {
  display: flex; align-items: center; gap: 10px;
  font-size: 13px; font-weight: 600; color: #4d7a62;
  margin-bottom: 12px;
}
.quiz-add-btn {
  display: inline-flex; align-items: center; gap: 4px;
  background: none; border: 1.5px solid #bdd4c8; color: #5f9e75;
  padding: 4px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
  transition: background 0.15s;
}
.quiz-add-btn:hover { background: #edf7f2; }
.quiz-add-opt-btn { margin-top: 8px; }
.quiz-q-block { background: #f5fbf7; border: 1px solid #cfe8da; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.quiz-q-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.quiz-q-num { font-size: 12.5px; font-weight: 600; color: #4d8764; }
.quiz-rm-btn { background: none; border: none; color: #e53e3e; cursor: pointer; padding: 2px; display: flex; opacity: 0.7; }
.quiz-rm-btn:hover { opacity: 1; }
.quiz-opt-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.quiz-opt-text { flex: 1; }
.quiz-opt-score { width: 70px; }
.quiz-score-row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.quiz-score-num   { width: 80px; }
.quiz-score-sep   { color: #94a3b8; flex-shrink: 0; }
.quiz-score-label { width: 90px; }
.quiz-score-level { width: 100px; }
.quiz-score-desc  { flex: 1; min-width: 120px; }

/* 弹窗过渡 */
.tp-modal-enter-active,
.tp-modal-leave-active { transition: opacity 0.2s ease; }
.tp-modal-enter-active .tp-modal,
.tp-modal-leave-active .tp-modal { transition: transform 0.2s ease; }
.tp-modal-enter-from,
.tp-modal-leave-to { opacity: 0; }
.tp-modal-enter-from .tp-modal,
.tp-modal-leave-to  .tp-modal { transform: translateY(12px); }
</style>
