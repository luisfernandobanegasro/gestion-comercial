import { useEffect, useState } from 'react'
import api from '../api/axios'
import { PATHS } from '../api/paths'
import { saveAs } from 'file-saver';

export default function Bitacora(){
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ desde: '', hasta: '', usuario: '', modulo: '', q: '' });
  // Estados para poblar los dropdowns de los filtros
  const [usuarios, setUsuarios] = useState([]);
  const [modulos, setModulos] = useState([]);

  // Carga los datos para los filtros una sola vez al montar el componente
  useEffect(() => {
    const loadFilterData = async () => {
      try {
        // Usamos una URL sin paginación para obtener todos los usuarios para el filtro
        const resUsuarios = await api.get(`${PATHS.usuarios}?page_size=1000`);
        setUsuarios(resUsuarios.data?.results || resUsuarios.data || []);
        // Para los módulos, una lista estática es más eficiente y predecible.
        setModulos(['cuentas', 'catalogo', 'clientes', 'ventas', 'pagos', 'reportes', 'configuracion', 'auditoria']);
      } catch (error) {
        console.error("Error al cargar datos para filtros", error);
      }
    };
    loadFilterData();
  }, []);

  // Carga los registros de la bitácora cada vez que los filtros cambian
  useEffect(()=>{
    const loadAuditData = async () => {
      setLoading(true);
    try{
      const params = new URLSearchParams(filters).toString();
      const r = await api.get(`${PATHS.auditoria}?ordering=-creado_en&${params}`)
      setItems(r.data || []) // La API ahora devuelve un array directamente
    } catch { setItems([]) }
    finally { setLoading(false); }
    };
    loadAuditData();
  }, [filters])

  const handleExport = async (format) => {
    try {
      const params = new URLSearchParams(filters).toString();
      const url = `${PATHS.auditoria}exportar-${format}/?${params}`;
      const response = await api.get(url, { responseType: 'blob' });
      const fileExtension = format === 'excel' ? 'xlsx' : format;
      saveAs(response.data, `auditoria.${fileExtension}`);
    } catch (error) {
      console.error(`Error al exportar a ${format}:`, error);
      alert(`No se pudo generar el archivo ${format}.`);
    }
  };

  return (
    <div className="grid">
      <div className="card">
        <h3 style={{margin:0}}>Bitácora de Auditoría</h3>
        
        {/* Usamos la clase 'form-row' que ya es responsive */}
        <div className="form-row" style={{alignItems: 'flex-end', marginTop: '16px'}}>
          <input type="datetime-local" value={filters.desde} onChange={e => setFilters({...filters, desde: e.target.value})} title="Desde" />
          <input type="datetime-local" value={filters.hasta} onChange={e => setFilters({...filters, hasta: e.target.value})} title="Hasta" />
          <select value={filters.usuario} onChange={e => setFilters({...filters, usuario: e.target.value})}>
            <option value="">Todos los usuarios</option>
            {usuarios.map(u => <option key={u.id} value={u.username}>{u.username}</option>)}
          </select>
          <select value={filters.modulo} onChange={e => setFilters({...filters, modulo: e.target.value})}>
            <option value="">Todos los módulos</option>
            {modulos.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <input type="text" value={filters.q} onChange={e => setFilters({...filters, q: e.target.value})} placeholder="Buscar por ruta, acción..." />
        </div>

        {/* La clase .btn-row ya es responsive y apila los botones en móvil */}
        <div className="btn-row" style={{marginTop: '16px'}}>
          <button onClick={() => handleExport('excel')}>Descargar Excel</button>
          <button onClick={() => handleExport('pdf')}>Descargar PDF</button>
        </div>
        <div className="table-responsive" style={{marginTop:10}}>
          <table className="table-nowrap">
            <thead><tr><th>Fecha y Hora</th><th>Usuario</th><th>IP</th><th>Módulo</th><th>Acción</th><th>Ruta</th><th>Método</th><th>Estado</th></tr></thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center' }}>Cargando...</td>
                </tr>
              ) : items.length > 0 ? items.map(r=>(
                <tr key={r.id}>
                  <td>{r.fecha_hora}</td>
                  <td>{r.usuario_username}</td>
                  <td>{r.ip}</td>
                  <td>{r.modulo}</td>
                  <td>{r.accion}</td>
                  <td>{r.ruta}</td>
                  <td>{r.metodo}</td>
                  <td>{r.estado}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center' }}>No se encontraron registros.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
