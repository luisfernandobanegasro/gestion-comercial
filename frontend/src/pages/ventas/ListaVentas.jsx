import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'

export default function ListaVentas() {
  const [ventas, setVentas] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const loadVentas = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get(PATHS.ventas.root)
      setVentas(res.data?.results || res.data || [])
    } catch (error) {
      console.error("Error al cargar la lista de ventas:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadVentas()
  }, [loadVentas])

  if (loading) return <div className="card">Cargando historial de ventas...</div>

  return (
    <div className="card">
      <h3>Historial de Ventas</h3>
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
            {ventas.map(v => (
              <tr key={v.id}>
                <td>{v.folio}</td>
                <td>{v.cliente_nombre}</td>
                <td>{new Date(v.creado_en).toLocaleDateString()}</td>
                <td>Bs. {Number(v.total).toFixed(2)}</td>
                <td><span className={`status-pill ${v.estado}`}>{v.estado}</span></td>
                <td><button onClick={() => navigate(`/ventas/${v.id}`)}>Ver / Pagar</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}