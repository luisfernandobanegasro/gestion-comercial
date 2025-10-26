from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, MarcaViewSet, OfertaViewSet, ProductoViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
router.register(r"categorias", CategoriaViewSet, basename="categoria")
router.register(r"marcas", MarcaViewSet, basename="marca")
router.register(r"ofertas", OfertaViewSet, basename="oferta")
router.register(r"productos", ProductoViewSet, basename="producto")
router.register(r"movimientos", MovimientoInventarioViewSet, basename="movimiento")

urlpatterns = [
    path("", include(router.urls)),
]
