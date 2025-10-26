import { useEffect, useState, useCallback } from 'react';
import api from '../../api/axios';
import { PATHS } from '../../api/paths';

export default function Categorias() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(null); // Usar null para mostrar/ocultar

  const load = useCallback(async () => {
    try {
      const res = await api.get(`${PATHS.categorias}?ordering=nombre`);
      setItems(res.data?.results || res.data || []);
    } catch (error) {
      console.error("Error al cargar categorías:", error);
      setItems([]);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const save = async (e) => {
    e.preventDefault();
    const payload = { nombre: form.nombre, descripcion: form.descripcion || '' };

    if (form.id) {
      await api.patch(`${PATHS.categorias}${form.id}/`, payload);
    } else {
      await api.post(PATHS.categorias, payload);
    }
    setForm(null); // Ocultar formulario
    load();
  };

  const del = async (id) => {
    if (window.confirm('¿Eliminar categoría? Esto podría fallar si está en uso.')) {
      await api.delete(`${PATHS.categorias}${id}/`);
      load();
    }
  };

  return (
    <div className="grid">
      <div className="card">
        <h3>Categorías</h3>
        <button onClick={() => setForm({})}>+ Nueva Categoría</button>
        <div className="table-responsive">
          <table className="table-nowrap">
            <thead><tr><th>Nombre</th><th>Descripción</th><th></th></tr></thead>
            <tbody>
              {items.map(c => (
                <tr key={c.id}><td>{c.nombre}</td><td>{c.descripcion}</td><td><div className="btn-row"><button onClick={() => setForm(c)}>Editar</button><button onClick={() => del(c.id)}>Eliminar</button></div></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {form && <div className="card"><h3>{form.id ? 'Editar' : 'Nueva'} Categoría</h3><form className="grid" onSubmit={save}><input placeholder="Nombre" value={form.nombre || ''} onChange={e => setForm({ ...form, nombre: e.target.value })} required /><input placeholder="Descripción (opcional)" value={form.descripcion || ''} onChange={e => setForm({ ...form, descripcion: e.target.value })} /><button className="primary">{form.id ? 'Actualizar' : 'Guardar'}</button><button type="button" onClick={() => setForm(null)}>Cancelar</button></form></div>}
    </div>
  );
}