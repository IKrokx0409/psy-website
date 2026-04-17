import http from './http'

/**
 * 获取公告列表（不含正文）
 * @param {string} [category] - 可选分类：中心公告 / 活动预告 / 心理讲座
 */
export const getAnnouncements = (category) =>
  http.get('/api/announcements', { params: category ? { category } : {} })
    .then(r => r.data)

/**
 * 获取单条公告详情（含 Markdown 正文）
 * @param {number} id
 */
export const getAnnouncement = (id) =>
  http.get(`/api/announcements/${id}`).then(r => r.data)
