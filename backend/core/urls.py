from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from .health import health_check

def root_health(_):
    return JsonResponse({"service": "smart-sales-365-api", "status": "ok"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_health),

    # OpenAPI
    path("api/esquema/", SpectacularAPIView.as_view(), name="esquema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="esquema"), name="docs"),

    # Rutas de apps
    path("api/cuentas/", include("cuentas.urls")),
    path("api/catalogo/", include("catalogo.urls")),
    path("api/clientes/", include("clientes.urls")),
    path("api/ventas/", include("ventas.urls")),
    path("api/pagos/", include("pagos.urls")),
    path("api/reportes/", include("reportes.urls")),
    path("api/configuracion/", include("configuracion.urls")),
    path("api/analitica/", include("analitica.urls")),
    path("api/auditoria/", include("auditoria.urls")),
    # psath("api/ia/", include("ia.urls")),

    path("health/", health_check, name="health_check"),
]

# ⭐ SERVIR MEDIA TANTO EN DEBUG COMO EN PRODUCCIÓN ⭐
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
