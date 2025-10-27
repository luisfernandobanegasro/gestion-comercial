import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'
import Pagos from '../pagos/Pagos'

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

  const descargarComprobante = async () => {
    try {
      // 1. Usamos axios para hacer la petición autenticada, esperando un blob
      const response = await api.get(PATHS.ventas.comprobante(id), {
        responseType: 'blob',
      });

      // 2. Creamos una URL temporal para el blob recibido
      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);

      // 3. Abrimos la URL temporal en una nueva pestaña
      window.open(fileURL, '_blank');
    } catch (error) {
      console.error("Error al descargar el comprobante:", error);
      alert("No se pudo generar el comprobante.");
    }
  };

  if (loading) return <div className="card">Cargando detalle de la venta...</div>
  if (!venta) return <div className="card">Venta no encontrada.</div>

  // DetalleVenta.jsx (solo la parte del render)
  return (
    <div className="venta-grid">
      <div className="card">
        <header className="venta-header">
          <div className="venta-title">
            <span className="venta-subtitle">Detalle de Venta</span>
            <h1 className="venta-folio">Folio: {venta.folio}</h1>
          </div>
          <span className={`status-pill ${venta.estado}`}>{venta.estado}</span>
        </header>

        <div className="venta-meta">
          <div><strong>Cliente:</strong> {venta.cliente_obj?.nombre || 'N/A'}</div>
          <div><strong>Fecha:</strong> {new Date(venta.creado_en).toLocaleString()}</div>
        </div>

        <h3>Items de la Venta</h3>
        <div className="table-scroll">
          <table className="table">
            <thead>
              <tr><th>Producto</th><th>Cantidad</th><th>Precio Unit.</th><th>Subtotal</th></tr>
            </thead>
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
                <th colSpan="3" className="ta-right">Total:</th>
                <th>Bs. {Number(venta.total).toFixed(2)}</th>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <div className="card">
        <h3>Acciones</h3>
        {venta.estado === 'pendiente' && (
          <div className="btn-row">
            <button onClick={() => navigate(`/ventas/editar/${venta.id}`)}>Editar Venta</button>
          </div>
        )}

        {venta.estado === 'pagada' ? (
          <div className="stack gap-8">
            <button className="primary" onClick={descargarComprobante}>Descargar Comprobante (PDF)</button>
            <p className="muted">Esta venta ya ha sido pagada.</p>
          </div>
        ) : venta.estado !== 'pendiente' && (
          <p className="muted">No hay acciones disponibles para una venta en estado '{venta.estado}'.</p>
        )}

        {venta.estado === 'pendiente' && (
          <Pagos venta={venta} onPaymentSuccess={loadVenta} />
        )}
      </div>
    </div>
  )

}