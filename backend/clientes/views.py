from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cliente
from .serializers import ClienteSerializer
from .filters import ClienteFilter
from cuentas.permissions import RequierePermisos

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.select_related("usuario").all().order_by("nombre")
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ClienteFilter
    ordering_fields = ["nombre", "creado_en"]
    search_fields = ["nombre","email","telefono","documento"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["clientes.ver"]
        elif self.action == "create":
            self.required_perms = ["clientes.crear"]
        elif self.action in ["update", "partial_update"]:
            self.required_perms = ["clientes.editar"]
        elif self.action == "destroy":
            self.required_perms = ["clientes.eliminar"]
        return [p() for p in self.permission_classes]
