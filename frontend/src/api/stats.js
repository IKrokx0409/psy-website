import http from './http'

export const fetchMonthlyStats = ({ year, month, threshold = 4, classId, teacherId }) => {
  const params = { year, month, threshold }
  if (classId)   params.class_id   = classId
  if (teacherId) params.teacher_id = teacherId
  return http.get('/api/stats/monthly', { params }).then(r => r.data)
}
