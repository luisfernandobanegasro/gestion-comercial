// src/pages/catalogo/OfertasAdmin.jsx
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'

const emptyForm = {
  id: null,
  nombre: '',
  porcentaje_descuento: '',
  fecha_inicio: '',
  fecha_fin: '',
  activa: true,
  marcas: [],
  categorias: [],
  productos_especificos: [],
}

export default function OfertasAdmin() {
  const navigate = useNavigate()

  const [ofertas, setOfertas] = useState([])
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [soloVigentes, setSoloVigentes] = useState(true)

  const [form, setForm] = useState(emptyForm)
  const [categorias, setCategorias] = useState([])
  const [marcas, setMarcas] = useState([])
  const [productos, setProductos] = useState([])

  const [saving, setSaving] = useState(false)
  const [buscaProducto, setBuscaProducto] = useState('')

  // ---------- Carga de combos ----------
  useEffect(() => {
    ;(async () => {
      try {
        const [catRes, marRes, prodRes] = await Promise.all([
          api.get(`${PATHS.categorias}?ordering=nombre`),
          api.get(`${PATHS.marcas}?ordering=nombre`),
          api.get(`${PATHS.productos}?ordering=nombre`),
        ])
        setCategorias(catRes.data?.results || catRes.data || [])
        setMarcas(marRes.data?.results || marRes.data || [])
        setProductos(prodRes.data?.results || prodRes.data || [])
      } catch {
        setCategorias([])
        setMarcas([])
        setProductos([])
      }
    })()
  }, [])

  // ---------- Carga de ofertas ----------
  const loadData = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (busqueda) params.append('search', busqueda)
      if (soloVigentes) params.append('vigente', 'true')

      const res = await api.get(`${PATHS.ofertas.root}?${params.toString()}`)
      setOfertas(res.data?.results || res.data || [])
    } catch {
      setOfertas([])
    }
    setLoading(false)
  }

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busqueda, soloVigentes])

  // ---------- Helpers selección ----------
  const toggleIdInArray = (arr, id) =>
    arr.includes(id) ? arr.filter(x => x !== id) : [...arr, id]

  const toggleCategoria = (id) =>
    setForm(prev => ({ ...prev, categorias: toggleIdInArray(prev.categorias, id) }))

  const toggleMarca = (id) =>
    setForm(prev => ({ ...prev, marcas: toggleIdInArray(prev.marcas, id) }))

  const toggleProducto = (id) =>
    setForm(prev => ({
      ...prev,
      productos_especificos: toggleIdInArray(prev.productos_especificos, id),
    }))

  const selectedProductos = useMemo(
    () =>
      form.productos_especificos
        .map(id => productos.find(p => p.id === id))
        .filter(Boolean),
    [form.productos_especificos, productos]
  )

  const filteredProductos = useMemo(() => {
    const q = buscaProducto.trim().toLowerCase()
    let data = productos.filter(p => !form.productos_especificos.includes(p.id))
    if (q) {
      data = data.filter(
        p =>
          (p.nombre || '').toLowerCase().includes(q) ||
          (p.codigo || '').toLowerCase().includes(q) ||
          (p.modelo || '').toLowerCase().includes(q)
      )
    }
    return data.slice(0, 30) // no saturar la lista
  }, [productos, buscaProducto, form.productos_especificos])

  // ---------- CRUD ----------
  const handleEdit = (oferta) => {
    setForm({
      id: oferta.id,
      nombre: oferta.nombre,
      porcentaje_descuento: oferta.porcentaje_descuento,
      fecha_inicio: oferta.fecha_inicio.slice(0, 16), // yyyy-MM-ddTHH:mm
      fecha_fin: oferta.fecha_fin.slice(0, 16),
      activa: oferta.activa,
      marcas: oferta.marcas || [],
      categorias: oferta.categorias || [],
      productos_especificos: oferta.productos_especificos || [],
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar esta oferta?')) return
    await api.delete(`${PATHS.ofertas.root}${id}/`)
    loadData()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    const payload = {
      nombre: form.nombre,
      porcentaje_descuento: form.porcentaje_descuento,
      fecha_inicio: form.fecha_inicio,
      fecha_fin: form.fecha_fin,
      activa: form.activa,
      marcas: form.marcas,
      categorias: form.categorias,
      productos_especificos: form.productos_especificos,
    }
    try {
      if (form.id) {
        await api.put(`${PATHS.ofertas.root}${form.id}/`, payload)
      } else {
        await api.post(PATHS.ofertas.root, payload)
      }
      setForm(emptyForm)
      setBuscaProducto('')
      await loadData()
      alert('Oferta guardada correctamente.')
    } catch (err) {
      console.error(err.response?.data || err)
      alert('Error al guardar la oferta.')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setForm(emptyForm)
    setBuscaProducto('')
  }

  // ---------- UI ----------
  return (
    <>
      <div className="card">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 8,
            flexWrap: 'wrap',
          }}
        >
          <div>
            <h2>Gestión de ofertas</h2>
            <p style={{ fontSize: 14, color: 'var(--muted)' }}>
              Ponle un <strong>nombre descriptivo</strong> (ej. &quot;Ofertas Hogar
              Noviembre&quot;), indica el % de descuento y marca los ámbitos
              donde aplica.
            </p>
          </div>

          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate('/ofertas/vigentes')}
          >
            Ver productos en oferta
          </button>
        </div>
      </div>

      {/* Filtros de la lista */}
      <div className="card">
        <div
          className="form-row"
          style={{ alignItems: 'center', gap: 8, flexWrap: 'wrap' }}
        >
          <input
            placeholder="Buscar por nombre de oferta…"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            style={{ flex: '2 1 220px' }}
          />
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              fontSize: 13,
            }}
          >
            <input
              type="checkbox"
              checked={soloVigentes}
              onChange={(e) => setSoloVigentes(e.target.checked)}
            />
            Solo vigentes
          </label>
          <button type="button" className="btn-secondary" onClick={loadData}>
            Recargar
          </button>
        </div>
      </div>

      {/* Lista de ofertas */}
      <div className="card">
        <h3>Ofertas registradas</h3>
        {loading ? (
          <p>Cargando...</p>
        ) : ofertas.length === 0 ? (
          <p style={{ color: 'var(--muted)' }}>No hay ofertas registradas.</p>
        ) : (
          <div className="table-responsive">
            <table className="table-nowrap">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>% Desc.</th>
                  <th>Vigencia</th>
                  <th>Estado</th>
                  <th>Ámbitos</th>
                  <th className="col-actions" />
                </tr>
              </thead>
              <tbody>
                {ofertas.map((o) => (
                  <tr key={o.id}>
                    <td>{o.nombre}</td>
                    <td>{Number(o.porcentaje_descuento).toFixed(2)}%</td>
                    <td>
                      {new Date(o.fecha_inicio).toLocaleString()}
                      <br />
                      <span style={{ fontSize: 12, opacity: 0.7 }}>
                        hasta {new Date(o.fecha_fin).toLocaleString()}
                      </span>
                    </td>
                    <td>{o.activa ? 'Activa' : 'Inactiva'}</td>
                    <td style={{ fontSize: 12 }}>
                      {o.categorias_nombres?.length ? (
                        <div>
                          <strong>Categorías:</strong>{' '}
                          {o.categorias_nombres.join(', ')}
                        </div>
                      ) : null}
                      {o.marcas_nombres?.length ? (
                        <div>
                          <strong>Marcas:</strong>{' '}
                          {o.marcas_nombres.join(', ')}
                        </div>
                      ) : null}
                      {o.productos_nombres?.length ? (
                        <div>
                          <strong>Productos:</strong>{' '}
                          {o.productos_nombres.join(', ')}
                        </div>
                      ) : null}
                    </td>
                    <td className="col-actions">
                      <button
                        className="btn-icon"
                        onClick={() => handleEdit(o)}
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon"
                        onClick={() => handleDelete(o.id)}
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Formulario crear/editar */}
      <div className="card">
        <h3>{form.id ? 'Editar oferta' : 'Nueva oferta'}</h3>

        <form className="ofertas-grid" onSubmit={handleSubmit}>
          {/* Columna izquierda: datos básicos */}
          <div>
            <div className="form-row" style={{ gap: 12, flexWrap: 'wrap' }}>
              <div style={{ flex: '2 1 200px' }}>
                <label className="form-label">Nombre de la oferta</label>
                <input
                  required
                  value={form.nombre}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, nombre: e.target.value }))
                  }
                  placeholder="Ej: Ofertas Hogar Noviembre"
                />
              </div>

              <div style={{ flex: '1 1 120px' }}>
                <label className="form-label">% Descuento</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  value={form.porcentaje_descuento}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      porcentaje_descuento: e.target.value,
                    }))
                  }
                />
              </div>
            </div>

            <p style={{ fontSize: 12, color: 'var(--muted)', marginTop: 4 }}>
              Marca uno o varios ámbitos. Ejemplo: solo categoría &quot;Hogar&quot; ➜
              todos los productos de Hogar entran en la oferta.
            </p>

            <div className="form-row" style={{ marginTop: 12, gap: 12 }}>
              <div style={{ flex: 1 }}>
                <label className="form-label">Fecha inicio</label>
                <input
                  type="datetime-local"
                  required
                  value={form.fecha_inicio}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      fecha_inicio: e.target.value,
                    }))
                  }
                />
              </div>
              <div style={{ flex: 1 }}>
                <label className="form-label">Fecha fin</label>
                <input
                  type="datetime-local"
                  required
                  value={form.fecha_fin}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      fecha_fin: e.target.value,
                    }))
                  }
                />
              </div>
            </div>

            <label
              style={{
                marginTop: 8,
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              <input
                type="checkbox"
                checked={form.activa}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, activa: e.target.checked }))
                }
              />
              Activa
            </label>
          </div>

          {/* Columna derecha: ámbitos */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Categorías */}
            <div>
              <div className="ofertas-label-row">
                <span className="form-label">Categorías</span>
              </div>
              <div className="pill-grid">
                {categorias.map((c) => {
                  const checked = form.categorias.includes(c.id)
                  return (
                    <label
                      key={c.id}
                      className={`pill ${checked ? 'pill-selected' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleCategoria(c.id)}
                      />
                      {c.nombre}
                    </label>
                  )
                })}
                {categorias.length === 0 && (
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    No hay categorías registradas.
                  </span>
                )}
              </div>
            </div>

            {/* Marcas */}
            <div>
              <div className="ofertas-label-row">
                <span className="form-label">Marcas</span>
              </div>
              <div className="pill-grid">
                {marcas.map((m) => {
                  const checked = form.marcas.includes(m.id)
                  return (
                    <label
                      key={m.id}
                      className={`pill ${checked ? 'pill-selected' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleMarca(m.id)}
                      />
                      {m.nombre}
                    </label>
                  )
                })}
                {marcas.length === 0 && (
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    No hay marcas registradas.
                  </span>
                )}
              </div>
            </div>

            {/* Productos específicos */}
            <div>
              <div className="ofertas-label-row">
                <span className="form-label">Productos específicos</span>
                <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                  (opcional)
                </span>
              </div>

              <input
                placeholder="Buscar producto por nombre o código…"
                value={buscaProducto}
                onChange={(e) => setBuscaProducto(e.target.value)}
                style={{ marginBottom: 8, width: '100%' }}
              />

              <div className="pill-list-scroll">
                {filteredProductos.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    className="pill pill-ghost"
                    onClick={() => toggleProducto(p.id)}
                  >
                    {p.nombre} {!!p.codigo && `(${p.codigo})`}
                  </button>
                ))}
                {filteredProductos.length === 0 && (
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    No hay productos que coincidan con la búsqueda.
                  </span>
                )}
              </div>

              {selectedProductos.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <span
                    style={{
                      fontSize: 12,
                      color: 'var(--muted)',
                      display: 'block',
                      marginBottom: 4,
                    }}
                  >
                    Productos seleccionados:
                  </span>
                  <div className="pill-grid">
                    {selectedProductos.map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        className="pill pill-selected"
                        onClick={() => toggleProducto(p.id)}
                      >
                        {p.nombre} {!!p.codigo && `(${p.codigo})`} ✕
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div style={{ gridColumn: '1 / -1', marginTop: 12 }}>
            <div className="btn-row">
              <button type="submit" className="primary" disabled={saving}>
                {saving
                  ? 'Guardando…'
                  : form.id
                  ? 'Actualizar oferta'
                  : 'Crear oferta'}
              </button>
              {form.id && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCancel}
                >
                  Cancelar edición
                </button>
              )}
            </div>
          </div>
        </form>
      </div>

      {/* Estilos específicos de OfertasAdmin */}
      <style>{`
        .ofertas-grid{
          display:flex;
          flex-direction:column;
          gap:16px;
        }
        @media (min-width: 960px){
          .ofertas-grid{
            display:grid;
            grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);
            align-items:flex-start;
          }
        }

        .ofertas-label-row{
          display:flex;
          align-items:baseline;
          justify-content:space-between;
          gap:8px;
          margin-bottom:4px;
        }

        .pill-grid{
          display:flex;
          flex-wrap:wrap;
          gap:6px;
        }

        .pill{
          border-radius:999px;
          padding:4px 10px;
          border:1px solid var(--border);
          font-size:12px;
          background:transparent;
          color:var(--text);
          display:inline-flex;
          align-items:center;
          gap:6px;
          cursor:pointer;
        }
        .pill input{
          margin:0;
        }
        .pill-selected{
          background:var(--primary);
          color:var(--primary-ink);
          border-color:var(--primary);
        }
        .pill-ghost{
          background:rgba(148,163,184,0.08);
        }
        .pill-ghost:hover{
          background:rgba(148,163,184,0.18);
        }

        .pill-list-scroll{
          max-height:160px;
          overflow:auto;
          padding:4px 0;
          border-radius:8px;
          border:1px solid var(--border);
          padding-inline:6px;
          display:flex;
          flex-wrap:wrap;
          gap:6px;
        }
      `}</style>
    </>
  )
}
