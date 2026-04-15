import { ref, computed } from 'vue'

// 模块级单例：所有组件共享同一个 role ref
const role = ref(localStorage.getItem('mock_role') || null)

export function useAuth() {
  const setRole = (r) => {
    role.value = r
    localStorage.setItem('mock_role', r)
  }

  const clearRole = () => {
    role.value = null
    localStorage.removeItem('mock_role')
  }

  const isTeacher = computed(() => role.value === 'teacher')
  const isStudent = computed(() => role.value === 'student')
  const isLoggedIn = computed(() => !!role.value)

  return { role, setRole, clearRole, isTeacher, isStudent, isLoggedIn }
}
