import { useAuth } from '../hooks/useAuth';

/**
 * Componente "guardián" que renderiza sus hijos solo si el usuario
 * tiene el permiso requerido.
 *
 * Un superusuario siempre tiene permiso.
 *
 * Uso: <Can required="permiso.requerido"> ...contenido a mostrar... </Can>
 */
export default function Can({ required, children }) {
  const { user, userHasPermission } = useAuth();

  const hasPerm = userHasPermission(required);
  const isSuper = user?.is_superuser;

  return (hasPerm || isSuper) ? <>{children}</> : null;
}