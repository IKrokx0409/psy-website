export function useUserId() {
  let id = localStorage.getItem('diary_user_id')
  if (!id) {
    id = 'uid_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7)
    localStorage.setItem('diary_user_id', id)
  }
  return id
}
