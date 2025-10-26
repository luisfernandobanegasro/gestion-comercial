import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axios';
import { PATHS } from '../../api/paths';

export default function Marcas() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(null); // Usar null para mostrar/ocultar

  const load = useCallback(async () => {
    try {
      const res = await api.get(`${PATHS.marcas}?ordering=nombre`);
      setItems(res.data?.results || res.data || []);
    } catch (error) {
      console.error("Error al cargar marcas:", error);
      setItems([]);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const save = async (e) => {
    e.preventDefault();
    const payload = { nombre: form.nombre };

    if (form.id) {
      await api.patch(`${PATHS.marcas}${form.id}/`, payload);
    } else {
      await api.post(PATHS.marcas, payload);
    }
    setForm(null); // Ocultar formulario
    load();
  };

  const del = async (id) => {
    if (window.confirm('¿Eliminar marca? Esto podría fallar si está en uso.')) {
      await api.delete(`${PATHS.marcas}${id}/`);
      load();
    }
  };

  return (
    <div className="grid">
      <div className="card">
        <h3>Marcas</h3>
        <button onClick={() => setForm({})}>+ Nueva Marca</button>
        <div className="table-responsive">
          <table className="table-nowrap">
            <thead><tr><th>Nombre</th><th></th></tr></thead>
            <tbody>
              {items.map(m => (
                <tr key={m.id}><td>{m.nombre}</td><td><div className="btn-row"><button onClick={() => setForm(m)}>Editar</button><button onClick={() => del(m.id)}>Eliminar</button></div></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {form && <div className="card"><h3>{form.id ? 'Editar' : 'Nueva'} Marca</h3><form className="grid" onSubmit={save}><input placeholder="Nombre" value={form.nombre || ''} onChange={e => setForm({ ...form, nombre: e.target.value })} required /><button className="primary">{form.id ? 'Actualizar' : 'Guardar'}</button><button type="button" onClick={() => setForm(null)}>Cancelar</button></form></div>}
    </div>
  );
}