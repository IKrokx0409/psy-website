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
  MessageSquare, Plus, X, Save,
} from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'
import {
  adminGetPosts, reviewPost, adminDeletePost,
  adminGetAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement,
} from '@/api/admin'

const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

// ── 主 Tab ────────────────────────────────────────────────────────────────────
const MAIN_TABS = [
  { key: 'treehole',      label: '树洞审核',  icon: TreePine   },
  { key: 'announcements', label: '公告管理',  icon: Megaphone  },
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

onMounted(() => {
  loadPosts()
  loadAnnouncements()
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
