from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Usuario, Rol, Permiso
from .serializers import UsuarioSerializer, RolSerializer, PermisoSerializer
from .permissions import RequierePermisos

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def yo(request):
    """Devuelve los datos completos del usuario autenticado."""
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)

# ping opcional para probar enroutado
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    return Response({"ok": True, "app": "cuentas"})


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().prefetch_related('roles', 'roles__permisos').order_by("username")
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, RequierePermisos]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["username", "email", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]

    # Aquí defines qué permiso se necesita para cada acción del CRUD
    def get_permissions(self):
        # Permitir que cualquiera se registre (cree un usuario)
        if self.action == 'create':
            return [AllowAny()]

        # Para el resto de acciones, requerir autenticación y permisos
        permission_classes = [IsAuthenticated, RequierePermisos]
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["usuarios.ver"]
        elif self.action in ["update", "partial_update"]:
            self.required_perms = ["usuarios.editar"]
        elif self.action == "destroy":
            self.required_perms = ["usuarios.eliminar"]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        # Al crear desde el endpoint público, asignamos rol "Cliente" automáticamente
        rol_cliente, _ = Rol.objects.get_or_create(nombre="Cliente")
        usuario = serializer.save()
        usuario.roles.add(rol_cliente)


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all().prefetch_related('permisos').order_by("nombre")
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated, RequierePermisos]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["nombre"]
    search_fields = ["nombre"]
    required_perms = ["roles.gestionar"] # Un solo permiso para todo el CRUD de roles


class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all().order_by("codigo")
    serializer_class = PermisoSerializer
    permission_classes = [IsAuthenticated, RequierePermisos]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["codigo"]
    search_fields = ["codigo", "descripcion"]
    # Solo los superusuarios o con un permiso muy específico deberían gestionar permisos
    required_perms = ["permisos.gestionar"]