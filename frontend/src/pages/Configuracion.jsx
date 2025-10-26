import { useEffect, useState, useCallback } from 'react';
import api from '../api/axios';
import { PATHS } from '../api/paths';

// Hook de formulario reutilizable
const useForm = (initialState = {}) => {
  const [form, setForm] = useState(initialState);
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };
  return [form, setForm, handleFormChange];
};

export default function Configuracion() {
  const [form, setForm, handleFormChange] = useForm({});
  const [loading, setLoading] = useState(true);

  // Carga la configuración desde el backend
  const loadConfig = useCallback(async () => {
    try {
      const res = await api.get(PATHS.configuracion);
      setForm(res.data || {}); // Asegurarse de que el form no sea null
    } catch (error) {
      console.error("Error al cargar la configuración", error);
      // No mostramos alerta si no hay config, puede ser la primera vez
      if (error.response?.status !== 404) {
        alert("No tienes permiso para ver la configuración.");
      }
    } finally {
      setLoading(false);
    }
  }, [setForm]);

  useEffect(() => { loadConfig() }, [loadConfig]);

  // Guarda la configuración en el backend
  const saveConfig = async (e) => {
    e.preventDefault();
    try {
      await api.put(PATHS.configuracion, form);
      alert("Configuración guardada con éxito.");
    } catch (error) {
      console.error("Error al guardar la configuración", error);
      alert(`No se pudo guardar la configuración: ${error.response?.data?.detail || 'Error desconocido'}`);
    }
  };

  if (loading) return <div className="card">Cargando...</div>;

  return (
    <div className="card">
      <h2>Configuración de Pagos</h2>
      <form className="grid" onSubmit={saveConfig}>
        <input name="nombre_banco" placeholder="Nombre del Banco" value={form.nombre_banco || ''} onChange={handleFormChange} />
        <input name="numero_cuenta" placeholder="Número de Cuenta" value={form.numero_cuenta || ''} onChange={handleFormChange} />
        <input name="nombre_titular" placeholder="Nombre del Titular" value={form.nombre_titular || ''} onChange={handleFormChange} />
        <input name="documento_titular" placeholder="CI/NIT del Titular" value={form.documento_titular || ''} onChange={handleFormChange} />
        <input name="glosa_qr" placeholder="Glosa o concepto para QR" value={form.glosa_qr || ''} onChange={handleFormChange} />
        <button type="submit" className="primary">Guardar Configuración</button>
      </form>
    </div>
  );
}