// hooks/useAuth.jsx
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react'
import { useNavigate } from 'react-router-dom'
import api, { API_BASE } from '../api/axios.js'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState(null)
  const [sideOpen, setSideOpen] = useState(false)
  const [permissions, setPermissions] = useState(new Set())
  const [hasFetchedMe, setHasFetchedMe] = useState(false)

  const navigate = useNavigate()

  const showToast = useCallback((msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }, [])

  /**
   * Carga /cuentas/yo/ SOLO si hay access_token.
   * Maneja bien 401 y limpia permisos si falla.
   */
  const fetchMe = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      // No hay sesión → no pegues al backend innecesariamente
      setUser(null)
      setPermissions(new Set())
      setLoading(false)
      return
    }

    try {
      const { data } = await api.get('/cuentas/yo/')
      setUser(data)
      setPermissions(new Set(data.permisos || []))
    } catch (err) {
      console.debug('fetchMe failed against', API_BASE, err?.message)
      setUser(null)
      setPermissions(new Set())

      // Si el backend dice 401, limpiamos tokens para evitar loops
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  // Se llama UNA sola vez al montar el provider
  useEffect(() => {
    if (hasFetchedMe) return
    setHasFetchedMe(true)
    fetchMe()
  }, [fetchMe, hasFetchedMe])

  const login = useCallback(
    async (username, password) => {
      setLoading(true)
      try {
        const { data } = await api.post('/cuentas/token/', {
          username,
          password,
        })

        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)

        // Para futuras requests (aunque ya tenemos el interceptor)
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`

        await fetchMe()
        showToast('¡Bienvenido!')
        navigate('/')
      } catch (err) {
        setLoading(false)
        // Deja que el componente de Login maneje el error si quiere
        throw err
      }
    },
    [fetchMe, navigate, showToast]
  )

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    setPermissions(new Set())
    showToast('Sesión cerrada')
  }, [showToast])

  const userHasPermission = useCallback(
    (perm) => permissions.has(perm),
    [permissions]
  )

  return (
    <Ctx.Provider
      value={{
        user,
        loading,
        login,
        logout,
        toast,
        sideOpen,
        setSideOpen,
        userHasPermission,
        fetchMe,
      }}
    >
      {children}
    </Ctx.Provider>
  )
}

export const useAuth = () => useContext(Ctx)
