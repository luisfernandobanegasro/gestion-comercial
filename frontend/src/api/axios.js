// api/axios.js
import axios from 'axios'
import { PATHS } from './paths'

export const API_BASE = import.meta.env.VITE_API_URL 
  || 'http://smart-sales.eba-n3j3inxe.us-east-1.elasticbeanstalk.com'

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// 2) Auth header automático en cada request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

let refreshing = false

// 3) Refresh token centralizado (y sin romper si el 401 viene del refresh)
api.interceptors.response.use(
  r => r,
  async (error) => {
    const original = error.config

    if (error.response?.status === 401 &&
        !original?._retry &&
        // evita bucles si justo el 401 vino del refresh
        !(original?.url || '').includes(PATHS.auth.refresh)) {

      if (refreshing) return Promise.reject(error)
      original._retry = true
      refreshing = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) throw new Error('No refresh token')

        // Usa la MISMA instancia para respetar baseURL
        const { data } = await api.post(PATHS.auth.refresh, { refresh })
        localStorage.setItem('access_token', data.access)

        refreshing = false
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${data.access}`

        return api(original) // reintenta el request original
      } catch (e) {
        refreshing = false
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    }
    return Promise.reject(error)
  }
)

export default api
