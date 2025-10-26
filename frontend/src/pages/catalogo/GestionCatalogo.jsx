import { useState } from 'react'
import Productos from './Productos.jsx'
import Categorias from './Categorias.jsx'
import Marcas from './Marcas.jsx'

export default function GestionCatalogo() {
  const [tab, setTab] = useState('productos')
  return (
    <div className="grid">
      <div className="card">
        <div className="tabs">
          <button className={`tab ${tab === 'productos' ? 'active' : ''}`} onClick={() => setTab('productos')}>Productos</button>
          <button className={`tab ${tab === 'categorias' ? 'active' : ''}`} onClick={() => setTab('categorias')}>Categorías</button>
          <button className={`tab ${tab === 'marcas' ? 'active' : ''}`} onClick={() => setTab('marcas')}>Marcas</button>
        </div>
      </div>
      {tab === 'productos' && <Productos />}
      {tab === 'categorias' && <Categorias />}
      {tab === 'marcas' && <Marcas />}
    </div>
  )
}
