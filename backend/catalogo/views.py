# # catalogo/views.py (ejemplo)
# from rest_framework import viewsets, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from cuentas.permissions import RequierePermisos
# from .models import Producto, Categoria, MovimientoInventario
# from .serializers import ProductoSerializer, CategoriaSerializer, MovimientoInventarioSerializer

# class ProductoViewSet(viewsets.ModelViewSet):
#     queryset = Producto.objects.all().order_by("nombre")
#     serializer_class = ProductoSerializer
#     permission_classes = [permissions.IsAuthenticated, RequierePermisos]
#     required_perms = ["catalogo.ver"]           # para listar/ver
#     # Para acciones que crean/editan, puedes reforzar:
#     def get_permissions(self):
#         perms = ["catalogo.ver"]
#         if self.action in ["create"]:
#             perms = ["catalogo.crear"]
#         elif self.action in ["update", "partial_update"]:
#             perms = ["catalogo.editar"]
#         elif self.action in ["destroy"]:
#             perms = ["catalogo.eliminar"]
#         self.required_perms = perms
#         return [p() for p in self.permission_classes]
