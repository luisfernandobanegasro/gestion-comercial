// src/pages/ventas/Ventas.jsx
import { useEffect, useMemo, useState, useCallback, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'
import ListaVentas from './ListaVentas'
import Carrito from './Carrito'
import { Plus } from 'lucide-react'

// =========================
// Helper: obtener user_id del JWT
// =========================
function getUserIdFromAccessToken() {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return null
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const payloadBase64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const payloadJson = atob(payloadBase64)
    const payload = JSON.parse(payloadJson)
    // SimpleJWT por defecto usa "user_id"
    return payload.user_id || payload.id || null
  } catch {
    return null
  }
}

function FormularioNuevaVenta({ onVentaGuardada, isEditing }) {
  const navigate = useNavigate()
  const { id: ventaId } = useParams()

  const [productos, setProductos] = useState([])
  const [buscar, setBuscar] = useState('')
  const [filtroCategoria, setFiltroCategoria] = useState('')
  const [filtroMarca, setFiltroMarca] = useState('')
  const [soloOfertas, setSoloOfertas] = useState(false)

  const [categorias, setCategorias] = useState([])
  const [marcas, setMarcas] = useState([])

  const [carrito, setCarrito] = useState([])
  const [productoActivo, setProductoActivo] = useState(null)
  const [cliente, setCliente] = useState('')
  const [clientes, setClientes] = useState([])
  const [loadingVenta, setLoadingVenta] = useState(isEditing)

  // si encontramos un Cliente para el usuario actual → true
  const [esCliente, setEsCliente] = useState(false)
  const [currentUserId] = useState(() => getUserIdFromAccessToken())

  // ref para hacer scroll al carrito (CTA móvil)
  const carritoRef = useRef(null)

  // Helper para mapear VentaSerializer -> arreglo de items del frontend
  const syncCarritoFromVenta = useCallback((venta) => {
    if (!venta) {
      setCarrito([])
      return
    }
    const items = (venta.items || []).map(it => ({
      itemId: it.id,
      producto: it.producto,
      nombre: it.producto_nombre,
      cantidad: it.cantidad,
      precio_unit: Number(it.precio_unit),
    }))
    setCarrito(items)
  }, [])

  // Carga de combos + venta en edición
  useEffect(() => {
    ;(async () => {
      try {
        // Productos
        const p = await api.get(`${PATHS.productos}?ordering=nombre`)
        setProductos(p.data?.results || p.data || [])
      } catch {
        setProductos([])
      }

      try {
        // Clientes
        const c = await api.get(`${PATHS.clientes}?ordering=nombre`)
        const lista = c.data?.results || c.data || []
        setClientes(lista)

        // 🔵 Si el usuario tiene perfil de Cliente
        if (currentUserId) {
          const miCliente = lista.find(cli =>
            cli.usuario === currentUserId ||
            cli.usuario_id === currentUserId ||
            cli.usuario?.id === currentUserId
          )
          if (miCliente) {
            setCliente(String(miCliente.id))
            setEsCliente(true)
          }
        }
      } catch {
        setClientes([])
      }

      try {
        // Categorías
        const cat = await api.get(`${PATHS.categorias}?ordering=nombre`)
        setCategorias(cat.data?.results || cat.data || [])
      } catch {
        setCategorias([])
      }

      try {
        // Marcas
        const m = await api.get(`${PATHS.marcas}?ordering=nombre`)
        setMarcas(m.data?.results || m.data || [])
      } catch {
        setMarcas([])
      }

      // Carga de venta para edición
      if (isEditing && ventaId) {
        try {
          const res = await api.get(`${PATHS.ventas.root}${ventaId}/`)
          const v = res.data
          setCliente(String(v.cliente))
          syncCarritoFromVenta(v)
        } finally {
          setLoadingVenta(false)
        }
      } else {
        setLoadingVenta(false)
      }
    })()
  }, [isEditing, ventaId, currentUserId, syncCarritoFromVenta])

  // Carga del carrito desde backend cuando se conoce el cliente (solo en nueva venta)
  useEffect(() => {
    if (isEditing) return
    if (!cliente) return

    ;(async () => {
      try {
        const res = await api.get(PATHS.ventas.carrito, {
          params: { cliente },
        })
        // aseguramos que el cliente del carrito quede seteado
        if (res.data?.cliente) {
          setCliente(String(res.data.cliente))
        }
        syncCarritoFromVenta(res.data)
      } catch (e) {
        // si no hay carrito aún o 400, simplemente lo ignoramos
        console.error('No se pudo cargar carrito inicial:', e)
      }
    })()
  }, [cliente, isEditing, syncCarritoFromVenta])

  // Lista filtrada de productos (buscador + filtros + solo ofertas)
  const list = useMemo(() => {
    let data = productos

    if (filtroCategoria) {
      data = data.filter(p => String(p.categoria) === String(filtroCategoria))
    }
    if (filtroMarca) {
      data = data.filter(p => String(p.marca) === String(filtroMarca))
    }
    if (soloOfertas) {
      data = data.filter(p => !!p.oferta_activa)
    }

    const q = buscar.trim().toLowerCase()
    if (q) {
      data = data.filter(x =>
        (x.nombre || '').toLowerCase().includes(q) ||
        (x.modelo || '').toLowerCase().includes(q) ||
        (x.codigo || '').toLowerCase().includes(q) ||
        (x.caracteristicas || '').toLowerCase().includes(q)
      )
    }

    return data
  }, [productos, buscar, filtroCategoria, filtroMarca, soloOfertas])

  // =============================
  // Operaciones de carrito
  // =============================

  const add = useCallback(
    async (prod, cantidad = 1) => {
      if (!cliente) {
        alert('Selecciona un cliente antes de agregar productos.')
        return
      }

      // Edición de venta existente → solo en memoria, luego PUT
      if (isEditing) {
        const precioUnit = prod.precio_final != null
          ? Number(prod.precio_final)
          : Number(prod.precio || 0)

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
              itemId: undefined,
              producto: prod.id,
              nombre: prod.nombre,
              modelo: prod.modelo,
              precio_unit: precioUnit,
              cantidad,
            },
          ]
        })
        setProductoActivo(null)
        return
      }

      // Nueva venta → carrito en backend
      try {
        const res = await api.post(PATHS.ventas.carrito, {
          cliente,
          producto: prod.id,
          cantidad,
        })
        syncCarritoFromVenta(res.data)
      } catch (e) {
        console.error('Error al agregar al carrito:', e.response?.data || e)
        const data = e.response?.data || {}
        const msg =
          data.cantidad ||
          data.producto ||
          data.cliente ||
          data.detail ||
          'No se pudo agregar el producto al carrito.'
        alert(msg)
      } finally {
        setProductoActivo(null)
      }
    },
    [cliente, isEditing, syncCarritoFromVenta]
  )

  const updateCantidadLocal = (i, nuevaCantidad) => {
    setCarrito(prev => {
      const a = [...prev]
      a[i] = { ...a[i], cantidad: Math.max(1, nuevaCantidad) }
      return a
    })
  }

  const updateCantidadBackend = async (itemId, nuevaCantidad) => {
    try {
      const res = await api.patch(PATHS.ventas.carritoItem(itemId), {
        cantidad: nuevaCantidad,
      })
      syncCarritoFromVenta(res.data)
    } catch (e) {
      console.error(e)
      alert('No se pudo actualizar la cantidad.')
    }
  }

  const setCant = (i, v) => {
    const n = Math.max(1, Number(v) || 1)
    const item = carrito[i]
    if (!item) return

    if (isEditing || !item.itemId) {
      updateCantidadLocal(i, n)
    } else {
      updateCantidadBackend(item.itemId, n)
    }
  }

  const inc = i => {
    const item = carrito[i]
    if (!item) return
    const nueva = item.cantidad + 1
    if (isEditing || !item.itemId) {
      updateCantidadLocal(i, nueva)
    } else {
      updateCantidadBackend(item.itemId, nueva)
    }
  }

  const dec = i => {
    const item = carrito[i]
    if (!item) return
    const nueva = Math.max(1, item.cantidad - 1)
    if (isEditing || !item.itemId) {
      updateCantidadLocal(i, nueva)
    } else {
      updateCantidadBackend(item.itemId, nueva)
    }
  }

  const quitar = async i => {
    const item = carrito[i]
    if (!item) return

    // edición → solo local
    if (isEditing || !item.itemId) {
      setCarrito(prev => prev.filter((_, k) => k !== i))
      return
    }

    // nueva venta → backend
    try {
      const res = await api.delete(PATHS.ventas.carritoItem(item.itemId))
      // si backend devuelve carrito actualizado (como lo hicimos)
      if (res.data) {
        syncCarritoFromVenta(res.data)
      } else {
        // por si acaso, recargamos
        const r2 = await api.get(PATHS.ventas.carrito, { params: { cliente } })
        syncCarritoFromVenta(r2.data)
      }
    } catch (e) {
      console.error(e)
      alert('No se pudo quitar el producto del carrito.')
    }
  }

  const total = useMemo(
    () => carrito.reduce((s, i) => s + i.cantidad * i.precio_unit, 0),
    [carrito]
  )

  const guardarVenta = async () => {
    if (!cliente) return alert('Selecciona un cliente')
    if (!carrito.length) return alert('El carrito está vacío')

    // Edición → sigue usando PUT /ventas/{id}/
    if (isEditing) {
      const payload = {
        cliente,
        items: carrito.map(it => ({
          producto: it.producto,
          cantidad: it.cantidad,
          precio_unit: it.precio_unit,
        })),
      }

      try {
        const res = await api.put(`${PATHS.ventas.root}${ventaId}/`, payload)
        alert('Venta actualizada con éxito.')
        onVentaGuardada(res.data.id)
      } catch (error) {
        console.error('Error al guardar la venta:', error.response?.data || error)
        alert(
          `Hubo un error al guardar la venta: ${
            error.response?.data?.detail || ''
          }`
        )
      }
      return
    }

    // Nueva venta → confirmar carrito en backend
    try {
      const res = await api.post(PATHS.ventas.carritoConfirmar, { cliente })
      alert('Venta creada con éxito. Redirigiendo al detalle de pago...')
      onVentaGuardada(res.data.id)
    } catch (error) {
      console.error('Error al guardar la venta:', error.response?.data || error)
      alert(
        `Hubo un error al guardar la venta: ${
          error.response?.data?.detail || ''
        }`
      )
    }
  }

  const scrollToCarrito = () => {
    carritoRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const limpiarFiltros = () => {
    setBuscar('')
    setFiltroCategoria('')
    setFiltroMarca('')
    setSoloOfertas(false)
  }

  if (loadingVenta) {
    return <div className="card">Cargando datos de la venta para editar...</div>
  }

  return (
    <>
      <div className="ventas-layout">
        {/* Columna Izquierda: Filtros + Catálogo */}
        <div className="grid" style={{ gap: 16, alignContent: 'start' }}>
          <div className="card">
            <div
              className="form-row"
              style={{ flexWrap: 'wrap', gap: 8, alignItems: 'center' }}
            >
              <input
                placeholder="Buscar producto por nombre, modelo o código…"
                value={buscar}
                onChange={e => setBuscar(e.target.value)}
                style={{ flex: '2 1 220px' }}
              />

              <select
                value={filtroCategoria}
                onChange={e => setFiltroCategoria(e.target.value)}
                style={{ flex: '1 1 160px' }}
              >
                <option value="">Todas las categorías</option>
                {categorias.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.nombre}
                  </option>
                ))}
              </select>

              <select
                value={filtroMarca}
                onChange={e => setFiltroMarca(e.target.value)}
                style={{ flex: '1 1 160px' }}
              >
                <option value="">Todas las marcas</option>
                {marcas.map(m => (
                  <option key={m.id} value={m.id}>
                    {m.nombre}
                  </option>
                ))}
              </select>

              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  fontSize: 13
                }}
              >
                <input
                  type="checkbox"
                  checked={soloOfertas}
                  onChange={e => setSoloOfertas(e.target.checked)}
                />
                Solo ofertas
              </label>

              <button
                type="button"
                onClick={limpiarFiltros}
                className="btn-secondary"
                style={{ fontSize: 13 }}
              >
                Limpiar
              </button>
            </div>

            <div
              className="form-row"
              style={{ marginTop: 12, gap: 8, alignItems: 'center' }}
            >
              {esCliente ? (
                // Cliente logueado → ve solo su propio nombre
                <input
                  type="text"
                  value={
                    (clientes || []).find(c => String(c.id) === String(cliente))
                      ?.nombre || 'Mi cuenta'
                  }
                  disabled
                  style={{ flex: 1, background: 'var(--surface)', opacity: 0.8 }}
                />
              ) : (
                // Admin / empleado → puede elegir cualquier cliente
                <select
                  value={cliente}
                  onChange={e => setCliente(e.target.value)}
                  style={{ flex: 1 }}
                >
                  <option value="">— Selecciona un cliente —</option>
                  {(clientes || []).map(c => (
                    <option key={c.id} value={c.id}>
                      {c.nombre}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          <div className="card">
            <h3>Catálogo</h3>
            <div className="cards">
              {list.map(p => {
                const precioOriginal = Number(p.precio || 0)
                const precioDesc = p.precio_final != null
                  ? Number(p.precio_final)
                  : precioOriginal
                const descuento = p.oferta_activa
                  ? Number(p.oferta_activa.porcentaje_descuento).toFixed(0)
                  : null
                const tieneDescuento = descuento && precioDesc < precioOriginal

                return (
                  <div
                    key={p.id}
                    className="card-item"
                    onClick={() => setProductoActivo(p)}
                  >
                    <img
                      src={
                        p.imagen_url ||
                        `https://picsum.photos/seed/${p.id}/600/400`
                      }
                      alt={p.nombre}
                    />

                    {tieneDescuento && (
                      <span className="badge-oferta">-{descuento}%</span>
                    )}

                    <div style={{ fontWeight: 700 }}>{p.nombre}</div>
                    <div style={{ fontSize: 13, color: 'var(--muted)' }}>
                      {p.marca_nombre || 'Sin marca'} · {p.categoria_nombre}
                    </div>

                    <div style={{ marginTop: 4 }}>
                      {tieneDescuento ? (
                        <>
                          <span
                            style={{
                              textDecoration: 'line-through',
                              opacity: 0.6,
                              marginRight: 6
                            }}
                          >
                            Bs. {precioOriginal.toFixed(2)}
                          </span>
                          <span style={{ fontWeight: 700 }}>
                            Bs. {precioDesc.toFixed(2)}
                          </span>
                        </>
                      ) : (
                        <span style={{ color: 'var(--muted)' }}>
                          Bs. {precioOriginal.toFixed(2)}
                        </span>
                      )}
                    </div>

                    <button
                      className="add-to-cart-btn"
                      onClick={e => {
                        e.stopPropagation()
                        add(p, 1)
                      }}
                      aria-label="Añadir al carrito"
                      title="Añadir al carrito"
                    >
                      <Plus size={20} />
                    </button>
                  </div>
                )
              })}
              {list.length === 0 && (
                <p style={{ color: 'var(--muted)', padding: '12px 0' }}>
                  No se encontraron productos con los filtros aplicados.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Columna Derecha: Carrito */}
        <Carrito
          carrito={carrito}
          total={total}
          cliente={cliente}
          isEditing={isEditing}
          carritoRef={carritoRef}
          scrollToCarrito={scrollToCarrito}
          guardarVenta={guardarVenta}
          setCant={setCant}
          inc={inc}
          dec={dec}
          quitar={quitar}
        />
      </div>

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

        .badge-oferta{
          position:absolute;
          top:8px;
          left:8px;
          background:#e11d48;
          color:white;
          font-size:11px;
          font-weight:700;
          padding:2px 6px;
          border-radius:999px;
        }

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
        .qty-stepper .input-cantidad::-webkit-outer-spin-button,
        .qty-stepper .input-cantidad::-webkit-inner-spin-button{ -webkit-appearance: none; margin: 0; }
        .qty-stepper .input-cantidad[type="number"]{ -moz-appearance: textfield; appearance: textfield; }

        .carrito-card td.col-cant{ overflow: visible; white-space: nowrap; text-overflow: initial; }

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

function ProductoModal({ producto, onAdd, onClose }) {
  const [cantidad, setCantidad] = useState(1)
  const handleModalClick = e => e.stopPropagation()

  const precioOriginal = Number(producto.precio || 0)
  const precioDesc = producto.precio_final != null
    ? Number(producto.precio_final)
    : precioOriginal
  const descuento = producto.oferta_activa
    ? Number(producto.oferta_activa.porcentaje_descuento).toFixed(0)
    : null
  const tieneDescuento = descuento && precioDesc < precioOriginal

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={handleModalClick}>
        <button className="modal-close" onClick={onClose}>
          &times;
        </button>
        <div className="grid-2" style={{ alignItems: 'start' }}>
          <img
            src={
              producto.imagen_url ||
              `https://picsum.photos/seed/${producto.id}/600/400`
            }
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

            <p>
              <strong>Precio:</strong>{' '}
              {tieneDescuento ? (
                <>
                  <span
                    style={{
                      textDecoration: 'line-through',
                      opacity: 0.6,
                      marginRight: 6
                    }}
                  >
                    Bs. {precioOriginal.toFixed(2)}
                  </span>
                  <span>Bs. {precioDesc.toFixed(2)}</span>
                  {'  '}
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    (-{descuento}%)
                  </span>
                </>
              ) : (
                <>Bs. {precioOriginal.toFixed(2)}</>
              )}
            </p>

            <p>
              <strong>Stock disponible:</strong> {producto.stock || 0}
            </p>

            {producto.caracteristicas ? (
              <div style={{ marginTop: 16 }}>
                <strong>Características:</strong>
                <p
                  style={{
                    whiteSpace: 'pre-wrap',
                    color: 'var(--muted)',
                    marginTop: 4,
                    fontSize: '14px'
                  }}
                >
                  {producto.caracteristicas}
                </p>
              </div>
            ) : (
              <p>Este producto no tiene una descripción detallada.</p>
            )}

            <div className="btn-row" style={{ marginTop: 24 }}>
              <input
                type="number"
                min={1}
                value={cantidad}
                onChange={e =>
                  setCantidad(Math.max(1, Number(e.target.value)))
                }
                style={{ maxWidth: 80 }}
              />
              <button
                className="primary"
                onClick={() => onAdd(producto, cantidad)}
              >
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

  const handleVentaGuardada = id => {
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

      {isEditing && (
        <div className="card">
          <h2>Editando Venta</h2>
        </div>
      )}

      {tab === 'nueva' || isEditing ? (
        <FormularioNuevaVenta
          onVentaGuardada={handleVentaGuardada}
          isEditing={isEditing}
        />
      ) : (
        <ListaVentas />
      )}
    </>
  )
}
