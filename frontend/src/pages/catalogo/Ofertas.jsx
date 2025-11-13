// src/pages/catalogo/Ofertas.jsx
import { useEffect, useMemo, useState } from 'react'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'

export default function Ofertas() {
  const [productos, setProductos] = useState([])
  const [buscar, setBuscar] = useState('')
  const [filtroCategoria, setFiltroCategoria] = useState('')
  const [filtroMarca, setFiltroMarca] = useState('')
  const [categorias, setCategorias] = useState([])
  const [marcas, setMarcas] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      try {
        const p = await api.get(`${PATHS.productos}?ordering=nombre`)
        const data = p.data?.results || p.data || []
        // Solo productos con oferta activa
        setProductos(data.filter((x) => !!x.oferta_activa))
      } catch {
        setProductos([])
      }

      try {
        const cat = await api.get(`${PATHS.categorias}?ordering=nombre`)
        setCategorias(cat.data?.results || cat.data || [])
      } catch {
        setCategorias([])
      }

      try {
        const m = await api.get(`${PATHS.marcas}?ordering=nombre`)
        setMarcas(m.data?.results || m.data || [])
      } catch {
        setMarcas([])
      }

      setLoading(false)
    })()
  }, [])

  const list = useMemo(() => {
    let data = productos

    if (filtroCategoria) {
      data = data.filter((p) => String(p.categoria) === String(filtroCategoria))
    }
    if (filtroMarca) {
      data = data.filter((p) => String(p.marca) === String(filtroMarca))
    }

    const q = buscar.trim().toLowerCase()
    if (q) {
      data = data.filter(
        (p) =>
          (p.nombre || '').toLowerCase().includes(q) ||
          (p.modelo || '').toLowerCase().includes(q) ||
          (p.codigo || '').toLowerCase().includes(q)
      )
    }
    return data
  }, [productos, buscar, filtroCategoria, filtroMarca])

  if (loading) return <div className="card">Cargando ofertas...</div>

  return (
    <>
      <div className="card">
        <h2>Ofertas vigentes</h2>
        <p style={{ color: 'var(--muted)', fontSize: 14 }}>
          Productos que actualmente tienen un descuento aplicado.
        </p>
      </div>

      <div className="card">
        <div className="form-row" style={{ flexWrap: 'wrap', gap: 8 }}>
          <input
            placeholder="Buscar producto en ofertas…"
            value={buscar}
            onChange={(e) => setBuscar(e.target.value)}
            style={{ flex: '2 1 220px' }}
          />
          <select
            value={filtroCategoria}
            onChange={(e) => setFiltroCategoria(e.target.value)}
            style={{ flex: '1 1 160px' }}
          >
            <option value="">Todas las categorías</option>
            {categorias.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
          <select
            value={filtroMarca}
            onChange={(e) => setFiltroMarca(e.target.value)}
            style={{ flex: '1 1 160px' }}
          >
            <option value="">Todas las marcas</option>
            {marcas.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        <div className="cards">
          {list.map((p) => {
            const precioOriginal = Number(p.precio || 0)
            const precioDesc =
              p.precio_final != null ? Number(p.precio_final) : precioOriginal
            const descuento = p.oferta_activa
              ? Number(p.oferta_activa.porcentaje_descuento).toFixed(0)
              : null

            return (
              <div key={p.id} className="card-item">
                <img
                  src={
                    p.imagen_url || `https://picsum.photos/seed/${p.id}/600/400`
                  }
                  alt={p.nombre}
                />
                {descuento && (
                  <span className="badge-oferta">-{descuento}%</span>
                )}
                <div style={{ fontWeight: 700 }}>{p.nombre}</div>
                <div style={{ fontSize: 13, color: 'var(--muted)' }}>
                  {p.marca_nombre || 'Sin marca'} · {p.categoria_nombre}
                </div>
                <div style={{ marginTop: 4 }}>
                  {precioDesc < precioOriginal ? (
                    <>
                      <span
                        style={{
                          textDecoration: 'line-through',
                          opacity: 0.6,
                          marginRight: 6,
                        }}
                      >
                        Bs. {precioOriginal.toFixed(2)}
                      </span>
                      <span style={{ fontWeight: 700 }}>
                        Bs. {precioDesc.toFixed(2)}
                      </span>
                    </>
                  ) : (
                    <span>Bs. {precioOriginal.toFixed(2)}</span>
                  )}
                </div>
              </div>
            )
          })}
          {list.length === 0 && (
            <p style={{ color: 'var(--muted)', padding: '12px 0' }}>
              No hay productos en oferta con los filtros aplicados.
            </p>
          )}
        </div>
      </div>

      <style>{`
        .card-item { position:relative; }
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
      `}</style>
    </>
  )
}
