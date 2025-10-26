# ventas/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.db import transaction

from .models import Venta
from .serializers import VentaSerializer
from cuentas.permissions import RequierePermisos
from clientes.models import Cliente
from .services import marcar_pagada, anular_venta
from .pdf import generar_comprobante_pdf

class VentaViewSet(viewsets.ModelViewSet):
    """
    /api/ventas/ con JWT
    - Cliente: solo ve sus ventas (si tiene Cliente.usuario vinculado)
    - Empleado/Administrador: ven todo
    """
    queryset = Venta.objects.all().select_related("cliente", "usuario")
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    # required_perms se define por acción para mayor granularidad

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.roles.filter(nombre__iexact="Cliente").exists():
            cli = Cliente.objects.filter(usuario=u).first()
            if not cli:
                return qs.none()
            qs = qs.filter(cliente=cli)
        return qs

    def get_permissions(self):
        """Asigna permisos específicos para cada acción."""
        if self.action in ['list', 'retrieve']:
            self.required_perms = ["ventas.ver"]
        elif self.action == 'create':
            self.required_perms = ["ventas.crear"]
        elif self.action in ['update', 'partial_update']:
            self.required_perms = ["ventas.editar"]
        elif self.action == 'anular':
            self.required_perms = ["ventas.anular"]
        elif self.action in ['confirmar_pago', 'comprobante']:
            self.required_perms = ["pagos.crear"] # Reutilizamos el permiso de crear pagos
        else:
            # Default seguro para cualquier otra acción futura
            self.required_perms = ["admin.is_staff"]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(
        detail=True,
        methods=["post"],
    )
    def confirmar_pago(self, request, pk=None):
        """
        Marca la venta como pagada y descuenta stock.
        (Si ya está pagada, es idempotente.)
        """
        venta = self.get_object()
        try:
            with transaction.atomic():
                marcar_pagada(venta, usuario=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"detail": "Pago confirmado", "estado": venta.estado})

    @action(
        detail=True,
        methods=["post"],
    )
    def anular(self, request, pk=None):
        """
        Anula la venta. Si estaba pagada, reingresa stock.
        Si estaba pendiente, no toca stock.
        """
        venta = self.get_object()
        try:
            with transaction.atomic():
                anular_venta(venta, usuario=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"detail": "Venta anulada", "estado": venta.estado})

    @action(detail=True, methods=["get"], url_path="comprobante")
    def comprobante(self, request, pk=None):
        """Genera y devuelve el comprobante de la venta en formato PDF."""
        venta = self.get_object()
        if venta.estado != 'pagada':
            return Response({"detail": "Solo se puede generar comprobante de ventas pagadas."}, status=status.HTTP_400_BAD_REQUEST)

        buffer = generar_comprobante_pdf(venta)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprobante_{venta.folio}.pdf"'
        return response
