# ventas/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

def user_has_role(user, nombre_rol: str) -> bool:
    try:
        return user.roles.filter(nombre__iexact=nombre_rol).exists()
    except Exception:
        return False

class EsAdminOEmpleadoPuedeVer(BasePermission):
    """
    - Admin / Empleado: pueden ver todo.
    - Cliente: solo sus propias ventas (filtramos en la vista).
    - Edición por cliente: solo si es suya y estado 'pendiente'.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if user_has_role(request.user, "Administrador") or user_has_role(request.user, "Empleado"):
            return True

        if user_has_role(request.user, "Cliente"):
            es_suya = getattr(obj.cliente, "usuario_id", None) == request.user.id
            return es_suya and obj.estado == "pendiente"

        return False
