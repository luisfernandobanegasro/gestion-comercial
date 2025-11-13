// src/components/Sidebar.jsx
import { NavLink } from 'react-router-dom'
import {
  Home,
  Receipt,
  BarChart3,
  ScrollText,
  UserRound,
  Boxes,
  UsersRound,
  ShieldCheck,
  Settings,
  Percent, // icono para Ofertas
} from 'lucide-react'
import Can from './Can' // guardián de permisos

export default function Sidebar({ collapsed }) {
  return (
    <aside className="sidebar">
      <div className="side-header">
        <div className="brand-dot"></div>
        <div className="hide-when-collapsed">SmartSales365</div>
      </div>

      <nav>
        {/* ===================== PRINCIPAL ===================== */}
        <div className="nav-group-title hide-when-collapsed">Principal</div>

        <Can required="analitica.ver">
          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Home className="nav-icon" />
            <span className="hide-when-collapsed">Dashboard</span>
          </NavLink>
        </Can>

        <Can required="ventas.ver">
          <NavLink
            to="/ventas"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Receipt className="nav-icon" />
            <span className="hide-when-collapsed">Ventas</span>
          </NavLink>
        </Can>

        <Can required="reportes.generar">
          <NavLink
            to="/reportes"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <BarChart3 className="nav-icon" />
            <span className="hide-when-collapsed">Reportes</span>
          </NavLink>
        </Can>

        <Can required="auditoria.ver">
          <NavLink
            to="/bitacora"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <ScrollText className="nav-icon" />
            <span className="hide-when-collapsed">Bitácora</span>
          </NavLink>
        </Can>

        <NavLink
          to="/perfil"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <UserRound className="nav-icon" />
          <span className="hide-when-collapsed">Perfil</span>
        </NavLink>

        {/* ===================== CATÁLOGO ===================== */}
        <div className="nav-group-title hide-when-collapsed">Catálogo</div>

        <Can required="catalogo.ver">
          <NavLink
            to="/productos"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Boxes className="nav-icon" />
            <span className="hide-when-collapsed">Productos</span>
          </NavLink>
        </Can>

        {/* Gestión de ofertas (CRUD) */}
        <Can required="catalogo.editar">
          <NavLink
            to="/ofertas"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Percent className="nav-icon" />
            <span className="hide-when-collapsed">Ofertas</span>
          </NavLink>
        </Can>

        <Can required="clientes.ver">
          <NavLink
            to="/clientes"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <UsersRound className="nav-icon" />
            <span className="hide-when-collapsed">Clientes</span>
          </NavLink>
        </Can>

        {/* ===================== ADMINISTRACIÓN ===================== */}
        <div className="nav-group-title hide-when-collapsed">Administración</div>

        <Can required="usuarios.ver">
          <NavLink
            to="/usuarios"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <ShieldCheck className="nav-icon" />
            <span className="hide-when-collapsed">Gestión de usuarios</span>
          </NavLink>
        </Can>

        <Can required="configuracion.gestionar">
          <NavLink
            to="/configuracion"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Settings className="nav-icon" />
            <span className="hide-when-collapsed">Configuración</span>
          </NavLink>
        </Can>
      </nav>
    </aside>
  )
}
