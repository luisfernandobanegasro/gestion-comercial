# ventas/services.py
from django.db import transaction
from catalogo.models import MovimientoInventario
from .models import Venta

@transaction.atomic
def anular_venta(venta: Venta, usuario):
    """
    Anula la venta. Si estaba pagada, reingresa stock.
    Si estaba pendiente, NO toca stock (porque aún no se descontó).
    """
    if not venta.puede_anular:
        raise ValueError("La venta no puede ser anulada en su estado actual.")

    if venta.estado == "pagada":
        # Reingreso por anulación (venta ya había descontado stock)
        for it in venta.items.select_related("producto"):
            prod = it.producto
            prod.stock = prod.stock + it.cantidad
            prod.save(update_fields=["stock"])
            MovimientoInventario.objects.create(
                producto=prod,
                tipo="IN",
                cantidad=it.cantidad,
                motivo=f"Reingreso por anulación {venta.folio}",
                usuario=usuario,
            )

    venta.estado = "anulada"
    venta.save(update_fields=["estado"])
    return venta


@transaction.atomic
def marcar_pagada(venta: Venta, usuario=None):
    """
    Marca venta como 'pagada' y DESCUENTA stock (con movimientos OUT).
    Idempotente: si ya está 'pagada' no repite.
    """
    if venta.estado == "pagada":
        return venta

    if not venta.puede_confirmar_pago:
        raise ValueError(f"No se puede marcar como pagada desde estado '{venta.estado}'")

    # Descuento de stock
    for it in venta.items.select_related("producto"):
        prod = it.producto
        if prod.stock < it.cantidad:
            raise ValueError(
                f"Stock insuficiente para {prod.nombre}. "
                f"Disponible: {prod.stock}, requerido: {it.cantidad}"
            )
        prod.stock -= it.cantidad
        prod.save(update_fields=["stock"])
        MovimientoInventario.objects.create(
            producto=prod,
            tipo="OUT",
            cantidad=it.cantidad,
            motivo=f"Venta {venta.folio}",
            usuario=usuario,
        )

    venta.estado = "pagada"
    venta.save(update_fields=["estado"])
    return venta


@transaction.atomic
def marcar_reembolsada(venta: Venta, usuario):
    """
    Cambia la venta a 'reembolsada' y reingresa stock con movimientos IN.
    Idempotente: si ya está 'reembolsada' no repite.
    """
    if venta.estado == "reembolsada":
        return venta

    if venta.estado != "pagada":
        raise ValueError(
            f"Solo se puede reembolsar una venta 'pagada'; estado actual '{venta.estado}'"
        )

    for it in venta.items.select_related("producto"):
        prod = it.producto
        prod.stock += it.cantidad
        prod.save(update_fields=["stock"])
        MovimientoInventario.objects.create(
            producto=prod,
            tipo="IN",
            cantidad=it.cantidad,
            motivo=f"Reingreso por reembolso {venta.folio}",
            usuario=usuario,
        )

    venta.estado = "reembolsada"
    venta.save(update_fields=["estado"])
    return venta
