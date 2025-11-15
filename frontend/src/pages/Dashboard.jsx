// src/pages/Dashboard.jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios.js'
import {
  ResponsiveContainer,
  ComposedChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  Line,
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
  const [predictions, setPredictions] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashboardRes, predictionsRes] = await Promise.all([
          api.get('/reportes/dashboard/'),
          api.get('/analitica/predicciones/ventas/')
        ])

        console.log('Dashboard data:', dashboardRes.data)
        console.log('Predicciones:', predictionsRes.data)

        setData(dashboardRes.data)
        setPredictions(predictionsRes.data)
      } catch (error) {
        console.error('Error al cargar los datos del dashboard', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return <div className="card">Cargando dashboard...</div>
  }

  if (!data) {
    return <div className="card">No se pudieron cargar los datos del dashboard.</div>
  }

  // ✅ Aseguramos que TODO lo que llega a los gráficos sea un array
  const ventasUltimos30 =
    Array.isArray(data.ventas_ultimos_30_dias) ? data.ventas_ultimos_30_dias : []

  const predsArray = Array.isArray(predictions) ? predictions : []

  const ventasPorCategoria =
    Array.isArray(data.ventas_por_categoria) ? data.ventas_por_categoria : []

  const ultimasVentas =
    Array.isArray(data.ultimas_ventas) ? data.ultimas_ventas : []

  // Dataset combinado para el gráfico principal
  const combinedChartData = [
    ...ventasUltimos30.map(item => ({
      ...item,
      type: 'historico'
    })),
    ...predsArray.map(pred => ({
      fecha: pred.fecha,
      total: pred.prediccion,
      type: 'prediccion'
    }))
  ]

  return (
    <div className="grid">
      {/* KPIs */}
      <div className="grid grid-kpi">
        <KpiCard
          title="Ventas de Hoy"
          value={data.kpis?.ventas_hoy ?? 0}
          prefix="Bs. "
          icon={<DollarSign />}
        />
        <KpiCard
          title="Ventas del Mes"
          value={data.kpis?.ventas_mes_actual ?? 0}
          prefix="Bs. "
          icon={<ShoppingCart />}
        />
        <KpiCard
          title="Nuevos Clientes (Mes)"
          value={data.kpis?.nuevos_clientes_mes ?? 0}
          icon={<UserPlus />}
        />
        <KpiCard
          title="Ticket Promedio (Mes)"
          value={data.kpis?.ticket_promedio ?? 0}
          prefix="Bs. "
          icon={<Ticket />}
        />
      </div>

      {/* Gráficos */}
      <div className="grid grid-2">
        <div className="card">
          <h3>Ventas y Predicciones (Próximos 30 días)</h3>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={combinedChartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="fecha"
                  tickFormatter={(date) =>
                    new Date(date).toLocaleDateString('es-BO', {
                      day: '2-digit',
                      month: '2-digit'
                    })
                  }
                />
                <YAxis />
                <Tooltip formatter={(value) => `Bs. ${Number(value).toLocaleString()}`} />
                <Legend />
                <Bar
                  dataKey="total"
                  name="Venta Histórica / Predicción"
                  fill="var(--brand)"
                />
                <Line
                  type="monotone"
                  dataKey="total"
                  name="Línea de tendencia"
                  stroke="#ec4899"
                  strokeDasharray="5 5"
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3>Ventas por Categoría (Mes)</h3>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={ventasPorCategoria}
                  dataKey="total"
                  nameKey="categoria"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {ventasPorCategoria.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `Bs. ${Number(value).toLocaleString()}`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Últimas ventas */}
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
              {ultimasVentas.map((v) => (
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
              {ultimasVentas.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '12px' }}>
                    No hay ventas recientes.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <style>{`
        .grid-kpi { grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
      `}</style>
    </div>
  )
}
