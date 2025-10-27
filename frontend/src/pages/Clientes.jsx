import { useEffect, useState } from 'react'
import api from '../api/axios'
import { PATHS } from '../api/paths'

export default function Clientes(){
  const [items, setItems] = useState([])
  const [form, setForm] = useState(null)
  const [q, setQ] = useState('')

  // ——— Carga de clientes con búsqueda ———
  const load = async (query='')=>{
    const url = `${PATHS.clientes}?ordering=nombre${query ? `&search=${encodeURIComponent(query)}` : ''}`
    const res = await api.get(url)
    setItems(res.data?.results || res.data || [])
  }
  useEffect(()=>{ load() }, [])

  // ——— Búsqueda con debounce ———
  useEffect(()=>{
    const t = setTimeout(()=>load(q.trim()), 350)
    return () => clearTimeout(t)
  }, [q])

  // ——— Guardar edición ———
  const save = async (e)=>{
    e.preventDefault()
    const payload = {
      nombre:   form.nombre   || '',
      email:    form.email    || '',
      telefono: form.telefono || '',
      documento:form.documento|| '',   // CI/NIT
    }
    if(form.id){
      await api.put(`${PATHS.clientes}${form.id}/`, payload)
      setForm(null)
      load(q.trim())
    }
  }

  return (
    // usa un split: lista + form (dos columnas en desktop, una en móvil)
    <div className={`panel-split ${form ? 'has-form' : ''}`}>
      <div className="card">
        <h3>Clientes</h3>

        <div className="btn-row" style={{marginBottom:12}}>
          <input
            placeholder="Buscar por nombre, email, teléfono o CI/NIT…"
            value={q}
            onChange={e=>setQ(e.target.value)}
            style={{flex:'1 1 280px'}}
          />
          {q && <button onClick={()=>setQ('')}>Limpiar</button>}
        </div>

        <div className="table-responsive">
          <table className="table clientes-table">
            <colgroup>
              <col style={{width:'36%'}} />
              <col style={{width:'32%'}} />
              <col style={{width:'16%'}} />
              <col style={{width:'12%'}} />
              {/* Columna de acciones con ancho fijo en px */}
              <col style={{width:'56px'}} />
            </colgroup>
            <thead>
              <tr>
                <th className="th-nowrap">Nombre / Razón Social</th>
                <th className="th-nowrap">Email</th>
                <th className="th-nowrap">Teléfono</th>
                <th className="th-nowrap">CI / NIT</th>
                <th aria-label="Acciones"></th>
              </tr>
            </thead>
            <tbody>
              {items.map(c => (
                <tr key={c.id}>
                  <td className="col-text">
                    {c.nombre} {c.usuario_obj ? `(@${c.usuario_obj.username})` : ''}
                  </td>
                  <td className="col-text">{c.email || c.usuario_obj?.email}</td>
                  <td className="col-num">{c.telefono}</td>
                  <td className="col-num">{c.documento}</td>
                  <td className="col-actions">
                    <button
                      className="action-btn"
                      title="Editar perfil de facturación"
                      aria-label="Editar perfil de facturación"
                      onClick={()=>setForm(c)}
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                        strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 20h9" />
                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
                      </svg>
                      <span className="label">Editar Perfil</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {form && (
        <div className="card">
          <h3>Editar perfil de facturación</h3>
          <form className="form-row" onSubmit={save}>
            {/* ...inputs iguales */}
            <button className="primary">Actualizar Perfil</button>
          </form>
        </div>
      )}
    </div>
  )
}
