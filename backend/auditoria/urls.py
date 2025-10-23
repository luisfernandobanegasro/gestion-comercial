from django.urls import path
from .views import RegistroAuditoriaLista

urlpatterns = [
    path("registros/", RegistroAuditoriaLista.as_view(), name="auditoria_registros"),
]
