from django.db import models
from django.conf import settings
from decimal import Decimal
from ventas.models import Venta

ESTADO_PAGO = (
    ("creado", "Creado"),          # intent creado
    ("aprobado", "Aprobado"),      # cobro exitoso
    ("fallido", "Fallido"),
    ("reembolsado", "Reembolsado") # reembolso (total)
)

class Pago(models.Model):
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name="pago")
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    moneda = models.CharField(max_length=10, default="BOB")
    metodo = models.CharField(max_length=30, default="stripe")
    estado = models.CharField(max_length=12, choices=ESTADO_PAGO, default="creado", db_index=True)
    referencia = models.CharField(max_length=120, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=60, blank=True, null=True, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pago {self.metodo} {self.estado} venta {self.venta_id}"
