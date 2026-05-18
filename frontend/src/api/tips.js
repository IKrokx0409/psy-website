import http from './http'

export const getRandomTip  = ()           => http.get('/api/tips/random').then(r => r.data)
export const listTips      = ()           => http.get('/api/tips/').then(r => r.data)
export const createTip     = (body)       => http.post('/api/tips/', body).then(r => r.data)
export const updateTip     = (id, body)   => http.patch(`/api/tips/${id}`, body).then(r => r.data)
export const deleteTip     = (id)         => http.delete(`/api/tips/${id}`)
