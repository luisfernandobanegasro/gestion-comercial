import { useEffect, useMemo, useState, useCallback, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'
import ListaVentas from './ListaVentas'
import { Plus, Minus, Trash2, ShoppingCart } from 'lucide-react'

function FormularioNuevaVenta({ onVentaGuardada, isEditing }) {
  const navigate = useNavigate()
  const { id: ventaId } = useParams()
  const [productos, setProductos] = useState([])
  const [buscar, setBuscar] = useState('')
  const [carrito, setCarrito] = useState([])
  const [productoActivo, setProductoActivo] = useState(null)
  const [cliente, setCliente] = useState('')
  const [clientes, setClientes] = useState([])
  const [loadingVenta, setLoadingVenta] = useState(isEditing)

  // ref para hacer scroll al carrito (CTA móvil)
  const carritoRef = useRef(null)

  useEffect(() => {
    (async () => {
      try {
        const p = await api.get(`${PATHS.productos}?ordering=nombre`)
        setProductos(p.data?.results || p.data || [])
      } catch { setProductos([]) }

      try {
        const c = await api.get(`${PATHS.clientes}?ordering=nombre`)
        setClientes(c.data?.results || c.data || [])
      } catch { setClientes([]) }

      if (isEditing && ventaId) {
        try {
          const res = await api.get(`${PATHS.ventas.root}${ventaId}/`)
          const v = res.data
          setCliente(v.cliente)
          setCarrito(v.items.map(it => ({
            producto: it.producto,
            nombre: it.producto_nombre,
            cantidad: it.cantidad,
            precio_unit: Number(it.precio_unit)
          })))
        } finally { setLoadingVenta(false) }
      }
    })()
  }, [isEditing, ventaId])

  const list = useMemo(() => {
    const q = buscar.trim().toLowerCase()
    if (!q) return productos
    return productos.filter(x =>
      (x.nombre || '').toLowerCase().includes(q) ||
      (x.descripcion || '').toLowerCase().includes(q)
    )
  }, [productos, buscar])

  const add = useCallback((prod, cantidad = 1) => {
    setCarrito(prev => {
      const i = prev.findIndex(x => x.producto === prod.id)
      if (i >= 0) {
        const arr = [...prev]
        arr[i] = { ...arr[i], cantidad: arr[i].cantidad + cantidad }
        return arr
      }
      return [
        ...prev,
        {
          producto: prod.id,
          nombre: prod.nombre,
          modelo: prod.modelo,
          precio_unit: Number(prod.precio || 0),
          cantidad
        }
      ]
    })
    setProductoActivo(null) // cerrar modal
  }, [])

  const setCant = (i, v) =>
    setCarrito(prev => {
      const a = [...prev]
      a[i] = { ...a[i], cantidad: Math.max(1, Number(v) || 1) }
      return a
    })

  const inc = (i) => setCarrito(prev => {
    const a = [...prev]
    a[i] = { ...a[i], cantidad: a[i].cantidad + 1 }
    return a
  })
  const dec = (i) => setCarrito(prev => {
    const a = [...prev]
    a[i] = { ...a[i], cantidad: Math.max(1, a[i].cantidad - 1) }
    return a
  })

  const quitar = (i) => setCarrito(prev => prev.filter((_, k) => k !== i))
  const total = carrito.reduce((s, i) => s + i.cantidad * i.precio_unit, 0)

  const guardarVenta = async () => {
    if (!cliente) return alert('Selecciona un cliente')
    if (!carrito.length) return alert('El carrito está vacío')

    const payload = {
      cliente,
      items: carrito.map(it => ({
        producto: it.producto,
        cantidad: it.cantidad,
        precio_unit: it.precio_unit
      }))
    }

    try {
      let res
      if (isEditing) {
        res = await api.put(`${PATHS.ventas.root}${ventaId}/`, payload)
        alert('Venta actualizada con éxito.')
      } else {
        res = await api.post(PATHS.ventas.root, payload)
        alert('Venta creada con éxito. Redirigiendo al detalle de pago...')
      }
      onVentaGuardada(res.data.id)
    } catch (error) {
      console.error('Error al guardar la venta:', error.response?.data || error)
      alert(`Hubo un error al guardar la venta: ${error.response?.data?.detail || ''}`)
    }
  }

  const scrollToCarrito = () => {
    carritoRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  if (loadingVenta) return <div className="card">Cargando datos de la venta para editar...</div>

  return (
    <>
      <div className="ventas-layout">
        {/* Columna Izquierda: Filtros + Catálogo */}
        <div className="grid" style={{ gap: 16, alignContent: 'start' }}>
          <div className="card">
            <div className="form-row">
              <input
                placeholder="Buscar producto…"
                value={buscar}
                onChange={e => setBuscar(e.target.value)}
              />
              <select value={cliente} onChange={e => setCliente(e.target.value)}>
                <option value="">— Selecciona un cliente —</option>
                {(clientes || []).map(c => (
                  <option key={c.id} value={c.id}>{c.nombre}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="card">
            <h3>Catálogo</h3>
            <div className="cards">
              {list.map(p => (
                <div
                  key={p.id}
                  className="card-item"
                  onClick={() => setProductoActivo(p)}
                >
                  <img
                    src={p.imagen_url || `https://picsum.photos/seed/${p.id}/600/400`}
                    alt={p.nombre}
                  />
                  <div style={{ fontWeight: 700 }}>{p.nombre}</div>
                  <div style={{ color: 'var(--muted)' }}>
                    Bs. {Number(p.precio || 0).toFixed(2)}
                  </div>
                  <button
                    className="add-to-cart-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      add(p, 1)
                    }}
                    aria-label="Añadir al carrito"
                    title="Añadir al carrito"
                  >
                    <Plus size={20} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Columna Derecha: Carrito */}
        <div className="carrito-sticky" ref={carritoRef}>
          <div className="card carrito-card">
            <h3>
              Carrito {carrito.length ? <span style={{ opacity: .7 }}>({carrito.length})</span> : null}
            </h3>
            <CarritoTable
              carrito={carrito}
              setCant={setCant}
              inc={inc}
              dec={dec}
              quitar={quitar}
              total={total}
            />
            <div className="btn-row" style={{ marginTop: 12 }}>
              <button
                className="primary"
                onClick={guardarVenta}
                disabled={!cliente || !carrito.length}
              >
                {isEditing ? 'Actualizar Venta' : 'Crear Venta'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* CTA móvil fijo (aparece si hay ítems en carrito) */}
      {carrito.length > 0 && (
        <div className="venta-cta">
          <div className="cta-left">
            <ShoppingCart size={18} />
            <span>{carrito.length} ítem(s)</span>
            <b style={{ marginLeft: 8 }}>Total: Bs. {total.toFixed(2)}</b>
          </div>
          <div className="cta-actions">
            <button onClick={scrollToCarrito} className="action-btn">
              Ver carrito
            </button>
            <button
              className="primary"
              onClick={guardarVenta}
              disabled={!cliente}
            >
              {isEditing ? 'Actualizar' : 'Crear venta'}
            </button>
          </div>
        </div>
      )}

      {/* Modal de Detalle de Producto */}
      {productoActivo && (
        <ProductoModal
          producto={productoActivo}
          onAdd={add}
          onClose={() => setProductoActivo(null)}
        />
      )}

      {/* Estilos locales puntuales */}
      <style>{`
        .card-item { position: relative; cursor: pointer; }
        .add-to-cart-btn {
          position: absolute; bottom: 8px; right: 8px;
          background: var(--primary); color: var(--primary-ink);
          border: none; border-radius: 50%; width: 32px; height: 32px;
          cursor: pointer; padding: 0; display: grid; place-items: center; line-height: 1;
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .add-to-cart-btn:hover { transform: scale(1.1); box-shadow: 0 6px 16px rgba(0,0,0,0.25); }

        /* Stepper de cantidad dentro de la tabla */
        .qty-stepper {
          display: inline-flex; align-items: center; gap: 6px;
          border: 1px solid var(--border); border-radius: 8px; padding: 2px;
          background: transparent; height: 36px;
        }
        .qty-stepper .btn-icon { border: none; width: 32px; height: 32px; }
        .qty-stepper .btn-icon:hover { background: var(--border); }
        .qty-stepper .input-cantidad {
          width: 64px; height: 32px; border: none; text-align: center;
          background: transparent; color: var(--text); font-weight: 600;
          font-variant-numeric: tabular-nums; padding: 0 6px;
        }
        /* Quitar flechitas del input number */
        .qty-stepper .input-cantidad::-webkit-outer-spin-button,
        .qty-stepper .input-cantidad::-webkit-inner-spin-button{ -webkit-appearance: none; margin: 0; }
        .qty-stepper .input-cantidad[type="number"]{ -moz-appearance: textfield; appearance: textfield; }

        /* Asegura que la celda de cantidad no recorte el contenido */
        .carrito-card td.col-cant{ overflow: visible; white-space: nowrap; text-overflow: initial; }

        /* CTA móvil fijo al pie */
        .venta-cta{
          position: fixed; left: 0; right: 0; bottom: 0;
          display: flex; gap: 12px; align-items: center; justify-content: space-between;
          padding: 10px 14px; background: var(--surface); border-top: 1px solid var(--border);
          z-index: 50; box-shadow: 0 -6px 24px rgba(0,0,0,.25);
        }
        .venta-cta .cta-left{ display:flex; align-items:center; gap:8px; color: var(--text); }
        .venta-cta .cta-actions{ display:flex; gap:8px; }
        @media (min-width:1025px){ .venta-cta{ display:none; } }
      `}</style>
    </>
  )
}

function CarritoTable({ carrito, setCant, inc, dec, quitar, total }) {
  if (carrito.length === 0) {
    return <p style={{ color: 'var(--muted)', textAlign: 'center', padding: '20px 0' }}>
      El carrito está vacío.
    </p>
  }
  return (
    <div className="table-responsive">
      <table className="table-nowrap">
        <thead>
          <tr>
            <th>Producto</th>
            <th className="th-nowrap">Cantidad</th>
            <th className="th-nowrap">PU</th>
            <th className="th-nowrap">Subtotal</th>
            <th className="col-actions" />
          </tr>
        </thead>
        <tbody>
          {carrito.map((it, i) => (
            <tr key={i}>
              <td className="col-text">{it.nombre}</td>
              <td className="col-cant">
                <div className="qty-stepper">
                  <button className="btn-icon" onClick={() => dec(i)} aria-label="Disminuir">
                    <Minus size={16} />
                  </button>
                  <input
                    className="input-cantidad"
                    type="number"
                    min="1"
                    value={it.cantidad}
                    onChange={e => setCant(i, e.target.value)}
                  />
                  <button className="btn-icon" onClick={() => inc(i)} aria-label="Aumentar">
                    <Plus size={16} />
                  </button>
                </div>
              </td>
              <td className="col-num">{it.precio_unit.toFixed(2)}</td>
              <td className="col-num">{(it.precio_unit * it.cantidad).toFixed(2)}</td>
              <td className="col-actions">
                <button
                  className="btn-icon"
                  onClick={() => quitar(i)}
                  aria-label="Quitar"
                  title="Quitar"
                >
                  <Trash2 size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={3} style={{ textAlign: 'right' }}>Total:</th>
            <th>Bs. {total.toFixed(2)}</th>
            <th />
          </tr>
        </tfoot>
      </table>
    </div>
  )
}

function ProductoModal({ producto, onAdd, onClose }) {
  const [cantidad, setCantidad] = useState(1)
  const handleModalClick = (e) => e.stopPropagation()

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={handleModalClick}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        <div className="grid-2" style={{ alignItems: 'start' }}>
          <img
            src={producto.imagen_url || `https://picsum.photos/seed/${producto.id}/600/400`}
            alt={producto.nombre}
            style={{ width: '100%', borderRadius: 12 }}
          />
          <div>
            <h2>{producto.nombre}</h2>
            {producto.modelo && (
              <p style={{ color: 'var(--muted)', marginTop: -12 }}>
                Modelo: {producto.modelo}
              </p>
            )}
            <p><strong>Precio:</strong> Bs. {Number(producto.precio || 0).toFixed(2)}</p>
            <p><strong>Stock disponible:</strong> {producto.stock || 0}</p>

            {producto.caracteristicas ? (
              <div style={{ marginTop: 16 }}>
                <strong>Características:</strong>
                <p style={{ whiteSpace: 'pre-wrap', color: 'var(--muted)', marginTop: 4, fontSize: '14px' }}>
                  {producto.caracteristicas}
                </p>
              </div>
            ) : <p>Este producto no tiene una descripción detallada.</p>}

            <div className="btn-row" style={{ marginTop: 24 }}>
              <input
                type="number"
                min={1}
                value={cantidad}
                onChange={e => setCantidad(Math.max(1, Number(e.target.value)))}
                style={{ maxWidth: 80 }}
              />
              <button className="primary" onClick={() => onAdd(producto, cantidad)}>
                Añadir {cantidad} al carrito
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Ventas({ isEditing = false }) {
  const [tab, setTab] = useState('nueva')
  const navigate = useNavigate()

  const handleVentaGuardada = (id) => {
    navigate(`/ventas/${id}`)
  }

  return (
    <>
      {!isEditing && (
        <div className="card">
          <div className="tabs">
            <button
              className={`tab ${tab === 'nueva' ? 'active' : ''}`}
              onClick={() => setTab('nueva')}
            >
              Nueva Venta
            </button>
            <button
              className={`tab ${tab === 'lista' ? 'active' : ''}`}
              onClick={() => setTab('lista')}
            >
              Historial de Ventas
            </button>
          </div>
        </div>
      )}

      {isEditing && <div className="card"><h2>Editando Venta</h2></div>}

      {(tab === 'nueva' || isEditing)
        ? <FormularioNuevaVenta onVentaGuardada={handleVentaGuardada} isEditing={isEditing} />
        : <ListaVentas />}
    </>
  )
}
