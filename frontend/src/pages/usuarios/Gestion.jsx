
import { useState } from 'react'
import Usuarios from './Usuarios.jsx'
import Roles from './Roles.jsx'
import Permisos from './Permisos.jsx'

export default function GestionUsuarios(){
  const [tab, setTab] = useState('usuarios')
  return (
    <div className="grid">
      <div className="card">
        <div className="tabs">
          <button className={`tab ${tab==='usuarios'?'active':''}`} onClick={()=>setTab('usuarios')}>Usuarios</button>
          <button className={`tab ${tab==='roles'?'active':''}`} onClick={()=>setTab('roles')}>Roles</button>
          <button className={`tab ${tab==='permisos'?'active':''}`} onClick={()=>setTab('permisos')}>Permisos</button>
        </div>
      </div>
      {tab==='usuarios' && <Usuarios/>}
      {tab==='roles' && <Roles/>}
      {tab==='permisos' && <Permisos/>}
    </div>
  )
}
