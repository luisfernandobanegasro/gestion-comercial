import { useState } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'

export default function Login(){
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState()
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  const onSubmit = async (e)=>{
    e.preventDefault()
    setError(undefined)
    setBusy(true)

    try {
      // opcional: evitar espacios accidentales
      const u = username.trim()
      const p = password.trim()

      await login(u, p)
      navigate(from, { replace:true })
    } catch (err) {
      console.error('Error al iniciar sesión:', err)

      let mensaje = 'Ocurrió un error al iniciar sesión.'

      // Error de red / timeout (no se llega al backend)
      if (err.code === 'ERR_NETWORK') {
        mensaje = 'No se pudo conectar con el servidor. Verifica tu conexión o inténtalo de nuevo en unos minutos.'
      }
      // Errores con respuesta HTTP
      else if (err.response) {
        const status = err.response.status
        const detail = err.response.data?.detail

        if (status === 400 || status === 401) {
          mensaje = detail || 'Usuario o contraseña inválidos.'
        } else if (status >= 500) {
          mensaje = 'El servidor está teniendo problemas. Intenta nuevamente más tarde.'
        } else {
          mensaje = detail || mensaje
        }
      }

      setError(mensaje)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{
      minHeight:'100vh',
      display:'grid',
      placeItems:'center',
      background:'radial-gradient(1200px 600px at 20% -10%, var(--primary)44, transparent), var(--bg)'
    }}>
      <div className="card" style={{
        width:'min(480px, 92vw)',
        padding:24,
        borderRadius:16,
        boxShadow:'0 20px 80px rgba(0,0,0,.2)'
      }}>
        <div style={{display:'flex', alignItems:'center', gap:10, marginBottom:10}}>
          <div style={{width:10, height:10, borderRadius:9999, background:'var(--primary)'}}/>
          <div style={{fontWeight:800, fontSize:18}}>SmartSales365</div>
        </div>
        <h2 style={{marginTop:0}}>Iniciar sesión</h2>
        <p style={{marginTop:-8, color:'var(--muted)'}}>Accede con tus credenciales</p>

        <form onSubmit={onSubmit} className="grid" style={{marginTop:12}}>
          <input
            placeholder="Usuario"
            value={username}
            onChange={e=>setUsername(e.target.value)}
            required
          />

          <div className="input-group">
            <input
              type={showPass ? 'text' : 'password'}
              placeholder="Contraseña"
              value={password}
              onChange={e=>setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              className="icon-btn"
              aria-label={showPass ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              onClick={()=>setShowPass(v=>!v)}
            >
              {showPass ? <EyeOff className="icon-16"/> : <Eye className="icon-16"/>}
            </button>
          </div>

          {error && (
            <div style={{color:'#fca5a5', fontSize:14}}>
              {error}
            </div>
          )}

          <button
            className="primary"
            disabled={busy}
            style={{display:'flex', alignItems:'center', gap:8, justifyContent:'center'}}
          >
            {busy && (
              <span
                className="spinner"
                style={{
                  width:14,
                  height:14,
                  border:'2px solid var(--primary-ink)',
                  borderTopColor:'transparent',
                  borderRadius:'50%',
                  animation:'spin .8s linear infinite'
                }}
              />
            )}
            {busy ? 'Ingresando…' : 'Ingresar'}
          </button>

          <div className="auth-links">
            <Link to="/registro">¿No tienes cuenta? Regístrate</Link>
            <Link to="/recuperar">¿Olvidaste tu contraseña?</Link>
          </div>
        </form>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}
