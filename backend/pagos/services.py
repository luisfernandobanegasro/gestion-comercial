# pagos/services.py
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import transaction

from ventas.models import Venta
from .models import Pago

# Stripe opcional (modo fake si no hay)
try:
    import stripe
except ImportError:
    stripe = None

STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", None)
STRIPE_CURRENCY = getattr(settings, "STRIPE_CURRENCY", "bob").lower()

if stripe and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


def _amount_to_cents(monto: Decimal) -> int:
    return int(Decimal(monto) * 100)


# ================
# 1) Intento pago
# ================

def crear_intento_pago(
    venta: Venta,
    user,
    idempotency_key: str | None = None,
) -> Pago:
    """
    Crea (o recupera) el Pago asociado a una venta.
    """
    if idempotency_key:
        pago = Pago.objects.filter(idempotency_key=idempotency_key).first()
        if pago:
            return pago

    pago, created = Pago.objects.get_or_create(
        venta=venta,
        defaults={
            "monto": venta.total,
            "moneda": STRIPE_CURRENCY.upper(),
            "usuario": user if getattr(user, "is_authenticated", False) else None,
            "idempotency_key": idempotency_key or "",
            "estado": "creado",
        },
    )

    if not created:
        pago.monto = venta.total
        pago.moneda = STRIPE_CURRENCY.upper()
        if user and getattr(user, "is_authenticated", False):
            pago.usuario = user
        if idempotency_key:
            pago.idempotency_key = idempotency_key
        if not pago.estado:
            pago.estado = "creado"
        pago.save(update_fields=["monto", "moneda", "usuario", "idempotency_key", "estado"])

    return pago


# ==========================
# 2) PaymentIntent en Stripe
# ==========================

def crear_stripe_payment_intent(pago: Pago) -> str:
    """
    Crea (o reutiliza) un PaymentIntent en Stripe y devuelve client_secret.
    Si Stripe no está configurado, genera uno fake.
    """
    if not stripe or not STRIPE_SECRET_KEY:
        if not pago.referencia:
            pago.referencia = f"fake_pi_{pago.id}"
            pago.save(update_fields=["referencia"])
        return f"fake_client_secret_{pago.id}"

    if pago.referencia:
        try:
            pi = stripe.PaymentIntent.retrieve(pago.referencia)
            return pi.client_secret
        except Exception:
            pass

    amount_cents = _amount_to_cents(pago.monto)
    params = {
        "amount": amount_cents,
        "currency": STRIPE_CURRENCY,
        "metadata": {
            "venta_id": pago.venta_id,
            "pago_id": pago.id,
        },
    }

    idempotency = pago.idempotency_key or f"pago-{pago.id}"
    pi = stripe.PaymentIntent.create(**params, idempotency_key=idempotency)

    pago.referencia = pi.id
    pago.save(update_fields=["referencia"])

    return pi.client_secret


# ==========================
# 3) Confirmar pago
# ==========================

@transaction.atomic
def confirmar_pago_stripe(
    venta: Venta,
    user,
    idempotency_key: str | None = None,
) -> Pago:
    """
    Marca el pago como aprobado y la venta como pagada.
    Opcionalmente valida el PaymentIntent en Stripe.
    """
    pago = crear_intento_pago(venta, user, idempotency_key)

    if pago.estado == "aprobado":
        return pago

    if stripe and STRIPE_SECRET_KEY and pago.referencia:
        try:
            pi = stripe.PaymentIntent.retrieve(pago.referencia)
            if pi.status not in ("succeeded", "requires_capture"):
                raise ValueError(f"PaymentIntent aún no está aprobado (status={pi.status})")
        except Exception:
            raise ValueError("No se pudo validar el pago en Stripe.")

    pago.estado = "aprobado"
    pago.usuario = user if getattr(user, "is_authenticated", False) else None
    pago.save(update_fields=["estado", "usuario"])

    venta.estado = "pagada"
    venta.save(update_fields=["estado"])

    return pago


# ==========================
# 4) Reembolso total
# ==========================

@transaction.atomic
def reembolsar_pago_total(venta: Venta, user) -> Pago:
    """
    Reembolso total de la venta (si el pago está aprobado).
    """
    try:
        pago = Pago.objects.select_for_update().get(venta=venta)
    except Pago.DoesNotExist:
        raise ValueError("No existe un pago asociado a esta venta.")

    if pago.estado != "aprobado":
        raise ValueError("Solo se puede reembolsar un pago aprobado.")

    if stripe and STRIPE_SECRET_KEY and pago.referencia:
        try:
            stripe.Refund.create(
                payment_intent=pago.referencia,
                metadata={"venta_id": venta.id, "pago_id": pago.id},
            )
        except Exception as e:
            raise ValueError(f"No se pudo procesar el reembolso en Stripe: {e}")

    pago.estado = "reembolsado"
    pago.usuario = user if getattr(user, "is_authenticated", False) else None
    pago.save(update_fields=["estado", "usuario"])

    venta.estado = "reembolsada"
    venta.save(update_fields=["estado"])

    return pago


