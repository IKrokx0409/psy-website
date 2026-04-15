import axios from 'axios'

const http = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
})

http.interceptors.request.use((config) => {
  const role = localStorage.getItem('mock_role')
  if (role) config.headers['X-Role'] = role
  return config
})

export default http
