# ventas/admin.py
from django.contrib import admin
from .models import Venta, ItemVenta

class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    extra = 0
    autocomplete_fields = ["producto"]
    fields = ("producto", "cantidad", "precio_unit", "subtotal")
    readonly_fields = ("subtotal",)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("folio", "cliente", "usuario", "estado", "total", "creado_en")
    list_filter = ("estado", "creado_en")
    search_fields = ("folio", "cliente__nombre", "usuario__username")
    autocomplete_fields = ["cliente", "usuario"]
    inlines = [ItemVentaInline]
    readonly_fields = ("subtotal", "total", "creado_en", "actualizado_en")
    fieldsets = (
        ("Datos", {
            "fields": ("folio", "cliente", "usuario", "estado", "observaciones")
        }),
        ("Totales", {
            "fields": ("subtotal", "descuento", "impuestos", "total")
        }),
        ("Tiempos", {
            "fields": ("creado_en", "actualizado_en")
        }),
    )

@admin.register(ItemVenta)
class ItemVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unit", "subtotal")
    autocomplete_fields = ["venta", "producto"]
    search_fields = ("venta__folio", "producto__nombre")
