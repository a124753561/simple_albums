import axios from 'axios'
import { showToast } from 'vant'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
})

request.interceptors.response.use(
  (res) => res,
  (error) => {
    showToast(error.response?.data?.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
