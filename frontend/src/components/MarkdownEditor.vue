<template>
  <div class="mde-wrap">
    <!-- 工具栏 -->
    <div class="mde-toolbar">
      <button v-for="btn in TOOLBAR" :key="btn.label" type="button"
        class="mde-btn" :title="btn.title" @click="apply(btn)">
        {{ btn.label }}
      </button>
      <div class="mde-sep"></div>
      <button type="button" class="mde-btn mde-preview-btn" @click="preview = !preview">
        {{ preview ? '编辑' : '预览' }}
      </button>
    </div>

    <!-- 预览区 -->
    <div v-if="preview" class="mde-preview tp-body-preview" v-html="rendered"></div>

    <!-- 编辑区 -->
    <textarea
      v-else
      ref="ta"
      class="tp-textarea mde-textarea"
      :rows="rows"
      :placeholder="placeholder"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      @keydown="onKeydown"
    ></textarea>

    <div v-if="showCount" class="tp-char-count">{{ (modelValue || '').length }} 字</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps({
  modelValue: { type: String, default: '' },
  rows:        { type: Number, default: 10 },
  placeholder: { type: String, default: 'Markdown 正文…' },
  showCount:   { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])

const ta      = ref(null)
const preview = ref(false)
const md      = new MarkdownIt({ html: false, linkify: true, typographer: true, breaks: true })
const rendered = computed(() => md.render(props.modelValue || ''))

const TOOLBAR = [
  { label: 'H2',    title: '二级标题',   prefix: '## ',      suffix: '',     block: true  },
  { label: 'H3',    title: '三级标题',   prefix: '### ',     suffix: '',     block: true  },
  { label: 'B',     title: '加粗',       prefix: '**',       suffix: '**',   block: false },
  { label: 'I',     title: '斜体',       prefix: '*',        suffix: '*',    block: false },
  { label: '🔗',   title: '超链接',     prefix: '[',        suffix: '](url)',block: false },
  { label: '`',     title: '行内代码',   prefix: '`',        suffix: '`',    block: false },
  { label: '```',   title: '代码块',     prefix: '```\n',    suffix: '\n```',block: false },
  { label: '—',    title: '分割线',     prefix: '\n---\n',  suffix: '',     block: true  },
  { label: '≡',    title: '无序列表',   prefix: '- ',       suffix: '',     block: true  },
  { label: '1.',    title: '有序列表',   prefix: '1. ',      suffix: '',     block: true  },
  { label: '"',     title: '引用',       prefix: '> ',       suffix: '',     block: true  },
]

function apply(btn) {
  const el = ta.value
  if (!el) return

  const start = el.selectionStart
  const end   = el.selectionEnd
  const val   = props.modelValue || ''
  const sel   = val.slice(start, end)

  let insert, cursorOffset

  if (btn.block && start === end) {
    // 无选中：行首插入前缀
    const lineStart = val.lastIndexOf('\n', start - 1) + 1
    insert = val.slice(0, lineStart) + btn.prefix + val.slice(lineStart)
    cursorOffset = lineStart + btn.prefix.length + (start - lineStart)
  } else {
    const replacement = btn.prefix + (sel || btn.title) + btn.suffix
    insert = val.slice(0, start) + replacement + val.slice(end)
    cursorOffset = start + btn.prefix.length + (sel || btn.title).length
  }

  // 触发 v-model 更新
  el.value = insert
  el.dispatchEvent(new Event('input'))

  // 恢复光标
  el.focus()
  requestAnimationFrame(() => {
    el.setSelectionRange(cursorOffset, cursorOffset)
  })
}

function onKeydown(e) {
  // Tab 插入两个空格而非跳出
  if (e.key === 'Tab') {
    e.preventDefault()
    apply({ prefix: '  ', suffix: '', block: false, title: '' })
  }
}
</script>

<style scoped>
.mde-wrap { display: flex; flex-direction: column; gap: 0; }

.mde-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 5px 8px;
  background: #f8faf9;
  border: 1px solid #d0d9d4;
  border-bottom: none;
  border-radius: var(--r-sm) var(--r-sm) 0 0;
  flex-wrap: wrap;
}

.mde-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 26px;
  padding: 0 6px;
  font-size: 12px;
  font-weight: 600;
  font-family: monospace;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  color: #3d6b52;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
  white-space: nowrap;
}
.mde-btn:hover { background: #e8f4ed; border-color: #b5d4c2; }
.mde-btn:active { background: #d2eadb; }

.mde-sep { width: 1px; height: 18px; background: #d0d9d4; margin: 0 4px; }

.mde-preview-btn {
  margin-left: auto;
  font-family: var(--f-sans, sans-serif);
  font-size: 12px;
  font-weight: 500;
  color: #5f9e75;
}

.mde-textarea {
  border-top-left-radius: 0 !important;
  border-top-right-radius: 0 !important;
  resize: vertical;
}

.mde-preview {
  border-top-left-radius: 0 !important;
  border-top-right-radius: 0 !important;
}
</style>
