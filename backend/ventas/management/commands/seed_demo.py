# ventas/management/commands/seed_demo.py
from decimal import Decimal
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from cuentas.models import Rol
from clientes.models import Cliente
from catalogo.models import Producto
from ventas.models import Venta, ItemVenta

User = get_user_model()


class Command(BaseCommand):
    help = "Crea roles/usuarios/clientes y un set grande de ventas demo (últimos 3 meses)."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # -------------------------
        # Roles base
        # -------------------------
        admin_rol, _ = Rol.objects.get_or_create(
            nombre="Administrador", defaults={"descripcion": "Acceso total"}
        )
        emp_rol, _ = Rol.objects.get_or_create(
            nombre="Empleado", defaults={"descripcion": "Gestión comercial"}
        )
        cli_rol, _ = Rol.objects.get_or_create(
            nombre="Cliente", defaults={"descripcion": "Compras"}
        )

        # -------------------------
        # Usuarios admin / empleado
        # -------------------------
        admin, _ = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@demo.com"}
        )
        if not admin.has_usable_password():
            admin.set_password("1234")
            admin.save()
        admin.roles.add(admin_rol)

        empleado, _ = User.objects.get_or_create(
            username="empleado1", defaults={"email": "emp@demo.com"}
        )
        if not empleado.has_usable_password():
            empleado.set_password("1234")
            empleado.save()
        empleado.roles.add(emp_rol)

        # -------------------------
        # Clientes (usuarios + perfil)
        # -------------------------
        clientes = []

        # Aseguramos cliente1 (por compatibilidad con lo que ya tenías)
        cli_user_1, _ = User.objects.get_or_create(
            username="cliente1", defaults={"email": "cli@demo.com"}
        )
        if not cli_user_1.has_usable_password():
            cli_user_1.set_password("1234")
            cli_user_1.save()
        cli_user_1.roles.add(cli_rol)

        c1, _ = Cliente.objects.get_or_create(
            usuario=cli_user_1,
            defaults={
                "nombre": "Cliente Demo 1",
                "email": "cli@demo.com",
                "telefono": "70000001",
                "direccion": "Calle Demo 1, Zona Centro",
                "documento": "CI-8000001",
                "activo": True,
            },
        )
        clientes.append(c1)

        # Ahora creamos más clientes: cliente2 ... cliente40
        for i in range(2, 41):
            username = f"cliente{i}"
            email = f"cliente{i}@demo.com"

            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            if not user.has_usable_password():
                user.set_password("1234")
                user.save()
            user.roles.add(cli_rol)

            cliente, _ = Cliente.objects.get_or_create(
                usuario=user,
                defaults={
                    "nombre": f"Cliente Demo {i}",
                    "email": email,
                    "telefono": f"7000{i:04d}",
                    "direccion": f"Calle Demo {i}, Zona Centro",
                    "documento": f"CI-{8000000 + i}",
                    "activo": True,
                },
            )
            clientes.append(cliente)

        self.stdout.write(self.style.SUCCESS(f"✔ Clientes DEMO listos: {len(clientes)}"))

        # -------------------------
        # Productos para usar en las ventas
        # -------------------------
        productos = list(Producto.objects.filter(activo=True))
        if not productos:
            self.stdout.write(
                self.style.ERROR(
                    "❌ No hay productos activos. Ejecuta primero: python manage.py seed_catalogo"
                )
            )
            return

        # -------------------------
        # Limpiar ventas demo anteriores (solo las marcadas como [DEMO])
        # -------------------------
        demo_ventas = Venta.objects.filter(observaciones__startswith="[DEMO]")
        demo_count = demo_ventas.count()
        if demo_count:
            self.stdout.write(
                f"🧹 Eliminando {demo_count} ventas demo anteriores (observaciones '[DEMO] ...')."
            )
            demo_ventas.delete()

        # -------------------------
        # Crear ventas históricas de los últimos 3 meses
        # -------------------------
        now = timezone.now()
        dias_rango = 90  # ~3 meses
        estados = ["pendiente", "pagada"]

        total_ventas_creadas = 0
        total_items_creados = 0

        for cli in clientes:
            # entre 1 y 4 ventas por cliente
            num_ventas = random.randint(1, 4)

            for _ in range(num_ventas):
                # Fecha aleatoria en los últimos 90 días
                delta_dias = random.randint(1, dias_rango)
                fecha = now - timedelta(days=delta_dias)

                estado = random.choice(estados)

                v = Venta.objects.create(
                    cliente=cli,
                    estado=estado,
                    observaciones=f"[DEMO] Venta auto-generada para {cli.nombre}",
                    usuario=empleado,
                    creado_en=fecha,
                    actualizado_en=fecha,
                )

                # Entre 1 y 4 productos por venta
                num_items = random.randint(1, 4)
                usados_ids = set()

                for _ in range(num_items):
                    prod = random.choice(productos)
                    # Evitar repetir el mismo producto muchas veces en la misma venta
                    if prod.id in usados_ids:
                        continue
                    usados_ids.add(prod.id)

                    cantidad = random.randint(1, 3)
                    subtotal = prod.precio * Decimal(cantidad)

                    ItemVenta.objects.create(
                        venta=v,
                        producto=prod,
                        cantidad=cantidad,
                        precio_unit=prod.precio,
                        subtotal=subtotal,
                    )
                    total_items_creados += 1

                # Recalcula subtotal/total
                v.recalc_totales()

                # Actualizamos la fecha nuevamente por si recalc_totales hace save()
                Venta.objects.filter(pk=v.pk).update(
                    creado_en=fecha,
                    actualizado_en=fecha,
                )

                total_ventas_creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✔ Ventas DEMO creadas: {total_ventas_creadas} (items: {total_items_creados})"
            )
        )
        self.stdout.write(
            "- Usuarios demo: admin/1234, empleado1/1234, cliente1..cliente40 (pass: 1234)"
        )
