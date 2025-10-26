import { useEffect, useState } from 'react'
import { Route, Routes, useNavigate, Navigate, useLocation } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Clientes from './pages/Clientes.jsx'
import Ventas from './pages/ventas/Ventas.jsx'
import Reportes from './pages/Reportes.jsx'
import Bitacora from './pages/Bitacora.jsx'
import Perfil from './pages/Perfil.jsx'
import Registro from './pages/Registro.jsx'
import Recuperar from './pages/Recuperar.jsx'
import Configuracion from './pages/Configuracion.jsx'

import { AuthProvider, useAuth } from './hooks/useAuth.jsx'
import Sidebar from './components/Sidebar.jsx'
import GestionCatalogo from './pages/catalogo/GestionCatalogo.jsx'
import DetalleVenta from './pages/ventas/DetalleVenta.jsx' // Ya estaba bien, pero lo confirmo
import GestionUsuarios from './pages/usuarios/Gestion.jsx'
import useTheme from './hooks/useTheme.js'

export default function App(){
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login/>}/>
        <Route path="/registro" element={<Registro/>}/>
        <Route path="/recuperar" element={<Recuperar/>}/>
        <Route path="/*" element={<RequireAuth><Shell/></RequireAuth>}/>
      </Routes>
    </AuthProvider>
  )
}

function Shell(){
  const { logout, toast, sideOpen, setSideOpen } = useAuth()
  const { theme, toggle } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  // Abrir/cerrar: móvil → overlay; desktop → colapsar
  const onHamburger = () => {
    if (window.innerWidth <= 900) setSideOpen(v => !v)
    else setCollapsed(c => !c)
  }

  // Cerrar el menú móvil cuando navegas a otra ruta
  useEffect(()=>{ if (sideOpen) setSideOpen(false) }, [location.pathname])

  // Cerrar con tecla ESC en móvil
  useEffect(()=>{
    const onKey = (e)=>{ if (e.key === 'Escape') setSideOpen(false) }
    window.addEventListener('keydown', onKey)
    return ()=> window.removeEventListener('keydown', onKey)
  }, [setSideOpen])

  // Bloquear scroll del body cuando el menú móvil está abierto
  useEffect(()=>{
    const cls = 'menu-open'
    if (sideOpen) document.body.classList.add(cls)
    else document.body.classList.remove(cls)
    return ()=> document.body.classList.remove(cls)
  }, [sideOpen])

  // Añadir/quitar clase al body cuando el sidebar se colapsa en desktop
  useEffect(()=>{
    const cls = 'sidebar-collapsed'
    if (collapsed) document.body.classList.add(cls)
    else document.body.classList.remove(cls)
    return ()=> document.body.classList.remove(cls)
  }, [collapsed])


  // Si redimensionas cruzando el umbral, aseguramos estado coherente
  useEffect(()=>{
    const onResize = ()=>{
      if (window.innerWidth > 900) setSideOpen(false)  // quita overlay si es desktop
    }
    window.addEventListener('resize', onResize)
    return ()=> window.removeEventListener('resize', onResize)
  }, [setSideOpen])

  return (
    <div className={`app ${sideOpen ? 'show-side' : ''} ${collapsed ? 'collapsed' : ''}`}>
      {/* Overlay clickeable en móvil */}
      <div
        className="mobile-backdrop"
        onClick={()=> setSideOpen(false)}
        aria-hidden="true"
      />
      <Sidebar collapsed={collapsed}/>

      <div>
        <div className="header">
          <button className="hamb" onClick={onHamburger} aria-label="Abrir menú">☰</button>
          <div className="spacer"></div>
          <button onClick={toggle}>{theme==='dark' ? 'Modo claro' : 'Modo oscuro'}</button>
          <button onClick={()=>{ logout(); navigate('/login') }}>Salir</button>
        </div>

        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard/>}/>
            <Route path="/productos" element={<GestionCatalogo/>}/>
            <Route path="/clientes" element={<Clientes/>}/>
            <Route path="/ventas" element={<Ventas/>}/>
            <Route path="/ventas/editar/:id" element={<Ventas isEditing />} />
            <Route path="/ventas/:id" element={<DetalleVenta/>}/>
            <Route path="/reportes" element={<Reportes/>}/>
            <Route path="/bitacora" element={<Bitacora/>}/>
            <Route path="/perfil" element={<Perfil/>}/>
            <Route path="/configuracion" element={<Configuracion/>}/>
            <Route path="/usuarios" element={<GestionUsuarios/>}/>
          </Routes>
        </div>
      </div>

      {toast && <div className="toast">{toast}</div>}
    </div>
  )
}

function RequireAuth({ children }){
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <div className="container">Cargando...</div>
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  return <>{children}</>
}
