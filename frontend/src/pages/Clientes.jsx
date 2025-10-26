import { useEffect, useState } from 'react'
import api from '../api/axios'
import { PATHS } from '../api/paths'
    
export default function Clientes(){
  const [items, setItems] = useState([])
  const [form, setForm] = useState(null) // Usamos null para saber si el formulario debe mostrarse
    
  const load = async ()=>{
    const resClientes = await api.get(`${PATHS.clientes}?ordering=nombre`)
    setItems(resClientes.data?.results || resClientes.data || [])
  }
  useEffect(()=>{ load() }, [])
    
  const save = async (e)=>{
    e.preventDefault()
    const payload = { ...form }
    // La creación de clientes es automática, aquí solo editamos
    if(form.id) {
      await api.put(`${PATHS.clientes}${form.id}/`, payload)
      setForm(null); 
      load()
    }
  }
    
  return (
    <div className="grid">
      <div className="card">
        <h3>Clientes</h3>
        <div className="table-responsive">
          <table className="table-nowrap">
            <thead><tr><th>Nombre / Razón Social</th><th>Email</th><th>Teléfono</th><th></th></tr></thead>
            <tbody>
              {items.map(c => (
                <tr key={c.id}>
                  <td>{c.nombre} {c.usuario_obj ? `(@${c.usuario_obj.username})` : ''}</td>
                  <td>{c.email || c.usuario_obj?.email}</td>
                  <td>{c.telefono}</td>
                  <td>
                    <div className="btn-row">
                      <button onClick={()=>setForm(c)}>Editar Perfil Facturación</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    
      {form && <div className="card">
        <h3>Editar perfil de facturación</h3>
        <form className="grid" onSubmit={save}>
          <input placeholder="Nombre o Razón Social" value={form.nombre||''} onChange={e=>setForm({...form, nombre:e.target.value})} required/>
          <input placeholder="Email de facturación" value={form.email||''} onChange={e=>setForm({...form, email:e.target.value})}/>
          <input placeholder="Teléfono" value={form.telefono||''} onChange={e=>setForm({...form, telefono:e.target.value})}/>
          <input placeholder="Dirección" value={form.direccion||''} onChange={e=>setForm({...form, direccion:e.target.value})}/>
          <input placeholder="CI / NIT" value={form.documento||''} onChange={e=>setForm({...form, documento:e.target.value})}/>
          <button className="primary">Actualizar Perfil</button>
        </form>
      </div>}
    </div>
  )
}
