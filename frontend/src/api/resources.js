import http from './http'

export const getResources = (category) => {
  const params = category ? { category } : {}
  return http.get('/api/resources', { params }).then(r => r.data)
}

export const getAdminResources = () =>
  http.get('/api/resources/admin').then(r => r.data)

export const getResource = (id) =>
  http.get(`/api/resources/${id}`).then(r => r.data)

export const createResource = (data) =>
  http.post('/api/resources', data).then(r => r.data)

export const updateResource = (id, data) =>
  http.patch(`/api/resources/${id}`, data).then(r => r.data)

export const deleteResource = (id) =>
  http.delete(`/api/resources/${id}`).then(r => r.data)
