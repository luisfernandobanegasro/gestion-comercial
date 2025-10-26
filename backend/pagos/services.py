import uuid
import stripe
from django.db import transaction, IntegrityError
from django.conf import settings
from .models import Pago
from ventas.services import marcar_pagada, marcar_reembolsada

# Configurar la clave de API de Stripe al iniciar el módulo
stripe.api_key = settings.STRIPE_SECRET_KEY

def _ensure_idempotency(idempotency_key: str) -> str:
    # Si no llega, generamos uno (esto evita doble confirmaciones si el cliente reintenta)
    return idempotency_key or f"key_{uuid.uuid4().hex}"

@transaction.atomic
def crear_intento_pago(venta, usuario, idempotency_key: str | None = None) -> Pago:
    key = _ensure_idempotency(idempotency_key)
    # idempotency a nivel de Pago
    try:
        pago, created = Pago.objects.get_or_create(
            venta=venta,
            defaults={
                "monto": venta.total,
                "usuario": usuario,
                "estado": "creado",
                "moneda": "BOB",
                "metodo": "stripe",
                "idempotency_key": key,
            },
        )
    except IntegrityError:
        # idempotency_key ya usado en otra operación: recuperamos
        pago = Pago.objects.get(idempotency_key=key)
    return pago

def crear_stripe_payment_intent(pago: Pago):
    """
    Crea o recupera un PaymentIntent de Stripe.
    Devuelve el client_secret para que el frontend pueda usarlo.
    """
    try:
        # Siempre creamos un nuevo PaymentIntent para asegurar un client_secret fresco.
        # Esto evita problemas si el usuario cancela y reintenta el pago.
        intent = stripe.PaymentIntent.create(
            amount=int(pago.monto * 100), # Stripe usa centavos
            currency=pago.moneda.lower(), # ej: 'bob'
            description=f"Pago para Venta {pago.venta.folio}",
            metadata={'venta_id': pago.venta.id, 'pago_id': pago.id}
        )
        # Guardamos la referencia del nuevo PaymentIntent en nuestro modelo de Pago
        pago.referencia = intent.id
        pago.save(update_fields=["referencia"])
        
        return intent.client_secret
    except Exception as e:
        raise ValueError(f"Error con Stripe: {str(e)}")

@transaction.atomic
def confirmar_pago_stripe(venta, usuario, idempotency_key: str | None = None) -> Pago:
    """
    DEPRECATED: Esta función simula un pago. El flujo real se inicia desde
    CrearIntentoPagoView y se confirma en el frontend. La confirmación final
    en el backend se hace llamando a `marcar_pagada` en la venta.
    """
    # Mantenemos la simulación por si se usa en otro lado, pero el flujo nuevo no la usará.
    pago = crear_intento_pago(venta, usuario, idempotency_key)
    if pago.estado != "aprobado":
        pago.referencia = f"pi_simulado_{uuid.uuid4().hex[:12]}"
        pago.estado = "aprobado"
        pago.save(update_fields=["referencia", "estado"])
        marcar_pagada(venta, usuario)
    return pago

@transaction.atomic
def reembolsar_pago_total(venta, usuario) -> Pago:
    pago = venta.pago
    if pago.estado != "aprobado":
        raise ValueError("Solo se puede reembolsar un pago aprobado.")
    pago.estado = "reembolsado"
    pago.save(update_fields=["estado"])
    marcar_reembolsada(venta, usuario)
    return pago
