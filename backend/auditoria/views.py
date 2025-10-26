from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import RegistroAuditoria
from .serializers import RegistroAuditoriaSerializer
from .filters import RegistroAuditoriaFilter
from .export import exportar_auditoria_excel, exportar_auditoria_pdf
from cuentas.permissions import RequierePermisos

class RegistroAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para la bitácora de auditoría.
    Permite listar y exportar los registros.
    
    GET /api/auditoria/
      ?fecha_min=2025-10-01&fecha_max=2025-10-23
      &modulo=ventas&usuario=3&estado=201
      &q=productos&page=1&ordering=-creado_en
    """
    queryset = RegistroAuditoria.objects.select_related("usuario")
    serializer_class = RegistroAuditoriaSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["auditoria.ver"]
    pagination_class = None # <-- Desactiva la paginación para esta vista

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RegistroAuditoriaFilter
    ordering_fields = ["creado_en", "metodo", "estado", "modulo"]
    ordering = ['-creado_en'] # Orden por defecto

    @action(detail=False, methods=['get'], url_path='exportar-excel')
    def exportar_excel(self, request, *args, **kwargs):
        """
        Exporta los registros de auditoría filtrados a un archivo Excel.
        """
        queryset = self.filter_queryset(self.get_queryset())
        response = exportar_auditoria_excel(queryset)
        return response

    @action(detail=False, methods=['get'], url_path='exportar-pdf')
    def exportar_pdf(self, request, *args, **kwargs):
        """
        Exporta los registros de auditoría filtrados a un archivo PDF.
        """
        queryset = self.filter_queryset(self.get_queryset())
        response = exportar_auditoria_pdf(queryset)
        return response
