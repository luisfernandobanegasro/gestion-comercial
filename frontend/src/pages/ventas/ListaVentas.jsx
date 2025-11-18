// src/pages/ventas/ListaVentas.jsx
import { useEffect, useState, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'

export default function ListaVentas() {
  const [ventas, setVentas] = useState([])
  const [loading, setLoading] = useState(true)

  const [search, setSearch] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const navigate = useNavigate()

  const loadVentas = useCallback(async () => {
    setLoading(true)
    try {
      // pedimos una cantidad grande y ordenada por fecha desc
      const res = await api.get(PATHS.ventas.root, {
        params: {
          page_size: 500,
          ordering: '-creado_en'
        }
      })
      setVentas(res.data?.results || res.data || [])
    } catch (error) {
      console.error('Error al cargar la lista de ventas:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadVentas()
  }, [loadVentas])

  // ==========================
  // Filtro en memoria
  // ==========================
  const filteredVentas = useMemo(() => {
    const q = search.trim().toLowerCase()
    const start = startDate ? new Date(startDate) : null
    const end = endDate ? new Date(endDate) : null

    return ventas.filter(v => {
      // buscador por folio / cliente / doc / tel / usuario
      if (q) {
        const texto = [
          v.folio,
          v.cliente_nombre,
          v.cliente_documento,
          v.cliente_telefono,
          v.usuario_username
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()
        if (!texto.includes(q)) return false
      }

      // filtro por rango de fechas (creado_en viene en ISO)
      if (start || end) {
        const fechaVenta = new Date(v.creado_en)
        if (start && fechaVenta < start) return false
        if (end) {
          // incluimos el día completo del end
          const endPlus = new Date(end)
          endPlus.setHours(23, 59, 59, 999)
          if (fechaVenta > endPlus) return false
        }
      }

      return true
    })
  }, [ventas, search, startDate, endDate])

  const handleClearFilters = () => {
    setSearch('')
    setStartDate('')
    setEndDate('')
  }

  if (loading) return <div className="card">Cargando historial de ventas...</div>

  return (
    <div className="card">
      <h3>Historial de Ventas</h3>

      {/* Filtros */}
      <div
        className="form-row"
        style={{ gap: 12, flexWrap: 'wrap', marginBottom: 12 }}
      >
        <input
          type="text"
          placeholder="Buscar por folio, cliente, CI, teléfono o usuario..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ minWidth: 260 }}
        />

        <input
          type="date"
          value={startDate}
          onChange={e => setStartDate(e.target.value)}
        />
        <input
          type="date"
          value={endDate}
          onChange={e => setEndDate(e.target.value)}
        />

        <button type="button" onClick={handleClearFilters}>
          Limpiar filtros
        </button>
      </div>

      <div className="table-responsive">
        <table className="table-nowrap">
          <thead>
            <tr>
              <th>Folio</th>
              <th>Cliente</th>
              <th>Fecha</th>
              <th>Total</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredVentas.map(v => (
              <tr key={v.id}>
                <td>{v.folio}</td>
                <td>{v.cliente_nombre}</td>
                <td>{new Date(v.creado_en).toLocaleDateString()}</td>
                <td>Bs. {Number(v.total).toFixed(2)}</td>
                <td>
                  <span className={`status-pill ${v.estado}`}>{v.estado}</span>
                </td>
                <td>
                  <button onClick={() => navigate(`/ventas/${v.id}`)}>
                    Ver / Pagar
                  </button>
                </td>
              </tr>
            ))}

            {!filteredVentas.length && (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '12px' }}>
                  No se encontraron ventas para los filtros aplicados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
