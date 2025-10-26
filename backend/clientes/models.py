from django.db import models
from django.conf import settings

class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Si se borra el usuario, se borra su perfil de cliente.
        related_name="perfil_cliente"
    )
    # Estos campos son para facturación y pueden ser distintos a los de la cuenta de usuario.
    nombre = models.CharField(max_length=120, help_text="Nombre completo o Razón Social para facturación")
    email = models.EmailField(blank=True, help_text="Email para facturación (si es distinto al de la cuenta)")
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    documento = models.CharField(max_length=20, blank=True, help_text="CI o NIT para facturas")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
        ]

    def __str__(self):
        return self.nombre or self.usuario.username