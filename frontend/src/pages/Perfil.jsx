
import { useAuth } from '../hooks/useAuth.jsx'

export default function Perfil(){
  const { user } = useAuth()
  if (!user) return null
  return (
    <div className="card">
      <h3>Mi perfil</h3>
      <p><strong>Usuario:</strong> {user.username}</p>
      <p><strong>Email:</strong> {user.email}</p>
      <p>
        <strong>Roles:</strong> {
          user.nombres_roles?.join(', ') || 
          (user.is_superuser ? 'Super Administrador' : 'No asignado')
        }
      </p>
    </div>
  )
}
