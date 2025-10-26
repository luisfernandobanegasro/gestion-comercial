import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { PATHS } from '../api/paths'
import Pagos from './pagos/Pagos'

export default function DetalleVenta() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [venta, setVenta] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadVenta = useCallback(async () => {
    try {
      const res = await api.get(`${PATHS.ventas.root}${id}/`)
      setVenta(res.data)
    } catch (error) {
      console.error("Error al cargar la venta:", error)
      alert("No se pudo cargar la venta.")
      navigate('/ventas')
    } finally {
      setLoading(false)
    }
  }, [id, navigate])

  useEffect(() => {
    loadVenta()
  }, [loadVenta])

  const descargarComprobante = () => {
    // La URL base de la API ya incluye /api
    const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace('/api', '');
    const url = `${baseUrl}${PATHS.ventas.comprobante(id)}`;
    // Abrimos la URL del comprobante en una nueva pestaña
    window.open(url, '_blank');
  }

  if (loading) return <div className="card">Cargando detalle de la venta...</div>
  if (!venta) return <div className="card">Venta no encontrada.</div>

  return (
    <div className="grid">
      <div className="card">
        <div className="btn-row">
          <h2>Detalle de Venta - Folio: {venta.folio}</h2>
          <span className="spacer"></span>
          <span className={`status-pill ${venta.estado}`}>{venta.estado}</span>
        </div>
        <p><strong>Cliente:</strong> {venta.cliente_obj?.nombre || 'N/A'}</p>
        <p><strong>Fecha:</strong> {new Date(venta.creado_en).toLocaleString()}</p>

        <h3>Items de la Venta</h3>
        <div className="table-responsive">
          <table className="table-nowrap">
            <thead><tr><th>Producto</th><th>Cantidad</th><th>Precio Unit.</th><th>Subtotal</th></tr></thead>
            <tbody>
              {venta.items.map(it => (
                <tr key={it.id}>
                  <td>{it.producto_nombre}</td>
                  <td>{it.cantidad}</td>
                  <td>Bs. {Number(it.precio_unit).toFixed(2)}</td>
                  <td>Bs. {Number(it.subtotal).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th colSpan="3" style={{ textAlign: 'right' }}>Total:</th>
                <th>Bs. {Number(venta.total).toFixed(2)}</th>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <div className="card">
        <h3>Acciones</h3>
        {venta.estado === 'pagada' ? (
          <div className="btn-row">
            <button className="primary" onClick={descargarComprobante}>Descargar Comprobante (PDF)</button>
            <p>Esta venta ya ha sido pagada.</p>
          </div>
        ) : (
          <p>No hay acciones disponibles para una venta en estado '{venta.estado}'.</p>
        )}

        {venta.estado === 'pendiente' && (
          <Pagos venta={venta} onPaymentSuccess={loadVenta} />
        )}
      </div>
    </div>
  )
}