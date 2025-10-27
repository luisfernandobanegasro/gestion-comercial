import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import api from '../api/axios'
import { PATHS } from '../api/paths'
import { Eye, EyeOff } from 'lucide-react'

export default function Recuperar(){
  const [params] = useSearchParams()
  const token = params.get('token')
  const uid = params.get('uid')
  return token && uid ? <ResetConfirm uid={uid} token={token}/> : <ResetRequest/>
}

function ResetRequest(){
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState()

  const submit = async (e)=>{
    e.preventDefault()
    setBusy(true); setError(undefined)
    try{
      await api.post(PATHS.auth.passwordResetRequest, { email })
      setSent(true)
    }catch(err){
      setError(err?.response?.data?.detail || 'No se pudo enviar el correo')
    }finally{ setBusy(false) }
  }

  return (
    <div style={{minHeight:'100vh', display:'grid', placeItems:'center', background:'var(--bg)'}}>
      <div className="card" style={{width:'min(520px, 94vw)'}}>
        <h2 style={{marginTop:0}}>Recuperar contraseña</h2>
        <p style={{marginTop:-6, color:'var(--muted)'}}>Ingresa tu email y te enviaremos instrucciones.</p>
        <form className="grid" onSubmit={submit}>
          <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required/>
          {error && <div style={{color:'#fca5a5'}}>{error}</div>}
          {sent && <div style={{color:'#22c55e'}}>Si el email existe, se enviaron instrucciones.</div>}
          <button className="primary" disabled={busy}>{busy? 'Enviando…':'Enviar instrucciones'}</button>
          <div className="auth-links"><Link to="/login">Volver al login</Link></div>
        </form>
      </div>
    </div>
  )
}

function ResetConfirm({ uid, token }){
  const [pass1, setPass1] = useState('')
  const [pass2, setPass2] = useState('')
  const [show1, setShow1] = useState(false)
  const [show2, setShow2] = useState(false)
  const [ok, setOk] = useState(false)
  const [error, setError] = useState()
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const submit = async (e)=>{
    e.preventDefault()
    if (pass1 !== pass2) return setError('Las contraseñas no coinciden')
    setBusy(true); setError(undefined)
    try{
      await api.post(PATHS.auth.passwordResetConfirm, { uid, token, new_password: pass1 })
      setOk(true)
      setTimeout(()=>navigate('/login'), 800)
    }catch(err){
      const d = err?.response?.data
      setError(d?.detail || 'No se pudo cambiar la contraseña')
    }finally{ setBusy(false) }
  }

  return (
    <div style={{minHeight:'100vh', display:'grid', placeItems:'center', background:'var(--bg)'}}>
      <div className="card" style={{width:'min(520px, 94vw)'}}>
        <h2 style={{marginTop:0}}>Nueva contraseña</h2>
        <form className="grid" onSubmit={submit}>
          <div className="input-group">
            <input type={show1?'text':'password'} placeholder="Nueva contraseña" value={pass1} onChange={e=>setPass1(e.target.value)} required/>
            <button type="button" className="icon-btn" onClick={()=>setShow1(v=>!v)}>{show1 ? <EyeOff/> : <Eye/>}</button>
          </div>
          <div className="input-group">
            <input type={show2?'text':'password'} placeholder="Repite la contraseña" value={pass2} onChange={e=>setPass2(e.target.value)} required/>
            <button type="button" className="icon-btn" onClick={()=>setShow2(v=>!v)}>{show2 ? <EyeOff/> : <Eye/>}</button>
          </div>
          {error && <div style={{color:'#fca5a5'}}>{error}</div>}
          {ok && <div style={{color:'#22c55e'}}>Contraseña actualizada. Redirigiendo…</div>}
          <button className="primary" disabled={busy}>{busy? 'Guardando…':'Cambiar contraseña'}</button>
          <div className="auth-links"><Link to="/login">Volver al login</Link></div>
        </form>
      </div>
    </div>
  )
}
