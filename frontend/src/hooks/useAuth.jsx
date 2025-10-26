
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios.js'
const Ctx = createContext(null)

export function AuthProvider({children}){
  const [user,setUser] = useState(null)
  const [loading,setLoading] = useState(true)
  const [toast, setToast] = useState(null)
  const [sideOpen, setSideOpen] = useState(false)
  // 1. Nuevo estado para guardar los permisos del usuario. Usamos un Set para búsquedas rápidas.
  const [permissions, setPermissions] = useState(new Set());
  const navigate = useNavigate()

  const showToast = (msg)=>{ setToast(msg); setTimeout(()=>setToast(null), 3000) }

  const fetchMe = async()=>{
    try{
      const { data } = await api.get('/cuentas/yo/');
      setUser(data)
      // 2. Cuando obtenemos los datos del usuario, también guardamos sus permisos.
      setPermissions(new Set(data.permisos || []));
    }
    catch{
      setUser(null)
      setPermissions(new Set()); // Si falla, limpiamos los permisos.
    }
    finally{ setLoading(false) }
  }
  useEffect(()=>{ fetchMe() }, [])

  const login = async (username,password)=>{
    const { data } = await api.post('/cuentas/token/', { username, password })
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
    await fetchMe(); // Carga el usuario y sus permisos
    showToast('¡Bienvenido!')
    navigate('/')
  }
  const logout = useCallback(()=>{
    localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null); setPermissions(new Set()); // Limpiamos usuario y permisos.
    showToast('Sesión cerrada');
  }, []);

  // 3. La nueva función que verifica si el usuario tiene un permiso.
  const userHasPermission = useCallback((perm) => permissions.has(perm), [permissions]);

  // 4. Añadimos `userHasPermission` al valor del Provider para que `Can.jsx` pueda usarlo.
  return <Ctx.Provider value={{user, loading, login, logout, toast, sideOpen, setSideOpen, userHasPermission, fetchMe}}>{children}</Ctx.Provider>
}
export const useAuth = ()=>useContext(Ctx)
