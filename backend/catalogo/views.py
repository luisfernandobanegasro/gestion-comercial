from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Categoria, Marca, Producto, MovimientoInventario, Oferta
from .serializers import CategoriaSerializer, MarcaSerializer, ProductoSerializer, MovimientoInventarioSerializer, OfertaSerializer
from .filters import ProductoFilter
from cuentas.permissions import RequierePermisos

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["catalogo.ver"]
        elif self.action == "create":
            self.required_perms = ["catalogo.crear"]
        elif self.action in ["update", "partial_update"]:
            self.required_perms = ["catalogo.editar"]
        elif self.action == "destroy":
            self.required_perms = ["catalogo.eliminar"]
        return [p() for p in self.permission_classes]

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all().order_by("nombre")
    serializer_class = MarcaSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["nombre"]
    search_fields = ["nombre"]

    def get_permissions(self):
        # Usamos los mismos permisos que para categorías
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["catalogo.ver"]
        else:
            self.required_perms = ["catalogo.editar"] # Un solo permiso para crear/editar/eliminar
        return [p() for p in self.permission_classes]

class OfertaViewSet(viewsets.ModelViewSet):
    queryset = Oferta.objects.all().order_by("-fecha_inicio")
    serializer_class = OfertaSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["fecha_inicio", "fecha_fin", "porcentaje_descuento"]
    search_fields = ["nombre"]

    def get_permissions(self):
        # Usamos permisos de catálogo, pero podrías crear unos específicos como "ofertas.gestionar"
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["catalogo.ver"]
        else:
            self.required_perms = ["catalogo.editar"]
        return [p() for p in self.permission_classes]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related("categoria", "marca").prefetch_related('ofertas_especificas').all().order_by("nombre")
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductoFilter
    ordering_fields = ["precio", "nombre", "stock", "creado_en"]
    search_fields = ["nombre", "codigo"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["catalogo.ver"]
        elif self.action == "create":
            self.required_perms = ["catalogo.crear"]
        elif self.action in ["update", "partial_update"]:
            self.required_perms = ["catalogo.editar"]
        elif self.action == "destroy":
            self.required_perms = ["catalogo.eliminar"]
        return [p() for p in self.permission_classes]

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.select_related("producto","usuario").all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["creado_en", "cantidad"]

    def get_permissions(self):
        # Podrías tener permisos específicos de inventario, por ahora usamos catalogo.editar
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["catalogo.ver"]
        else:
            self.required_perms = ["catalogo.editar"]
        return [p() for p in self.permission_classes]

    @transaction.atomic
    def perform_create(self, serializer):
        mov = serializer.save(usuario=self.request.user)
        p = mov.producto
        if mov.tipo == "IN":
            p.stock = p.stock + mov.cantidad
        else:
            if mov.cantidad > p.stock:
                # rollback implícito por atomic
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"cantidad": "No hay stock suficiente para salida."})
            p.stock = p.stock - mov.cantidad
        p.save(update_fields=["stock"])
