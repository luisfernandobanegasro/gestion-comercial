from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import RegistroAuditoria
from .serializers import RegistroAuditoriaSerializer
from .filters import RegistroAuditoriaFilter
from cuentas.permissions import RequierePermisos

class RegistroAuditoriaLista(generics.ListAPIView):
    """
    GET /api/auditoria/registros/
      ?fecha_min=2025-10-01&fecha_max=2025-10-23
      &modulo=ventas&usuario=3&estado=201
      &q=productos&page=1&ordering=-creado_en
    """
    queryset = RegistroAuditoria.objects.select_related("usuario").order_by("-creado_en")
    serializer_class = RegistroAuditoriaSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["auditoria.ver"]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RegistroAuditoriaFilter
    ordering_fields = ["creado_en", "fecha", "metodo", "estado", "modulo"]
