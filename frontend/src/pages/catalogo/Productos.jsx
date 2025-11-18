// src/pages/catalogo/Productos.jsx
import { useEffect, useState, useCallback } from 'react'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'
import ImageUploader from '../../components/ImageUploader'

const useForm = (initialState = null) => {
  const [form, setForm] = useState(initialState)
  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }
  const setFormField = (field, value) =>
    setForm(prev => ({ ...prev, [field]: value }))
  return [form, setForm, handleFormChange, setFormField]
}

function ProductTable({ items, onEdit, onDelete }) {
  return (
    <div className="table-responsive">
      <table className="table-xs products-table">
        <colgroup>
          {[
            <col key="img" className="col-img" />,
            <col key="nombre" />,
            <col key="modelo" />,
            <col key="cat" />,
            <col key="marca" />,
            <col key="precio" />,
            <col key="stock" />,
            <col key="activo" />,
            <col key="acc" className="col-actions" />,
          ]}
        </colgroup>
        <thead>
          <tr>
            <th></th>
            <th>Nombre</th>
            <th>Modelo</th>
            <th>Categoría</th>
            <th>Marca</th>
            <th className="col-num">Precio</th>
            <th className="col-num">Stock</th>
            <th>Activo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map(p => (
            <tr key={p.id}>
              <td>
                {p.imagen_url && (
                  <img
                    src={p.imagen_url}
                    alt={p.nombre}
                    style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 8 }}
                  />
                )}
              </td>
              <td className="col-text">{p.nombre}</td>
              <td className="col-text">{p.modelo}</td>
              <td className="col-text">{p.categoria_nombre}</td>
              <td className="col-text">{p.marca_nombre}</td>
              <td className="col-num">{Number(p.precio || 0).toFixed(2)}</td>
              <td className="col-num">{p.stock}</td>
              <td className="col-text">
                {p.activo ? '✔️' : '❌'}
              </td>
              <td className="col-actions">
                <div className="btn-row">
                  <button onClick={() => onEdit({ ...p, imagen: null })}>
                    Editar
                  </button>
                  <button onClick={() => onDelete(p.id)}>Eliminar</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ProductForm({
  form,
  setForm,
  save,
  categorias,
  marcas,
  handleFormChange,
  setFormField,
}) {
  return (
    <div className="card">
      <h3>{form.id ? 'Editar' : 'Nuevo'} producto</h3>
      <form className="grid" onSubmit={save}>
        <input
          name="nombre"
          placeholder="Nombre"
          value={form.nombre || ''}
          onChange={handleFormChange}
          required
        />
        <input
          name="modelo"
          placeholder="Modelo (opcional)"
          value={form.modelo || ''}
          onChange={handleFormChange}
        />

        <select
          name="categoria"
          value={form.categoria || ''}
          onChange={handleFormChange}
          required
        >
          <option value="">-- Selecciona Categoría --</option>
          {categorias.map(c => (
            <option key={c.id} value={c.id}>
              {c.nombre}
            </option>
          ))}
        </select>

        <select
          name="marca"
          value={form.marca || ''}
          onChange={handleFormChange}
        >
          <option value="">-- Selecciona Marca (opcional) --</option>
          {marcas.map(m => (
            <option key={m.id} value={m.id}>
              {m.nombre}
            </option>
          ))}
        </select>

        <input
          name="precio"
          type="number"
          step="0.01"
          placeholder="Precio"
          value={form.precio || ''}
          onChange={handleFormChange}
          required
        />
        <input
          name="stock"
          type="number"
          placeholder="Stock"
          value={form.stock || ''}
          onChange={handleFormChange}
          required
        />

        <textarea
          name="caracteristicas"
          placeholder="Características (opcional, una por línea)"
          value={form.caracteristicas || ''}
          onChange={handleFormChange}
          rows="4"
        ></textarea>

        {/* Checkbox ACTIVO */}
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            marginTop: 4,
            fontSize: 14,
          }}
        >
          <input
            type="checkbox"
            name="activo"
            checked={!!form.activo}
            onChange={handleFormChange}
          />
          Producto activo (se puede vender)
        </label>

        <ImageUploader
          onFileChange={file => setFormField('imagen', file)}
          initialImage={form.imagen_url}
        />

        <div className="btn-row">
          <button className="primary">
            {form.id ? 'Actualizar' : 'Guardar'}
          </button>
          <button type="button" onClick={() => setForm(null)}>
            Cancelar
          </button>
        </div>
      </form>
    </div>
  )
}

export default function Productos() {
  const [items, setItems] = useState([])
  const [categorias, setCategorias] = useState([])
  const [marcas, setMarcas] = useState([])
  const [form, setForm, handleFormChange, setFormField] = useForm(null)

  const load = useCallback(async () => {
    try {
      const [resProductos, resCategorias, resMarcas] = await Promise.all([
        api.get(`${PATHS.productos}?ordering=nombre`),
        api.get(`${PATHS.categorias}?ordering=nombre`),
        api.get(`${PATHS.marcas}?ordering=nombre`),
      ])
      setItems(resProductos.data?.results || resProductos.data || [])
      setCategorias(resCategorias.data?.results || resCategorias.data || [])
      setMarcas(resMarcas.data?.results || resMarcas.data || [])
    } catch (error) {
      console.error('Error al cargar datos de productos:', error)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const save = useCallback(
    async e => {
      e.preventDefault()
      if (!form) return

      const formData = new FormData()
      Object.keys(form).forEach(key => {
        if (key === 'imagen') {
          if (form.imagen instanceof File) {
            formData.append('imagen', form.imagen)
          }
          return
        }

        const value = form[key]
        if (value === null || value === undefined) return

        // Booleans como 'true' / 'false' para DRF
        if (typeof value === 'boolean') {
          formData.append(key, value ? 'true' : 'false')
        } else {
          formData.append(key, value)
        }
      })

      const config = { headers: { 'Content-Type': 'multipart/form-data' } }
      try {
        if (form.id) {
          await api.patch(`${PATHS.productos}${form.id}/`, formData, config)
        } else {
          await api.post(PATHS.productos, formData, config)
        }
        setForm(null)
        load()
      } catch (error) {
        console.error('Error al guardar el producto:', error.response?.data || error)
        alert('Hubo un error al guardar el producto.')
      }
    },
    [form, load]
  )

  const del = useCallback(
    async id => {
      if (window.confirm('¿Eliminar producto?')) {
        try {
          await api.delete(`${PATHS.productos}${id}/`)
          load()
        } catch (error) {
          console.error('Error al eliminar el producto:', error)
          alert(
            'Hubo un error al eliminar el producto. Es posible que esté asociado a una venta.'
          )
        }
      }
    },
    [load]
  )

  return (
    <div className={`panel-split ${form ? 'has-form' : ''}`}>
      <div className="card">
        <h3>Productos</h3>
        <div className="btn-row" style={{ marginBottom: 12 }}>
          {/* Nuevo producto con activo = true por defecto */}
          <button onClick={() => setForm({ activo: true })}>
            + Nuevo Producto
          </button>
        </div>
        <ProductTable items={items} onEdit={setForm} onDelete={del} />
      </div>

      {form && (
        <ProductForm
          form={form}
          setForm={setForm}
          save={save}
          categorias={categorias}
          marcas={marcas}
          handleFormChange={handleFormChange}
          setFormField={setFormField}
        />
      )}
    </div>
  )
}
