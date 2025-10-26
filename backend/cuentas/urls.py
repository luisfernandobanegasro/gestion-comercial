from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import yo, UsuarioViewSet, RolViewSet, PermisoViewSet

# El router genera automáticamente las URLs para el ViewSet (list, create, retrieve, update, destroy)
router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuario")
router.register(r"roles", RolViewSet, basename="rol")
router.register(r"permisos", PermisoViewSet, basename="permiso")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("yo/", yo, name="cuentas_yo"),
    # Incluimos las URLs generadas por el router
    path("", include(router.urls)),
]
