import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { PATHS } from '../api/paths'

export default function Registro(){
  const [form, setForm] = useState({ username:'', email:'', password:'', first_name: '', last_name: '' })
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState()
  const [ok, setOk] = useState(false)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  const submit = async (e)=>{
    e.preventDefault()
    setBusy(true); setError(undefined)
    try{
      await api.post(PATHS.auth.register, form)
      setOk(true)
      setTimeout(()=> navigate('/login'), 800)
    }catch(err){
      const d = err?.response?.data
      setError(d?.detail || Object.values(d||{})?.[0]?.[0] || 'No se pudo registrar')
    }finally{ setBusy(false) }
  }

  return (
    <div style={{minHeight:'100vh', display:'grid', placeItems:'center', background:'var(--bg)'}}>
      <div className="card" style={{width:'min(520px, 94vw)'}}>
        <h2 style={{marginTop:0}}>Crear cuenta</h2>
        <form className="grid" onSubmit={submit}>
      <input placeholder="Nombres" value={form.first_name} onChange={e=>setForm({...form, first_name:e.target.value})} required/>
      <input placeholder="Apellidos" value={form.last_name} onChange={e=>setForm({...form, last_name:e.target.value})} required/>
          <input placeholder="Usuario" value={form.username} onChange={e=>setForm({...form, username:e.target.value})} required/>
          <input type="email" placeholder="Email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})} required/>

          <div className="input-group">
            <input
              type={showPass ? 'text':'password'}
              placeholder="Contraseña"
              value={form.password}
              onChange={e=>setForm({...form, password:e.target.value})}
              required
            />
            <button type="button" className="icon-btn" onClick={()=>setShowPass(v=>!v)}>{showPass?'🙈':'👁️'}</button>
          </div>

          {error && <div style={{color:'#fca5a5'}}>{String(error)}</div>}
          {ok && <div style={{color:'#22c55e'}}>Cuenta creada. Redirigiendo…</div>}
          <button className="primary" disabled={busy}>{busy? 'Guardando…':'Registrarme'}</button>
          <div className="auth-links"><Link to="/login">Volver al login</Link></div>
        </form>
      </div>
    </div>
  )
}
