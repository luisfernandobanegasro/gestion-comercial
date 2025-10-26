from django.contrib import admin
from .models import Pago

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "venta", "metodo", "monto", "estado", "creado_en")
    list_filter = ("metodo", "estado", "creado_en")
    search_fields = ("referencia", "venta__id")
