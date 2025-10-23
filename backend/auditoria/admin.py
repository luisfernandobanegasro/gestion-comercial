from django.contrib import admin
from .models import RegistroAuditoria

@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("creado_en", "usuario", "modulo", "accion", "metodo", "estado", "ip")
    list_filter = ("modulo", "metodo", "estado", "fecha")
    search_fields = ("ruta", "accion", "user_agent", "ip")
    date_hierarchy = "fecha"
