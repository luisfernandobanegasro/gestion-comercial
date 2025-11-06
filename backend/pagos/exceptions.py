class PagosError(Exception):
    """Clase base para excepciones de la app de pagos."""
    pass

class StripeConfigError(PagosError):
    """Error si la configuración de Stripe falta."""
    pass

class StripePaymentError(PagosError):
    """Error durante una operación de pago con Stripe."""
    pass