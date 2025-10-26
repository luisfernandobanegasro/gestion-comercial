from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # # OpenAPI
    path("api/esquema/", SpectacularAPIView.as_view(), name="esquema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="esquema"), name="docs"),

    # # Rutas de apps
    path("api/cuentas/", include("cuentas.urls")),
    path("api/catalogo/", include("catalogo.urls")),
    path("api/clientes/", include("clientes.urls")),
    path("api/ventas/", include("ventas.urls")),
    path("api/pagos/", include("pagos.urls")),
    path("api/reportes/", include("reportes.urls")),
    path("api/configuracion", include("configuracion.urls")),
    # path("api/analitica/", include("analitica.urls")),
    path("api/auditoria/", include("auditoria.urls")),  # ← esta es la que te falla ahora
    # path("api/ia/", include("ia.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
