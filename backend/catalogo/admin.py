from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa", "creado_en")
    search_fields = ("nombre",)
    list_filter = ("activa",)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "precio", "stock", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("activo", "categoria")
