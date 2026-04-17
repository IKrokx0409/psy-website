import http from './http'

export const getQuestionnaires = () =>
  http.get('/api/questionnaires').then(r => r.data)

export const getAdminQuestionnaires = () =>
  http.get('/api/questionnaires/admin').then(r => r.data)

export const getQuestionnaire = (id) =>
  http.get(`/api/questionnaires/${id}`).then(r => r.data)

export const createQuestionnaire = (data) =>
  http.post('/api/questionnaires', data).then(r => r.data)

export const updateQuestionnaire = (id, data) =>
  http.patch(`/api/questionnaires/${id}`, data).then(r => r.data)

export const deleteQuestionnaire = (id) =>
  http.delete(`/api/questionnaires/${id}`).then(r => r.data)
