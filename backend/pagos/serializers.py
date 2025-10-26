from rest_framework import serializers
from ventas.models import Venta

class CrearIntentoSerializer(serializers.Serializer):
    venta_id = serializers.IntegerField()
    idempotency_key = serializers.CharField(max_length=60, required=False, allow_blank=True)

    def validate(self, data):
        try:
            venta = Venta.objects.get(id=data["venta_id"])
        except Venta.DoesNotExist:
            raise serializers.ValidationError("Venta no existe.")
        if venta.total <= 0:
            raise serializers.ValidationError("El total de la venta debe ser mayor a 0.")
        data["venta"] = venta
        return data

class ConfirmarPagoSerializer(serializers.Serializer):
    venta_id = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    idempotency_key = serializers.CharField(max_length=60, required=False, allow_blank=True)

    def validate(self, data):
        try:
            venta = Venta.objects.get(id=data["venta_id"])
        except Venta.DoesNotExist:
            raise serializers.ValidationError("Venta no existe.")
        if venta.total != data["monto"]:
            raise serializers.ValidationError("El monto no coincide con el total de la venta.")
        data["venta"] = venta
        return data

class ReembolsoSerializer(serializers.Serializer):
    venta_id = serializers.IntegerField()

    def validate(self, data):
        try:
            venta = Venta.objects.get(id=data["venta_id"])
        except Venta.DoesNotExist:
            raise serializers.ValidationError("Venta no existe.")
        if venta.estado not in ("pagada",):
            raise serializers.ValidationError("Solo se puede reembolsar una venta pagada.")
        data["venta"] = venta
        return data
