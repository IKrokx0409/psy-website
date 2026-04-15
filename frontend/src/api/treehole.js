import http from './http'

const TOKENS_KEY = 'treehole_tokens'

const getMyTokens = () => JSON.parse(localStorage.getItem(TOKENS_KEY) || '{}')

const saveToken = (postId, token) => {
  const tokens = getMyTokens()
  tokens[String(postId)] = token
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens))
}

/** 查询本地是否持有某帖子的 author_token */
export const getMyToken = (postId) => getMyTokens()[String(postId)] || null

/** 获取所有已审核帖子 */
export const getPosts = () => http.get('/api/treehole').then(r => r.data)

/** 发布新帖，成功后自动将 author_token 存入 localStorage */
export const createPost = async (data) => {
  const res = await http.post('/api/treehole', data)
  saveToken(res.data.id, res.data.author_token)
  return res.data
}

/** 申请删除自己的帖子 */
export const requestDelete = (postId) => {
  const token = getMyToken(postId)
  if (!token) throw new Error('无删除权限')
  return http.post(`/api/treehole/${postId}/delete-request`, { author_token: token })
    .then(r => r.data)
}
