// hooks/useAuth.jsx
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { API_BASE } from '../api/axios.js'

const Ctx = createContext(null)

export function AuthProvider({children}){
  const [user,setUser] = useState(null)
  const [loading,setLoading] = useState(true)
  const [toast, setToast] = useState(null)
  const [sideOpen, setSideOpen] = useState(false)
  const [permissions, setPermissions] = useState(new Set());
  const navigate = useNavigate()

  const showToast = (msg)=>{ setToast(msg); setTimeout(()=>setToast(null), 3000) }

  const fetchMe = async()=>{
    try{
      // SIEMPRE usar la instancia 'api' (respeta baseURL + headers)
      const { data } = await api.get('/cuentas/yo/')
      setUser(data)
      setPermissions(new Set(data.permisos || []))
    }catch(err){
      console.debug('fetchMe failed against', API_BASE, err?.message)
      setUser(null)
      setPermissions(new Set())
    }finally{
      setLoading(false)
    }
  }
  useEffect(()=>{ fetchMe() }, [])

  const login = async (username,password)=>{
    const { data } = await api.post('/cuentas/token/', { username, password })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    // seteo inmediato para que próximas llamadas ya vayan con token
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
    await fetchMe()
    showToast('¡Bienvenido!')
    navigate('/')
  }

  const logout = useCallback(()=>{
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    setPermissions(new Set())
    showToast('Sesión cerrada')
  }, [])

  const userHasPermission = useCallback((perm) => permissions.has(perm), [permissions])

  return (
    <Ctx.Provider value={{user, loading, login, logout, toast, sideOpen, setSideOpen, userHasPermission, fetchMe}}>
      {children}
    </Ctx.Provider>
  )
}
export const useAuth = ()=>useContext(Ctx)
