import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
})

request.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  // 刷新 token 请求不附带 access_token，避免后端先校验 access_token
  if (authStore.accessToken && !config.url?.includes('/auth/refresh/')) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})

let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

request.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data.code !== undefined && data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // refresh 接口本身 401 说明 refresh_token 也过期了，直接登出
    if (error.response?.status === 401 && originalRequest.url?.includes('/auth/refresh/')) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push(`/login?redirect=${encodeURIComponent(router.currentRoute.value.fullPath)}`)
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const authStore = useAuthStore()

      if (!isRefreshing) {
        isRefreshing = true
        try {
          const newToken = await authStore.refreshToken()
          isRefreshing = false
          pendingRequests.forEach((cb) => cb(newToken))
          pendingRequests = []
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return request(originalRequest)
        } catch {
          isRefreshing = false
          pendingRequests = []
          authStore.logout()
          router.push(`/login?redirect=${encodeURIComponent(router.currentRoute.value.fullPath)}`)
          return Promise.reject(error)
        }
      } else {
        return new Promise((resolve) => {
          pendingRequests.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(request(originalRequest))
          })
        })
      }
    }
    const message = error.response?.data?.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
