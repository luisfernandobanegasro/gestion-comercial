from django.urls import path
from .views import ConfiguracionView

urlpatterns = [
    # Esta única URL maneja GET y PUT/PATCH para la configuración
    path("", ConfiguracionView.as_view(), name="configuracion-detail"),
]