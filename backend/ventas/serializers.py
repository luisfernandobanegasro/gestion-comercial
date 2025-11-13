from rest_framework import serializers
from .models import Venta, ItemVenta
from clientes.models import Cliente


# Serializer simple para anidar la información del cliente en la venta.
# Esto resuelve el problema del "N/A" en el detalle de la venta.
class _ClienteSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nombre", "documento", "email"]


class ItemVentaSerializer(serializers.ModelSerializer):
    # Añadimos el nombre del producto para que sea fácil de mostrar en el frontend.
    producto_nombre = serializers.CharField(
        source="producto.nombre",
        read_only=True,
    )

    class Meta:
        model = ItemVenta
        fields = ["id", "producto", "producto_nombre",
                  "cantidad", "precio_unit", "subtotal"]


class VentaSerializer(serializers.ModelSerializer):
    # Para lectura, incluimos el objeto completo del cliente y la lista de items.
    cliente_obj = _ClienteSimpleSerializer(source="cliente", read_only=True)
    items = ItemVentaSerializer(many=True, read_only=True)

    # cliente_nombre es útil para la vista de lista, donde no necesitamos el objeto completo.
    cliente_nombre = serializers.CharField(
        source="cliente.nombre",
        read_only=True,
    )

    class Meta:
        model = Venta
        fields = [
            "id", "folio", "cliente", "cliente_obj", "cliente_nombre", "usuario",
            "estado", "subtotal", "descuento", "impuestos", "total",
            "observaciones", "creado_en", "actualizado_en", "items",
        ]
        # Web: puede enviar cliente.
        # App móvil (rol Cliente): puede omitir cliente y se auto-asigna.
        extra_kwargs = {
            "cliente": {"write_only": True, "required": False},
        }

    # ------------------ helpers internos ------------------

    def _resolver_cliente(self, validated_data):
        """
        - Si 'cliente' viene en validated_data → lo usa (caso web).
        - Si NO viene:
            * Si el usuario tiene rol Cliente → busca Cliente vinculado a ese usuario.
            * Si NO tiene rol Cliente → error.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)

        cliente = validated_data.get("cliente")
        if cliente:
            return cliente

        # No se mandó cliente explícito
        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                {"cliente": "Este campo es requerido."}
            )

        # Sólo autocompletamos para usuarios con rol 'Cliente'
        try:
            tiene_rol_cliente = user.roles.filter(
                nombre__iexact="Cliente"
            ).exists()
        except Exception:
            tiene_rol_cliente = False

        if not tiene_rol_cliente:
            # Admin / Empleado deben enviar cliente desde el frontend (web)
            raise serializers.ValidationError(
                {"cliente": "Este campo es requerido para usuarios que no son Cliente."}
            )

        cli = Cliente.objects.filter(usuario=user).first()
        if not cli:
            raise serializers.ValidationError(
                {
                    "cliente": (
                        "No hay un Cliente vinculado a este usuario. "
                        "Vincula el usuario a un Cliente en el panel de administración."
                    )
                }
            )

        validated_data["cliente"] = cli
        return cli

    # ------------------ CREATE ------------------

    def create(self, validated_data):
        request = self.context.get("request")

        # 1) Resolver cliente según reglas web / móvil
        self._resolver_cliente(validated_data)

        # 2) El frontend envía los items en el cuerpo de la petición
        items_data = []
        if request is not None:
            items_data = request.data.get("items", [])

        if not items_data:
            raise serializers.ValidationError(
                {"items": "La venta debe tener al menos un producto."}
            )

        # 3) Crear venta
        venta = Venta.objects.create(**validated_data)

        # 4) Crear items
        for item_data in items_data:
            ItemVenta.objects.create(
                venta=venta,
                producto_id=item_data["producto"],
                cantidad=item_data["cantidad"],
                precio_unit=item_data["precio_unit"],
                # El subtotal se calcula en el save del ItemVenta o en recalc_totales
            )

        # 5) Recalcular totales
        venta.recalc_totales()
        return venta

    # ------------------ UPDATE ------------------

    def update(self, instance, validated_data):
        # El método update solo se permitirá para ventas pendientes.
        if instance.estado != "pendiente":
            raise serializers.ValidationError(
                "Solo se pueden editar ventas en estado 'pendiente'."
            )

        request = self.context.get("request")
        items_data = (
            request.data.get("items") if request is not None else None
        )

        # Si se envían items, se reemplazan los existentes.
        if items_data is not None:
            if not items_data:
                raise serializers.ValidationError(
                    {"items": "La venta no puede quedar sin productos."}
                )

            # Eliminar items antiguos y crear los nuevos
            instance.items.all().delete()
            for item_data in items_data:
                producto_id = item_data.pop("producto")
                ItemVenta.objects.create(
                    venta=instance,
                    producto_id=producto_id,
                    **item_data,
                )

        # Recalcular totales y guardar la venta
        instance.recalc_totales()
        return super().update(instance, validated_data)
