import { useEffect, useState } from 'react'
import api from '../../api/axios.js'
import { useAuth } from '../../hooks/useAuth.jsx'

export default function Roles(){
  const [items,setItems] = useState([])
  const [form,setForm] = useState({})
  const [permisos, setPermisos] = useState([])
  const { fetchMe } = useAuth() // Obtenemos la función para refrescar permisos

  const load = async()=>{
    const r = await api.get('/cuentas/roles/?ordering=nombre')
    const p = await api.get('/cuentas/permisos/?ordering=codigo')
    setItems(r.data?.results || r.data)
    setPermisos(p.data?.results || p.data)
  }
  useEffect(()=>{ load() }, [])

  const save = async(e)=>{
    e.preventDefault()
    const payload = {...form, permisos:(form.permisos||[]).map(Number)}
    if (form.id) await api.put(`/cuentas/roles/${form.id}/`, payload)
    else await api.post(`/cuentas/roles/`, payload)
    setForm({}); load(); fetchMe(); // <-- Refrescamos los permisos del usuario actual
  }
  const del = async(id)=>{ if(confirm('¿Eliminar rol?')){ await api.delete(`/cuentas/roles/${id}/`); load() } }
  const togglePerm = (pid)=>{
    const set = new Set(form.permisos||[])
    set.has(pid)? set.delete(pid) : set.add(pid)
    setForm(f=>({...f, permisos:[...set]}))
  }

  return (
    <div className="grid">
      <div className="card">
        <h3>Roles</h3>
         <div className="table-responsive">
        <table>
          <thead><tr><th>Nombre</th><th>Permisos</th><th></th></tr></thead>
          <tbody>
            {items.map(r=>(
              <tr key={r.id}>
                <td>{r.nombre}</td>
                <td>{(r.permisos_obj||[]).map(p=>p.codigo).join(', ')}</td>
                <td>
                  <button onClick={()=>setForm({id:r.id, nombre:r.nombre, permisos:(r.permisos_obj||[]).map(p=>p.id)})}>Editar</button>
                  <span> </span>
                  <button onClick={()=>del(r.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>
      <div className="card">
        <h3>{form.id? 'Editar' : 'Nuevo'} rol</h3>
        <form onSubmit={save} className="grid">
          <input placeholder="Nombre del rol" value={form.nombre||''} onChange={e=>setForm({...form, nombre:e.target.value})} required/>
          <div>
            <div style={{color:'#94a3b8', fontSize:12, marginBottom:6}}>Permisos</div>
            <div style={{display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:6}}>
              {permisos.map(p=>(
                <label key={p.id} style={{display:'inline-flex', gap:6, alignItems:'center'}}>
                  <input type="checkbox" checked={(form.permisos||[]).includes(p.id)} onChange={()=>togglePerm(p.id)}/>
                  {p.codigo}
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
