// src/pages/Dashboard.jsx
import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios.js'
import { PATHS } from '../api/paths'
import {
  ResponsiveContainer,
  ComposedChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts'
import { DollarSign, ShoppingCart, UserPlus, Ticket } from 'lucide-react'

const COLORS = ['#0ea5e9', '#6366f1', '#ec4899', '#f97316', '#10b981']

function KpiCard({ title, value, icon, prefix = '' }) {
  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ padding: '12px', background: 'var(--border)', borderRadius: '50%' }}>
          {icon}
        </div>
        <div>
          <div style={{ color: 'var(--muted)' }}>{title}</div>
          <div style={{ fontSize: '24px', fontWeight: 700 }}>
            {prefix}{value}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  // filtros
  const [period, setPeriod] = useState('30d')
  const [productId, setProductId] = useState('')
  const [categoryId, setCategoryId] = useState('')

  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])

  // series histórico + predicción
  const [historico, setHistorico] = useState([])
  const [predicciones, setPredicciones] = useState([])

  // categorías visibles en el pie
  const [visibleCategories, setVisibleCategories] = useState([])

  // ==========================
  // Carga combos (productos + categorías)
  // ==========================
  useEffect(() => {
    const fetchCombos = async () => {
      try {
        const [prodRes, catRes] = await Promise.all([
          api.get(`${PATHS.productos}?ordering=nombre&page_size=500`),
          api.get(`${PATHS.categorias}?ordering=nombre&page_size=200`)
        ])

        const prods = prodRes.data?.results || prodRes.data || []
        const cats = catRes.data?.results || catRes.data || []
        setProductos(prods)
        setCategorias(cats)
      } catch (error) {
        console.error('Error al cargar combos del dashboard', error)
      }
    }
    fetchCombos()
  }, [])

  // ==========================
  // Cargar KPIs + ventas por categoría (afectados por filtros)
  // ==========================
  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true)
      try {
        const params = { period }
        if (productId) params.product_id = productId
        if (categoryId) params.category_id = categoryId

        const res = await api.get('/reportes/dashboard/', { params })
        setData(res.data)

        const cats = res.data?.ventas_por_categoria || []
        setVisibleCategories(cats.map(c => c.categoria))
      } catch (error) {
        console.error('Error al cargar datos del dashboard', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [period, productId, categoryId])

  // ==========================
  // Cargar histórico + predicciones según filtros
  // ==========================
  useEffect(() => {
    const fetchSeries = async () => {
      try {
        const params = { period }
        if (productId) params.product_id = productId
        if (categoryId) params.category_id = categoryId

        const res = await api.get('/analitica/predicciones/ventas/', { params })
        setHistorico(res.data.historico || [])
        setPredicciones(res.data.predicciones || [])
      } catch (error) {
        console.error('Error al cargar series de ventas / predicciones', error)
      }
    }
    fetchSeries()
  }, [period, productId, categoryId])

  // ==========================
  // Preparar datos para ComposedChart (histórico + predicción)
  // ==========================
  const combinedChartData = useMemo(() => {
    const map = {}

    for (const h of historico) {
      map[h.fecha] = {
        fecha: h.fecha,
        historico: h.total || 0,
        prediccion: 0
      }
    }

    for (const p of predicciones) {
      if (!map[p.fecha]) {
        map[p.fecha] = {
          fecha: p.fecha,
          historico: 0,
          prediccion: p.prediccion || 0
        }
      } else {
        map[p.fecha].prediccion = p.prediccion || 0
      }
    }

    return Object.values(map).sort(
      (a, b) => new Date(a.fecha) - new Date(b.fecha)
    )
  }, [historico, predicciones])

  // ==========================
  // Datos filtrados para el Pie (categorías visibles)
  // ==========================
  const pieData = useMemo(() => {
    const source = data?.ventas_por_categoria || []
    if (!visibleCategories.length) return source
    return source.filter(item => visibleCategories.includes(item.categoria))
  }, [data?.ventas_por_categoria, visibleCategories])

  if (loading) return <div className="card">Cargando dashboard...</div>
  if (!data) return <div className="card">No se pudieron cargar los datos del dashboard.</div>

  return (
    <div className="grid">
      {/* Filtros superiores para gráfico + KPIs */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Filtros de ventas</h3>
        <div className="form-row" style={{ gap: 12, flexWrap: 'wrap' }}>
          <select
            value={period}
            onChange={e => setPeriod(e.target.value)}
            style={{ minWidth: 160 }}
          >
            <option value="7d">Última semana</option>
            <option value="30d">Últimos 30 días</option>
            <option value="365d">Último año</option>
          </select>

          <select
            value={categoryId}
            onChange={e => setCategoryId(e.target.value)}
            style={{ minWidth: 200 }}
          >
            <option value="">Todas las categorías</option>
            {categorias.map(c => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>

          <select
            value={productId}
            onChange={e => setProductId(e.target.value)}
            style={{ minWidth: 220 }}
          >
            <option value="">Todos los productos</option>
            {productos.map(p => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Fila de KPIs */}
      <div className="grid grid-kpi">
        <KpiCard
          title="Ventas de Hoy"
          value={data.kpis.ventas_hoy}
          prefix="Bs. "
          icon={<DollarSign />}
        />
        <KpiCard
          title="Ventas del Mes"
          value={data.kpis.ventas_mes_actual}
          prefix="Bs. "
          icon={<ShoppingCart />}
        />
        <KpiCard
          title="Nuevos Clientes (Mes)"
          value={data.kpis.nuevos_clientes_mes}
          icon={<UserPlus />}
        />
        <KpiCard
          title="Ticket Promedio (Mes)"
          value={data.kpis.ticket_promedio}
          prefix="Bs. "
          icon={<Ticket />}
        />
      </div>

      {/* Fila de Gráficos */}
      <div className="grid grid-2">
        {/* Histórico + predicción */}
        <div className="card">
          <h3>Ventas históricas y predicciones</h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={combinedChartData}
                barCategoryGap={combinedChartData.length > 25 ? 8 : 20}
                barGap={0}
              >
                <defs>
                  <linearGradient id="colorHist" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.95} />
                    <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0.7} />
                  </linearGradient>
                  <linearGradient id="colorPred" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#fb923c" stopOpacity={0.95} />
                    <stop offset="100%" stopColor="#f97316" stopOpacity={0.7} />
                  </linearGradient>
                </defs>

                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="fecha"
                  tickFormatter={(dateStr) =>
                    new Date(dateStr).toLocaleDateString('es-BO', {
                      day: '2-digit',
                      month: '2-digit'
                    })
                  }
                />
                <YAxis />
                <Tooltip
                  // etiqueta de la fecha
                  labelFormatter={(label) =>
                    new Date(label).toLocaleDateString('es-BO', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric'
                    })
                  }
                  // una fila por serie
                  formatter={(value, _name, props) => {
                    if (value == null || value === 0) return null
                    const label =
                      props.dataKey === 'historico'
                        ? 'Venta histórica'
                        : 'Predicción'
                    return [`Bs. ${Number(value).toLocaleString()}`, label]
                  }}
                />
                <Legend />

                <Bar
                  dataKey="historico"
                  name="Venta histórica"
                  barSize={combinedChartData.length > 25 ? 18 : 28}
                  radius={[4, 4, 0, 0]}   // menos redondeado
                  fill="url(#colorHist)"
                  stroke="rgba(15,23,42,0.4)"
                  strokeWidth={1}
                />
                <Bar
                  dataKey="prediccion"
                  name="Predicción"
                  barSize={combinedChartData.length > 25 ? 18 : 28}
                  radius={[4, 4, 0, 0]}   // menos redondeado
                  fill="url(#colorPred)"
                  stroke="rgba(15,23,42,0.4)"
                  strokeWidth={1}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie por categoría con checklist */}
        <div className="card">
          <h3>Ventas por Categoría (periodo)</h3>

          {/* Checklist de categorías */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
              marginBottom: '12px'
            }}
          >
            {(data.ventas_por_categoria || []).map((item) => {
              const checked = visibleCategories.includes(item.categoria)
              return (
                <label
                  key={item.categoria}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 10px',
                    borderRadius: 999,
                    border: '1px solid var(--border)',
                    background: checked ? 'rgba(56,189,248,0.08)' : 'transparent',
                    cursor: 'pointer',
                    fontSize: 13
                  }}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => {
                      setVisibleCategories(prev =>
                        checked
                          ? prev.filter(c => c !== item.categoria)
                          : [...prev, item.categoria]
                      )
                    }}
                    style={{ accentColor: '#0ea5e9' }}
                  />
                  <span>{item.categoria}</span>
                </label>
              )
            })}
          </div>

          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="total"
                  nameKey="categoria"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name) =>
                    [`Bs. ${Number(value || 0).toLocaleString()}`, name]
                  }
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Fila de Últimas Ventas */}
      <div className="card">
        <h3>Últimas Ventas</h3>
        <div className="table-responsive">
          <table className="table-nowrap">
            <thead>
              <tr>
                <th>Folio</th>
                <th>Cliente</th>
                <th>Total</th>
                <th>Fecha</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.ultimas_ventas.map(v => (
                <tr key={v.id}>
                  <td>{v.folio}</td>
                  <td>{v.cliente}</td>
                  <td>Bs. {v.total}</td>
                  <td>{v.fecha}</td>
                  <td>
                    <Link to={`/ventas/${v.id}`}>Ver Detalle</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Estilo para el grid de KPIs */}
      <style>{`
        .grid-kpi {
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        }
      `}</style>
    </div>
  )
}
