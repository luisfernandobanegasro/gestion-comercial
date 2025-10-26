from rest_framework import views, permissions, status
from rest_framework.response import Response
from cuentas.permissions import RequierePermisos
from .serializers import CrearIntentoSerializer, ConfirmarPagoSerializer, ReembolsoSerializer
from .services import crear_intento_pago, confirmar_pago_stripe, reembolsar_pago_total, crear_stripe_payment_intent

class CrearIntentoPagoView(views.APIView):
    """
    POST /api/pagos/stripe/intent/
    body: { "venta_id": 1, "idempotency_key": "op-123" }
    """
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["pagos.crear"]

    def post(self, request):
        ser = CrearIntentoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        venta = ser.validated_data["venta"]
        # 1. Crea (o recupera) nuestro objeto Pago local
        pago = crear_intento_pago(venta, request.user, ser.validated_data.get("idempotency_key"))
        # 2. Crea (o recupera) el PaymentIntent en Stripe y obtiene el client_secret
        client_secret = crear_stripe_payment_intent(pago)

        return Response({
            "clientSecret": client_secret
        }, status=status.HTTP_200_OK)

class ConfirmarPagoStripeView(views.APIView):
    """
    POST /api/pagos/stripe/confirmar/
    body: { "venta_id": 1, "monto": "100.00", "idempotency_key": "op-123" }
    """
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["pagos.crear"]

    def post(self, request):
        ser = ConfirmarPagoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        venta = ser.validated_data["venta"]
        pago = confirmar_pago_stripe(venta, request.user, ser.validated_data.get("idempotency_key"))
        return Response({
            "detail": "Pago aprobado",
            "venta_id": venta.id,
            "pago_id": pago.id,
            "estado": pago.estado,
            "payment_intent": pago.referencia
        }, status=status.HTTP_200_OK)

class ReembolsoTotalView(views.APIView):
    """
    POST /api/pagos/stripe/reembolsar/
    body: { "venta_id": 1 }
    """
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["pagos.reembolsar"]

    def post(self, request):
        ser = ReembolsoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        venta = ser.validated_data["venta"]
        try:
            pago = reembolsar_pago_total(venta, request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({
            "detail": "Reembolso total OK",
            "venta_id": venta.id,
            "pago_id": pago.id,
            "estado": pago.estado
        }, status=status.HTTP_200_OK)
