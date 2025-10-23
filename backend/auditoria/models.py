from django.db import models
from django.conf import settings

class RegistroAuditoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    accion = models.CharField(max_length=100)        # p.ej. 'request', 'login', 'crear_producto'
    modulo = models.CharField(max_length=50)         # p.ej. 'cuentas','catalogo','ventas'
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ruta = models.CharField(max_length=255)
    metodo = models.CharField(max_length=10)
    estado = models.IntegerField(null=True, blank=True)    # status code de la respuesta
    payload = models.JSONField(null=True, blank=True)

    # Marcas de tiempo (tienes ambas: fecha/hora separadas y timestamp completo)
    fecha = models.DateField(auto_now_add=True, db_index=True)
    hora = models.TimeField(auto_now_add=True)
    creado_en = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["modulo", "fecha"]),
            models.Index(fields=["usuario", "fecha"]),
        ]

    def __str__(self):
        u = self.usuario_id if self.usuario_id else "anon"
        return f"[{self.creado_en}] {self.metodo} {self.ruta} ({u}) {self.estado or ''}"
