# ventas/views.py
from django.db import transaction
from django.http import HttpResponse

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Venta, ItemVenta
from .serializers import VentaSerializer
from cuentas.permissions import RequierePermisos
from clientes.models import Cliente
from catalogo.models import Producto
from .services import marcar_pagada, anular_venta
from .pdf import generar_comprobante_pdf


class VentaViewSet(viewsets.ModelViewSet):
    """
    /api/ventas/ con JWT
    - Cliente: solo ve sus ventas (si tiene Cliente.usuario vinculado)
    - Empleado/Administrador: ven todo
    """
    queryset = Venta.objects.all().select_related("cliente", "usuario")
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    # required_perms se define por acción para mayor granularidad

    # ======================
    # Helpers internos
    # ======================
    def _resolver_cliente(self, request):
        """
        Devuelve el Cliente a partir de:
        - query param 'cliente' o body 'cliente'
        - o el cliente vinculado al usuario autenticado.
        """
        u = request.user
        cliente_id = request.data.get("cliente") or request.query_params.get("cliente")

        if cliente_id:
            cliente = Cliente.objects.filter(pk=cliente_id).first()
            if not cliente:
                raise ValidationError({"cliente": "Cliente no encontrado."})
            return cliente

        cliente = Cliente.objects.filter(usuario=u).first()
        if not cliente:
            raise ValidationError(
                {
                    "cliente": (
                        "No se pudo determinar el cliente. "
                        "Envíe el ID de cliente o vincule el usuario a un cliente."
                    )
                }
            )
        return cliente

    def _get_or_create_carrito(self, usuario, cliente):
        """
        Obtiene o crea la Venta en estado 'pendiente' que actuará como carrito
        para ese usuario + cliente.
        """
        venta, _ = Venta.objects.get_or_create(
            cliente=cliente,
            usuario=usuario,
            estado="pendiente",
        )
        return venta

    # ======================
    # Queryset / permisos
    # ======================
    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.roles.filter(nombre__iexact="Cliente").exists():
            cli = Cliente.objects.filter(usuario=u).first()
            if not cli:
                return qs.none()
            qs = qs.filter(cliente=cli)
        return qs

    def get_permissions(self):
        """Asigna permisos específicos para cada acción."""
        if self.action in ["list", "retrieve"]:
            self.required_perms = ["ventas.ver"]
        elif self.action in [
            "create",
            "crear_desde_carrito",
            "carrito",
            "carrito_item",
            "confirmar_carrito",
        ]:
            self.required_perms = ["ventas.crear"]
        elif self.action in ["update", "partial_update"]:
            self.required_perms = ["ventas.editar"]
        elif self.action == "anular":
            self.required_perms = ["ventas.anular"]
        elif self.action in ["confirmar_pago", "comprobante"]:
            # Reutilizamos el permiso de crear pagos
            self.required_perms = ["pagos.crear"]
        else:
            # Default seguro para cualquier otra acción futura
            self.required_perms = ["admin.is_staff"]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    # ======================
    # Carrito WEB (Venta pendiente)
    # ======================
    @action(detail=False, methods=["get", "post"], url_path="carrito")
    def carrito(self, request):
        """
        GET  -> devuelve la venta pendiente (carrito) del cliente/usuario.
                Si no existe, la crea vacía.
        POST -> agrega/incrementa un producto en el carrito.

        Body para POST:
        {
          "cliente": 1,          # opcional si el usuario ya está vinculado
          "producto": 5,
          "cantidad": 2
        }
        """
        usuario = request.user
        cliente = self._resolver_cliente(request)

        if request.method == "GET":
            venta = (
                Venta.objects.filter(
                    cliente=cliente,
                    usuario=usuario,
                    estado="pendiente",
                )
                .prefetch_related("items__producto")
                .first()
            )
            if not venta:
                venta = self._get_or_create_carrito(usuario, cliente)

            ser = VentaSerializer(venta, context={"request": request})
            return Response(ser.data)

        # POST -> agregar producto
        prod_id = request.data.get("producto")
        cantidad = int(request.data.get("cantidad") or 0)

        if not prod_id or cantidad <= 0:
            raise ValidationError(
                {"cantidad": "Debe enviar 'producto' y 'cantidad' > 0."}
            )

        # ⚠️ IMPORTANTE: ya no filtramos por activo=True aquí
        producto = Producto.objects.filter(pk=prod_id).first()
        if not producto:
            raise ValidationError({"producto": "Producto no encontrado."})
        if not producto.activo:
            raise ValidationError({"producto": "El producto está inactivo."})

        with transaction.atomic():
            venta = self._get_or_create_carrito(usuario, cliente)

            item = ItemVenta.objects.filter(venta=venta, producto=producto).first()
            cantidad_actual = item.cantidad if item else 0
            nueva_cantidad = cantidad_actual + cantidad

            # validarStock
            if nueva_cantidad > producto.stock:
                raise ValidationError({"cantidad": "No hay stock suficiente."})

            precio_unit = producto.precio_final

            if item:
                item.cantidad = nueva_cantidad
                item.precio_unit = precio_unit
                item.save()
            else:
                ItemVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unit=precio_unit,
                )

            venta.recalc_totales()

        ser = VentaSerializer(venta, context={"request": request})
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["patch", "delete"],
        url_path=r"carrito/items/(?P<item_id>[^/.]+)",
    )
    def carrito_item(self, request, item_id=None):
        """
        PATCH  -> cambia cantidad de un ítem del carrito.
                  Body: { "cantidad": 3 }
        DELETE -> elimina un ítem del carrito.
        """
        usuario = request.user

        try:
            item = (
                ItemVenta.objects.select_related("venta", "producto").get(
                    pk=item_id,
                    venta__usuario=usuario,
                    venta__estado="pendiente",
                )
            )
        except ItemVenta.DoesNotExist:
            return Response(
                {"detail": "Ítem no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        venta = item.venta

        with transaction.atomic():
            if request.method == "DELETE":
                item.delete()
            else:  # PATCH
                cantidad = int(request.data.get("cantidad") or 0)
                if cantidad <= 0:
                    item.delete()
                else:
                    if cantidad > item.producto.stock:
                        raise ValidationError({"cantidad": "No hay stock suficiente."})
                    item.cantidad = cantidad
                    item.save()

            venta.recalc_totales()

        ser = VentaSerializer(venta, context={"request": request})
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="carrito/confirmar")
    def confirmar_carrito(self, request):
        """
        Confirma el carrito (venta pendiente) y devuelve la Venta.

        Body:
        {
          "cliente": 1   # opcional si el usuario ya está vinculado
        }

        NO marca como pagada, solo asegura que tiene ítems y totales correctos.
        Luego, el flujo de pago usará `confirmar_pago`.
        """
        usuario = request.user
        cliente = self._resolver_cliente(request)

        venta = (
            Venta.objects.filter(
                cliente=cliente,
                usuario=usuario,
                estado="pendiente",
            )
            .prefetch_related("items__producto")
            .first()
        )
        if not venta or not venta.items.exists():
            return Response(
                {"detail": "El carrito está vacío."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        venta.recalc_totales()
        ser = VentaSerializer(venta, context={"request": request})
        return Response(ser.data, status=status.HTTP_200_OK)

    # ======================
    # Carrito MÓVIL (ya lo tenías)
    # ======================
    @action(detail=False, methods=["post"], url_path="desde-carrito")
    def crear_desde_carrito(self, request):
        """
        Crea una venta a partir de un carrito enviado por el cliente móvil.

        Espera body JSON:
        {
          "cliente": 1,              # opcional si el usuario ya está vinculado a un Cliente
          "items": [
            { "producto": 5, "cantidad": 2 },
            { "producto": 7, "cantidad": 1 }
          ]
        }

        Respuesta: VentaSerializer + estado ya 'pagada'.
        """
        u = request.user

        # 1) Resolver cliente
        cliente_id = request.data.get("cliente")
        if cliente_id:
            cliente = Cliente.objects.filter(pk=cliente_id).first()
            if not cliente:
                return Response(
                    {"detail": "Cliente no encontrado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Buscar cliente vinculado al usuario (rol Cliente)
            cliente = Cliente.objects.filter(usuario=u).first()
            if not cliente:
                return Response(
                    {
                        "detail": (
                            "No se pudo determinar el cliente. "
                            "Envíe el ID de cliente o vincule el usuario a un cliente."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        items_data = request.data.get("items", [])
        if not items_data:
            return Response(
                {"detail": "El carrito está vacío."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # 2) Crear venta en estado 'pendiente'
            venta = Venta.objects.create(
                cliente=cliente,
                usuario=u,
                estado="pendiente",
            )

            # 3) Crear items con el precio actual del producto (precio_final si hay oferta)
            for raw_item in items_data:
                prod_id = raw_item.get("producto")
                cantidad = int(raw_item.get("cantidad") or 0)

                if not prod_id or cantidad <= 0:
                    continue

                # Igual que arriba: ya no filtramos por activo en la consulta,
                # pero sí lo comprobamos.
                producto = Producto.objects.filter(pk=prod_id).first()
                if not producto:
                    continue
                if not producto.activo:
                    continue

                precio_unit = producto.precio_final  # usa descuento si lo hay
                ItemVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unit=precio_unit,
                    subtotal=precio_unit * cantidad,
                )

            # Validar que haya items
            if not venta.items.exists():
                raise ValueError("La venta no tiene ítems válidos.")

            # 4) Recalcular totales y marcar pagada (descuento de stock)
            venta.recalc_totales()
            marcar_pagada(venta, usuario=u)

        serializer = VentaSerializer(venta, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ======================
    # Pago / Anulación / Comprobante
    # ======================
    @action(detail=True, methods=["post"])
    def confirmar_pago(self, request, pk=None):
        """
        Marca la venta como pagada y descuenta stock.
        (Si ya está pagada, es idempotente.)
        """
        venta = self.get_object()
        try:
            with transaction.atomic():
                marcar_pagada(venta, usuario=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"detail": "Pago confirmado", "estado": venta.estado})

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        """
        Anula la venta. Si estaba pagada, reingresa stock.
        Si estaba pendiente, no toca stock.
        """
        venta = self.get_object()
        try:
            with transaction.atomic():
                anular_venta(venta, usuario=request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response({"detail": "Venta anulada", "estado": venta.estado})

    @action(detail=True, methods=["get"], url_path="comprobante")
    def comprobante(self, request, pk=None):
        """Genera y devuelve el comprobante de la venta en formato PDF."""
        venta = self.get_object()
        if venta.estado != "pagada":
            return Response(
                {"detail": "Solo se puede generar comprobante de ventas pagadas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        buffer = generar_comprobante_pdf(venta)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="comprobante_{venta.folio}.pdf"'
        )
        return response
