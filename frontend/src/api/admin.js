import http from './http'

// ── 树洞管理 ──────────────────────────────────────────────────────────────────

/** 获取所有帖子，可按 status 过滤 */
export const adminGetPosts = (status) =>
  http.get('/api/admin/treehole', { params: status ? { status } : {} }).then(r => r.data)

/** 审核帖子：action = "approve" | "reject" */
export const reviewPost = (postId, action) =>
  http.patch(`/api/admin/treehole/${postId}/review`, { action }).then(r => r.data)

/** 删除帖子 */
export const adminDeletePost = (postId) =>
  http.delete(`/api/admin/treehole/${postId}`).then(r => r.data)

// ── 公告管理 ──────────────────────────────────────────────────────────────────

/** 获取全部公告（含未发布） */
export const adminGetAnnouncements = () =>
  http.get('/api/admin/announcements').then(r => r.data)

/** 新建公告 */
export const createAnnouncement = (data) =>
  http.post('/api/admin/announcements', data).then(r => r.data)

/** 编辑公告 */
export const updateAnnouncement = (id, data) =>
  http.patch(`/api/admin/announcements/${id}`, data).then(r => r.data)

/** 删除公告 */
export const deleteAnnouncement = (id) =>
  http.delete(`/api/admin/announcements/${id}`).then(r => r.data)
