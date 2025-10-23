from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("activo", "roles")}),
    )
    list_display = ("username", "email", "is_staff", "activo")
    filter_horizontal = ("roles",)

admin.site.register(Rol)
