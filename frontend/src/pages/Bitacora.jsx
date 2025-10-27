import { useEffect, useState } from 'react'
import api from '../api/axios'
import { PATHS } from '../api/paths'
import { saveAs } from 'file-saver'

const toLocalDT = (d) => {
  // datetime-local requiere yyyy-MM-ddTHH:mm (sin zona)
  const pad = (n) => String(n).padStart(2, '0')
  const y = d.getFullYear()
  const m = pad(d.getMonth() + 1)
  const day = pad(d.getDate())
  const h = pad(d.getHours())
  const min = pad(d.getMinutes())
  return `${y}-${m}-${day}T${h}:${min}`
}

export default function Bitacora() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ desde: '', hasta: '', usuario: '', modulo: '', q: '' })
  const [usuarios, setUsuarios] = useState([])
  const [modulos, setModulos] = useState([])

  // ---------- filtros rápidos de rango ----------
  const quickRange = {
    hoy: () => {
      const now = new Date()
      const start = new Date(now); start.setHours(0,0,0,0)
      setFilters(f => ({ ...f, desde: toLocalDT(start), hasta: toLocalDT(now) }))
    },
    h24: () => {
      const now = new Date()
      const start = new Date(now.getTime() - 24*60*60*1000)
      setFilters(f => ({ ...f, desde: toLocalDT(start), hasta: toLocalDT(now) }))
    },
    d7: () => {
      const now = new Date()
      const start = new Date(now.getTime() - 7*24*60*60*1000)
      setFilters(f => ({ ...f, desde: toLocalDT(start), hasta: toLocalDT(now) }))
    },
    mes: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0, 0)
      setFilters(f => ({ ...f, desde: toLocalDT(start), hasta: toLocalDT(now) }))
    },
    borrar: () => setFilters(f => ({ ...f, desde: '', hasta: '' }))
  }

  useEffect(() => {
    const loadFilterData = async () => {
      try {
        const resUsuarios = await api.get(`${PATHS.usuarios}?page_size=1000`)
        setUsuarios(resUsuarios.data?.results || resUsuarios.data || [])
        setModulos(['cuentas','catalogo','clientes','ventas','pagos','reportes','configuracion','auditoria'])
      } catch (error) {
        console.error("Error al cargar datos de filtros:", error)
      }
    }
    loadFilterData()
  }, [])

  useEffect(() => {
    const loadAuditData = async () => {
      setLoading(true)
      try {
        const params = new URLSearchParams(filters).toString()
        const r = await api.get(`${PATHS.auditoria}?ordering=-creado_en&${params}`)
        setItems(r.data || [])
      } catch {
        setItems([])
      } finally {
        setLoading(false)
      }
    }
    loadAuditData()
  }, [filters])

  const handleExport = async (format) => {
    try {
      const params = new URLSearchParams(filters).toString()
      const url = `${PATHS.auditoria}exportar-${format}/?${params}`
      const response = await api.get(url, { responseType: 'blob' })
      const ext = format === 'excel' ? 'xlsx' : format
      saveAs(response.data, `auditoria.${ext}`)
    } catch (error) {
      console.error(`Error al exportar a ${format}:`, error)
      alert(`No se pudo generar el archivo ${format}.`)
    }
  }

  return (
    <div className="grid">
      <div className="card">
        <h3 style={{ margin: 0 }}>Bitácora de Auditoría</h3>

        {/* FILTROS */}
        <div className="form-row" style={{ alignItems: 'flex-end', marginTop: 16, gap: 10 }}>
          <div className="input-group">
            <label>Desde</label>
            <input
              type="datetime-local"
              value={filters.desde}
              onChange={e => setFilters({ ...filters, desde: e.target.value })}
            />
          </div>
          <div className="input-group">
            <label>Hasta</label>
            <input
              type="datetime-local"
              value={filters.hasta}
              onChange={e => setFilters({ ...filters, hasta: e.target.value })}
            />
          </div>
          <div className="input-group">
            <label>Usuario</label>
            <select value={filters.usuario} onChange={e => setFilters({ ...filters, usuario: e.target.value })}>
              <option value="">Todos los usuarios</option>
              {usuarios.map(u => <option key={u.id} value={u.username}>{u.username}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label>Módulo</label>
            <select value={filters.modulo} onChange={e => setFilters({ ...filters, modulo: e.target.value })}>
              <option value="">Todos los módulos</option>
              {modulos.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div className="input-group" style={{ flex: 1 }}>
            <label>Búsqueda</label>
            <input
              type="text"
              value={filters.q}
              onChange={e => setFilters({ ...filters, q: e.target.value })}
              placeholder="Buscar por ruta, acción..."
            />
          </div>
        </div>

        {/* Rango rápido */}
        <div className="btn-row quick-range">
          <button onClick={quickRange.hoy}>Hoy</button>
          <button onClick={quickRange.h24}>Últimas 24 h</button>
          <button onClick={quickRange.d7}>Últimos 7 días</button>
          <button onClick={quickRange.mes}>Este mes</button>
          <button onClick={quickRange.borrar}>Borrar rango</button>
        </div>

        {/* Export */}
        <div className="btn-row" style={{ marginTop: 8 }}>
          <button onClick={() => handleExport('excel')}>Descargar Excel</button>
          <button onClick={() => handleExport('pdf')}>Descargar PDF</button>
        </div>

        {/* TABLA */}
        <div className="table-responsive" style={{ marginTop: 12 }}>
          <table className="audit-table sticky-head">
            <colgroup>
              {[
                <col key="fecha" style={{ width: '22%' }} />,
                <col key="user"  style={{ width: '16%' }} />,
                <col key="ip"    style={{ width: '12%' }} />,
                <col key="mod"   style={{ width: '10%' }} />,
                <col key="acc"   style={{ width: '12%' }} />,
                <col key="ruta"  style={{ width: '24%' }} />, // más aire para rutas largas
                <col key="met"   style={{ width: '4%'  }} />,
                <col key="est"   style={{ width: '4%'  }} />,
              ]}
            </colgroup>
            <thead>
              <tr>
                <th>Fecha y Hora</th>
                <th>Usuario</th>
                <th>IP</th>
                <th>Módulo</th>
                <th>Acción</th>
                <th>Ruta</th>
                <th>Método</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="8" style={{ textAlign: 'center' }}>Cargando...</td></tr>
              ) : items.length > 0 ? (
                items.map(r => (
                  <tr key={r.id}>
                    <td>{r.fecha_hora}</td>
                    <td>{r.usuario_username}</td>
                    <td>{r.ip}</td>
                    <td>{r.modulo}</td>
                    <td>{r.accion}</td>
                    <td>{r.ruta}</td>
                    <td>{r.metodo}</td>
                    <td>{r.estado}</td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan="8" style={{ textAlign: 'center' }}>No se encontraron registros.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
