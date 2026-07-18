import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

interface User {
  id: number
  username: string
  is_superuser: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshTokenValue = ref(localStorage.getItem('refresh_token') || '')
  const user = ref<User | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  )

  const isLoggedIn = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.is_superuser ?? false)

  async function login(username: string, password: string) {
    const res = await request.post('/auth/login/', { username, password })
    const data = res.data.data
    accessToken.value = data.access
    refreshTokenValue.value = data.refresh
    user.value = data.user
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
    return data
  }

  async function refreshToken() {
    const res = await request.post('/auth/refresh/', { refresh: refreshTokenValue.value })
    const newAccess = res.data.data.access
    accessToken.value = newAccess
    localStorage.setItem('access_token', newAccess)
    return newAccess
  }

  function logout() {
    accessToken.value = ''
    refreshTokenValue.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return { accessToken, refreshTokenValue, user, isLoggedIn, isAdmin, login, refreshToken, logout }
})
