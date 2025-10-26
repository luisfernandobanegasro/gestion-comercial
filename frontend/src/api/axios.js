import axios from 'axios'
import { PATHS } from './paths'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(cfg=>{
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

let refreshing = false

api.interceptors.response.use(r=>r, async (error)=>{
  const original = error.config
  // Evitar bucle de refresh si el error 401 viene de la ruta de refresh
  if (error.response?.status === 401 && !original._retry && original.url !== PATHS.auth.refresh) {
    if (refreshing) return Promise.reject(error)
    original._retry = true
    refreshing = true
    try{
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) throw new Error('No refresh token')
      const { data } = await axios.post(`${api.defaults.baseURL}${PATHS.auth.refresh}`, { refresh })
      localStorage.setItem('access_token', data.access)
      refreshing = false
      original.headers.Authorization = `Bearer ${data.access}`
      return api(original)
    }catch(e){
      refreshing = false
      localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token')
    }
  }
  return Promise.reject(error)
})

export default api
