# cuentas/permissions.py
from rest_framework.permissions import BasePermission

class RequierePermisos(BasePermission):
    """
    Lee de la vista los permisos requeridos en `required_perms` (lista de strings).
    Ejemplo en la vista:
        required_perms = ["catalogo.ver", "catalogo.crear"]
    """
    message = "No tienes permisos para realizar esta acción."

    def has_permission(self, request, view):
        # Si la vista no declaró permisos, permitir (queda solo autenticación)
        required = getattr(view, "required_perms", [])
        if not required:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Administrador Django (is_superuser) permite todo
        if user.is_superuser:
            return True
        # Si el usuario tiene TODOS los permisos requeridos
        for code in required:
            if not getattr(user, "tiene_permiso", lambda c: False)(code):
                return False
        return True
