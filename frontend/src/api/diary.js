import http from './http'

export const getDiaries = (userId, start, end) => {
  const params = { user_id: userId }
  if (start) params.start = start
  if (end) params.end = end
  return http.get('/api/diary', { params }).then(r => r.data)
}

export const saveDiary = (data) =>
  http.post('/api/diary', data).then(r => r.data)

export const updateDiary = (id, data) =>
  http.patch(`/api/diary/${id}`, data).then(r => r.data)

export const deleteDiary = (id) =>
  http.delete(`/api/diary/${id}`).then(r => r.data)
