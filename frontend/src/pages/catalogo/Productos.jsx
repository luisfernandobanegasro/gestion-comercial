import { useEffect, useState, useCallback } from 'react'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'
import ImageUploader from '../../components/ImageUploader'

// Hook personalizado para manejar el estado del formulario
const useForm = (initialState = {}) => {
  const [form, setForm] = useState(initialState);
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };
  const setFormField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };
  return [form, setForm, handleFormChange, setFormField];
};

function ProductTable({ items, onEdit, onDelete }) {
  return (
    <div className="table-responsive">
      <table className="table-nowrap">
        <thead><tr><th></th><th>Nombre</th><th>Modelo</th><th>Categoría</th><th>Marca</th><th>Precio</th><th>Stock</th><th></th></tr></thead>
        <tbody>
          {items.map(p => (
            <tr key={p.id}>
              <td>{p.imagen_url && <img src={p.imagen_url} alt={p.nombre} style={{ width: 40, height: 40, objectFit: 'cover' }} />}</td>
              <td>{p.nombre}</td>
              <td>{p.modelo}</td>
              <td>{p.categoria_nombre}</td>
              <td>{p.marca_nombre}</td>
              <td>{Number(p.precio || 0).toFixed(2)}</td>
              <td>{p.stock}</td>
              <td>
                <div className="btn-row">
                  <button onClick={() => onEdit({ ...p, imagen: null })}>Editar</button>
                  <button onClick={() => onDelete(p.id)}>Eliminar</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ProductForm({ form, setForm, save, categorias, marcas, handleFormChange, setFormField }) {
  return (
    <div className="card">
      <h3>{form.id ? 'Editar' : 'Nuevo'} producto</h3>
      <form className="grid" onSubmit={save}>
        <input name="nombre" placeholder="Nombre" value={form.nombre || ''} onChange={handleFormChange} required />
        <input name="modelo" placeholder="Modelo (opcional)" value={form.modelo || ''} onChange={handleFormChange} />
        <select name="categoria" value={form.categoria || ''} onChange={handleFormChange} required>
          <option value="">-- Selecciona Categoría --</option>
          {categorias.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
        </select>
        <select name="marca" value={form.marca || ''} onChange={handleFormChange}>
          <option value="">-- Selecciona Marca (opcional) --</option>
          {marcas.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
        </select>
        <input name="precio" type="number" step="0.01" placeholder="Precio" value={form.precio || ''} onChange={handleFormChange} required />
        <input name="stock" type="number" placeholder="Stock" value={form.stock || ''} onChange={handleFormChange} required />
        <textarea name="caracteristicas" placeholder="Características (opcional, una por línea)" value={form.caracteristicas || ''} onChange={handleFormChange} rows="4"></textarea>
        <ImageUploader onFileChange={file => setFormField('imagen', file)} initialImage={form.imagen_url} />
        <button className="primary">{form.id ? 'Actualizar' : 'Guardar'}</button>
        <button type="button" onClick={() => setForm(null)}>Cancelar</button>
      </form>
    </div>
  );
}

export default function Productos() {
  const [items, setItems] = useState([])
  const [categorias, setCategorias] = useState([])
  const [marcas, setMarcas] = useState([])
  const [form, setForm, handleFormChange, setFormField] = useForm(null);

  const load = useCallback(async () => {
    try {
      // Cargar todo en paralelo para mayor velocidad
      const [resProductos, resCategorias, resMarcas] = await Promise.all([
        api.get(`${PATHS.productos}?ordering=nombre`),
        api.get(`${PATHS.categorias}?ordering=nombre`),
        api.get(`${PATHS.marcas}?ordering=nombre`),
      ]);
      setItems(resProductos.data?.results || resProductos.data || []);
      setCategorias(resCategorias.data?.results || resCategorias.data || []);
      setMarcas(resMarcas.data?.results || resMarcas.data || []);
    } catch (error) {
      console.error("Error al cargar datos de productos:", error);
    }
  }, []);

  useEffect(() => { load() }, [load]);

  const save = useCallback(async (e) => {
    e.preventDefault();
    if (!form) return;

    const formData = new FormData();
    Object.keys(form).forEach(key => {
      if (key !== 'imagen' && (form[key] === null || form[key] === undefined)) return;
      formData.append(key, form[key]);
    });

    const config = { headers: { 'Content-Type': 'multipart/form-data' } };

    try {
      if (form.id) {
        await api.patch(`${PATHS.productos}${form.id}/`, formData, config);
      } else {
        await api.post(PATHS.productos, formData, config);
      }
      setForm(null); // Ocultar formulario
      load();
    } catch (error) {
      console.error("Error al guardar el producto:", error);
      alert("Hubo un error al guardar el producto.");
    }
  }, [form, load, setForm]);

  const del = useCallback(async (id) => {
    if (window.confirm('¿Eliminar producto?')) {
      try {
        await api.delete(`${PATHS.productos}${id}/`);
        load();
      } catch (error) {
        console.error("Error al eliminar el producto:", error);
        alert("Hubo un error al eliminar el producto. Es posible que esté asociado a una venta.");
      }
    }
  }, [load]);

  return (
    <div className="grid">
      <div className="card">
        <h3>Productos</h3>
        <button onClick={() => setForm({})}>+ Nuevo Producto</button>
        <ProductTable items={items} onEdit={setForm} onDelete={del} />
      </div>

      {form && <ProductForm form={form} setForm={setForm} save={save} categorias={categorias} marcas={marcas} handleFormChange={handleFormChange} setFormField={setFormField} />}
    </div>
  )
}
