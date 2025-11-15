// api/axios.js
import axios from 'axios'
import { PATHS } from './paths'

// ==============================
// BASE URL DEL BACKEND
// ==============================
// - Toma el valor del .env del frontend (VITE_API_URL)
// - Si no existe, usa tu Elastic Beanstalk por defecto (HTTP)
// ==============================
export const API_BASE =
  import.meta.env.VITE_API_URL ||
  'http://smart-sales.eba-n3j3inxe.us-east-1.elasticbeanstalk.com'

// Log opcional para verificar en producción qué URL carga
console.log("🌐 BACKEND BASE URL:", API_BASE)

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// ==============================
// TOKEN EN CADA REQUEST
// ==============================
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// ==============================
// MANEJO CENTRALIZADO DEL REFRESH TOKEN
// ==============================
let refreshing = false

api.interceptors.response.use(
  r => r,
  async (error) => {
    const original = error.config

    // Error 401 → intento refrescar token
    if (
      error.response?.status === 401 &&
      !original?._retry &&
      !(original?.url || '').includes(PATHS.auth.refresh)
    ) {
      if (refreshing) return Promise.reject(error)

      original._retry = true
      refreshing = true

      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) throw new Error('No refresh token')

        const { data } = await api.post(PATHS.auth.refresh, { refresh })

        localStorage.setItem('access_token', data.access)
        refreshing = false

        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${data.access}`

        return api(original)
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
