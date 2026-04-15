import http from './http'

/**
 * 获取公告列表
 * @param {string} [category] - 可选分类：中心公告 / 活动预告 / 心理讲座
 */
export const getAnnouncements = (category) =>
  http.get('/api/announcements', { params: category ? { category } : {} })
    .then(r => r.data)
