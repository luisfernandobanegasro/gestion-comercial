from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils.crypto import get_random_string
from clientes.models import Cliente
from catalogo.models import Producto, MovimientoInventario

ESTADO_VENTA = (
    ("pendiente", "Pendiente"),   # creada pero sin pago confirmado
    ("pagada", "Pagada"),         # pago aprobado
    ("anulada", "Anulada"),       # anulada antes/después de pago
    ("reembolsada", "Reembolsada")# se devolvió el dinero (total)
)

def generar_folio():
    # folio corto legible (no sensible)
    return f"V-{get_random_string(10).upper()}"

class Venta(models.Model):
    
    folio = models.CharField(
    max_length=20,
    unique=True,
    null=False,         # definitivo
    blank=False,        # definitivo
    default=generar_folio,  # definitivo (callable)
    db_index=True,
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ventas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventas_creadas")
    estado = models.CharField(max_length=12, choices=ESTADO_VENTA, default="pendiente", db_index=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    observaciones = models.CharField(max_length=250, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.folio} - {self.cliente.nombre} - {self.estado}"

    def recalc_totales(self):
        sub = sum((i.subtotal for i in self.items.all()), start=Decimal("0.00"))
        self.subtotal = sub
        # Política simple: total = subtotal - descuento + impuestos
        self.total = (self.subtotal - self.descuento + self.impuestos).quantize(Decimal("0.01"))
        self.save(update_fields=["subtotal", "total", "actualizado_en"])

    @property
    def puede_anular(self):
        return self.estado in ("pendiente", "pagada")

    @property
    def puede_confirmar_pago(self):
        return self.estado == "pendiente"

class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="items_vendidos")
    cantidad = models.PositiveIntegerField()
    precio_unit = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.venta.folio} - {self.producto.nombre} x{self.cantidad}"

    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar."""
        if self.cantidad and self.precio_unit:
            self.subtotal = self.cantidad * self.precio_unit
        super().save(*args, **kwargs)
