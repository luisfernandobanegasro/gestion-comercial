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

