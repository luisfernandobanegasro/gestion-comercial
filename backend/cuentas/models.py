from django.contrib.auth.models import AbstractUser
from django.db import models

class Permiso(models.Model):
    # ejemplo de codigo: "catalogo.ver", "ventas.crear", "clientes.editar"
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.codigo

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)   # Administrador, Empleado, Cliente
    descripcion = models.CharField(max_length=200, blank=True)
    permisos = models.ManyToManyField(Permiso, blank=True, related_name="roles")

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    activo = models.BooleanField(default=True)
    roles = models.ManyToManyField(Rol, blank=True, related_name="usuarios")

    @property
    def nombres_roles(self):
        return list(self.roles.values_list("nombre", flat=True))

    def tiene_permiso(self, codigo: str) -> bool:
        # True si cualquier rol del usuario contiene el permiso "codigo"
        return self.roles.filter(permisos__codigo=codigo).exists()

    def get_all_permissions(self, obj=None):
        """
        Devuelve un set de strings con los códigos de permiso que tiene el usuario
        a través de sus roles. Sobrescribe el método de Django para usar nuestro
        sistema de roles personalizado.
        """
        if not self.is_active or self.is_anonymous:
            return set()
        if self.is_superuser:
            # Un superusuario tiene todos los permisos de nuestro sistema.
            return set(Permiso.objects.values_list('codigo', flat=True))

        # Obtenemos todos los permisos de todos los roles del usuario.
        return set(Permiso.objects.filter(roles__in=self.roles.all()).values_list('codigo', flat=True))
