from rest_framework import serializers
from .models import Venta, ItemVenta
from clientes.models import Cliente

# Serializer simple para anidar la información del cliente en la venta.
# Esto resuelve el problema del "N/A" en el detalle de la venta.
class _ClienteSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'documento', 'email']

class ItemVentaSerializer(serializers.ModelSerializer):
    # Añadimos el nombre del producto para que sea fácil de mostrar en el frontend.
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = ItemVenta
        fields = ["id", "producto", "producto_nombre", "cantidad", "precio_unit", "subtotal"]

class VentaSerializer(serializers.ModelSerializer):
    # Para lectura, incluimos el objeto completo del cliente y la lista de items.
    cliente_obj = _ClienteSimpleSerializer(source='cliente', read_only=True)
    items = ItemVentaSerializer(many=True, read_only=True)

    # cliente_nombre es útil para la vista de lista, donde no necesitamos el objeto completo.
    cliente_nombre = serializers.CharField(source="cliente.nombre", read_only=True)

    class Meta:
        model = Venta
        fields = [
            "id", "folio", "cliente", "cliente_obj", "cliente_nombre", "usuario",
            "estado", "subtotal", "descuento", "impuestos", "total",
            "observaciones", "creado_en", "actualizado_en", "items"
        ]
        # Hacemos que 'cliente' sea de solo escritura, ya que para leer usamos 'cliente_obj'.
        extra_kwargs = {
            'cliente': {'write_only': True}
        }

    def create(self, validated_data):
        # El frontend envía los items en el cuerpo de la petición, los recuperamos del contexto.
        items_data = self.context['request'].data.get('items', [])
        if not items_data:
            raise serializers.ValidationError({"items": "La venta debe tener al menos un producto."})

        venta = Venta.objects.create(**validated_data)

        for item_data in items_data:
            ItemVenta.objects.create(
                venta=venta,
                producto_id=item_data['producto'],
                cantidad=item_data['cantidad'],
                precio_unit=item_data['precio_unit']
                # El subtotal se calcula en el save del ItemVenta o en recalc_totales
            )

        venta.recalc_totales()
        return venta

    def update(self, instance, validated_data):
        # El método update solo se permitirá para ventas pendientes.
        if instance.estado != 'pendiente':
            raise serializers.ValidationError("Solo se pueden editar ventas en estado 'pendiente'.")

        items_data = self.context['request'].data.get('items')

        # Si se envían items, se reemplazan los existentes.
        if items_data is not None:
            if not items_data:
                raise serializers.ValidationError({"items": "La venta no puede quedar sin productos."})
            
            # Eliminar items antiguos y crear los nuevos
            instance.items.all().delete()
            for item_data in items_data:
                # Corregimos el nombre de la clave de 'producto' a 'producto_id'
                item_data['producto_id'] = item_data.pop('producto')
                ItemVenta.objects.create(venta=instance, **item_data)

        # Recalcular totales y guardar la venta
        instance.recalc_totales()
        return super().update(instance, validated_data)
