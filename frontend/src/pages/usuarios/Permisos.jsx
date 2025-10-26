import { useEffect, useState } from 'react'
import api from '../../api/axios.js'

export default function Permisos(){
  const [items,setItems] = useState([])
  const [form,setForm] = useState({})

  const load = async()=>{
    const r = await api.get('/cuentas/permisos/?ordering=codigo')
    setItems(r.data?.results || r.data)
  }
  useEffect(()=>{ load() }, [])

  const save = async(e)=>{
    e.preventDefault()
    if (form.id) await api.put(`/cuentas/permisos/${form.id}/`, form)
    else await api.post(`/cuentas/permisos/`, form)
    setForm({}); load()
  }
  const del = async(id)=>{ if(confirm('¿Eliminar permiso?')){ await api.delete(`/cuentas/permisos/${id}/`); load() } }

  return (
    <div className="grid">
      <div className="card">
        <h3>Permisos</h3>
         <div className="table-responsive">
        <table>
          <thead><tr><th>Código</th><th>Descripción</th><th></th></tr></thead>
          <tbody>
            {items.map(p=>(
              <tr key={p.id}>
                <td>{p.codigo}</td>
                <td>{p.descripcion}</td>
                <td>
                  <button onClick={()=>setForm({id:p.id, codigo:p.codigo, descripcion:p.descripcion})}>Editar</button>
                  <span> </span>
                  <button onClick={()=>del(p.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>
      <div className="card">
        <h3>{form.id? 'Editar' : 'Nuevo'} permiso</h3>
        <form onSubmit={save} className="grid">
          <input placeholder="Código (ej. catalogo.crear)" value={form.codigo||''} onChange={e=>setForm({...form, codigo:e.target.value})} required/>
          <input placeholder="Descripción" value={form.descripcion||''} onChange={e=>setForm({...form, descripcion:e.target.value})}/>
          <button className="primary">Guardar</button>
        </form>
      </div>
    </div>
  )
}
