import { useEffect, useState } from 'react'
import api from '../../api/axios.js'
import { useAuth } from '../../hooks/useAuth.jsx'

export default function Usuarios(){
  const [items,setItems] = useState([])
  const [form,setForm] = useState({})
  const [roles, setRoles] = useState([])
  const { fetchMe } = useAuth() // Obtenemos la función para refrescar permisos

  const load = async()=>{
    const u = await api.get('/cuentas/usuarios/?ordering=username')
    const r = await api.get('/cuentas/roles/?ordering=nombre')
    setItems(u.data?.results || u.data)
    setRoles(r.data?.results || r.data)
  }
  useEffect(()=>{ load() }, [])

  const save = async(e)=>{
    e.preventDefault()
    const payload = {...form, roles: (form.roles||[]).map(Number)}
    if (form.id) await api.put(`/cuentas/usuarios/${form.id}/`, payload)
    else await api.post(`/cuentas/usuarios/`, payload)
    setForm({}); load(); fetchMe(); // <-- Refrescamos los permisos del usuario actual
  }
  const del = async(id)=>{ if(confirm('¿Eliminar usuario?')){ await api.delete(`/cuentas/usuarios/${id}/`); load() } }
  const toggleRole = (rid)=>{
    const set = new Set(form.roles||[])
    set.has(rid)? set.delete(rid) : set.add(rid)
    setForm(f=>({...f, roles:[...set]}))
  }

  return (
    <div className="grid">
      <div className="card">
        <h3>Usuarios</h3>
         <div className="table-responsive">
        <table>
          <thead><tr><th>Usuario</th><th>Email</th><th>Roles</th><th></th></tr></thead>
          <tbody>
            {items.map(u=>(
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>{u.email}</td>
                <td>{(u.roles_obj||[]).map(r=>r.nombre).join(', ')}</td>
                <td>
                  <button onClick={()=>setForm({id:u.id, username:u.username, email:u.email, roles:(u.roles_obj||[]).map(r=>r.id)})}>Editar</button>
                  <span> </span>
                  <button onClick={()=>del(u.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>
      <div className="card">
        <h3>{form.id? 'Editar' : 'Nuevo'} usuario</h3>
        <form onSubmit={save} className="grid">
          <input placeholder="Usuario" value={form.username||''} onChange={e=>setForm({...form, username:e.target.value})} required/>
          <input placeholder="Email" value={form.email||''} onChange={e=>setForm({...form, email:e.target.value})}/>
          {!form.id && <input type="password" placeholder="Contraseña" value={form.password||''} onChange={e=>setForm({...form, password:e.target.value})} required/>}
          <div>
            <div style={{color:'#94a3b8', fontSize:12, marginBottom:6}}>Roles</div>
            <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
              {roles.map(r=>(
                <label key={r.id} style={{display:'inline-flex', gap:6, alignItems:'center'}}>
                  <input type="checkbox" checked={(form.roles||[]).includes(r.id)} onChange={()=>toggleRole(r.id)}/>
                  {r.nombre}
                </label>
              ))}
            </div>
          </div>
          <button className="primary">Guardar</button>
        </form>
      </div>
    </div>
  )
}
