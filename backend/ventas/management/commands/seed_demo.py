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
    help = (
        "Crea roles/usuarios/clientes y un set GRANDE de ventas demo "
        "(último año completo) para pruebas de dashboard/reportes."
    )

    DEMO_PREFIX = "[DEMO-YEAR]"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando seed DEMO masivo..."))

        # ==========================
        # Roles base
        # ==========================
        admin_rol, _ = Rol.objects.get_or_create(
            nombre="Administrador", defaults={"descripcion": "Acceso total"}
        )
        emp_rol, _ = Rol.objects.get_or_create(
            nombre="Empleado", defaults={"descripcion": "Gestión comercial"}
        )
        cli_rol, _ = Rol.objects.get_or_create(
            nombre="Cliente", defaults={"descripcion": "Compras"}
        )

        # ==========================
        # Usuarios admin / empleado
        # ==========================
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

        # ==========================
        # Clientes (usuarios + perfil)
        # ==========================
        clientes: list[Cliente] = []

        # cliente1 “clásico”
        cli_user_1, _ = User.objects.get_or_create(
            username="cliente1", defaults={"email": "cliente1@demo.com"}
        )
        if not cli_user_1.has_usable_password():
            cli_user_1.set_password("1234")
            cli_user_1.save()
        cli_user_1.roles.add(cli_rol)

        c1, _ = Cliente.objects.get_or_create(
            usuario=cli_user_1,
            defaults={
                "nombre": "Cliente Demo 1",
                "email": "cliente1@demo.com",
                "telefono": "70000001",
                "direccion": "Calle Demo 1, Zona Centro",
                "documento": "CI-8000001",
                "activo": True,
            },
        )
        clientes.append(c1)

        # cliente2...cliente60
        for i in range(2, 61):
            username = f"cliente{i}"
            email = f"{username}@demo.com"

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
                    "telefono": f"7{i:07d}",
                    "direccion": f"Calle Demo {i}, Zona Centro",
                    "documento": f"CI-{8000000 + i}",
                    "activo": True,
                },
            )
            clientes.append(cliente)

        self.stdout.write(
            self.style.SUCCESS(f"✔ Clientes DEMO listos: {len(clientes)}")
        )

        # ==========================
        # Productos activos
        # ==========================
        productos = list(Producto.objects.filter(activo=True))
        if not productos:
            self.stdout.write(
                self.style.ERROR(
                    "❌ No hay productos activos. Ejecuta primero: "
                    "python manage.py seed_catalogo"
                )
            )
            return

        # ==========================
        # Limpiar ventas demo anteriores
        # ==========================
        demo_ventas = Venta.objects.filter(observaciones__startswith="[DEMO")
        demo_count = demo_ventas.count()
        if demo_count:
            self.stdout.write(
                f"🧹 Eliminando {demo_count} ventas demo anteriores "
                "(observaciones que empiezan con '[DEMO')."
            )
            demo_ventas.delete()

        # ==========================
        # Crear ventas históricas del ÚLTIMO AÑO
        # ==========================
        now = timezone.now()
        dias_rango = 365  # 1 año completo

        # pesos para los estados
        estados = ["pagada", "pendiente", "anulada"]
        pesos_estados = [0.7, 0.2, 0.1]  # 70% pagadas, 20% pendiente, 10% anulada

        total_ventas_creadas = 0
        total_items_creados = 0

        self.stdout.write("⏳ Generando ventas demo del último año...")

        # Recorremos día por día desde hoy hacia atrás
        for offset in range(dias_rango):
            # Fecha del día (con hora aleatoria)
            base_date = now - timedelta(days=offset)

            # entre 5 y 25 ventas por día
            num_ventas_dia = random.randint(5, 25)

            for _ in range(num_ventas_dia):
                cli = random.choice(clientes)

                estado = random.choices(estados, weights=pesos_estados, k=1)[0]

                # Hora aleatoria dentro del día
                hora = random.randint(8, 21)
                minuto = random.randint(0, 59)
                segundo = random.randint(0, 59)
                fecha = base_date.replace(
                    hour=hora, minute=minuto, second=segundo, microsecond=0
                )

                v = Venta.objects.create(
                    cliente=cli,
                    estado=estado,
                    observaciones=f"{self.DEMO_PREFIX} Venta auto-generada "
                    f"para {cli.nombre} ({fecha.date()})",
                    usuario=empleado,
                    creado_en=fecha,
                    actualizado_en=fecha,
                )

                # entre 1 y 6 productos distintos por venta
                num_items = random.randint(1, 6)
                usados_ids = set()

                for _ in range(num_items):
                    prod = random.choice(productos)
                    # evitamos repetir el mismo producto muchas veces en la misma venta
                    if prod.id in usados_ids:
                        continue
                    usados_ids.add(prod.id)

                    # cantidades pequeñas para que parezca más real
                    cantidad = random.randint(1, 4)
                    subtotal = prod.precio * Decimal(cantidad)

                    ItemVenta.objects.create(
                        venta=v,
                        producto=prod,
                        cantidad=cantidad,
                        precio_unit=prod.precio,
                        subtotal=subtotal,
                    )
                    total_items_creados += 1

                # recalcular totales
                v.recalc_totales()

                # aseguramos que la fecha no se “resetee”
                Venta.objects.filter(pk=v.pk).update(
                    creado_en=fecha,
                    actualizado_en=fecha,
                )

                total_ventas_creadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✔ Ventas DEMO creadas en total: {total_ventas_creadas} "
                f"(items: {total_items_creados})"
            )
        )
        self.stdout.write(
            "- Usuarios demo: admin/1234, empleado1/1234, "
            "cliente1..cliente60 (pass: 1234)"
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Seed masivo listo. El dashboard y los filtros deberían verse MUY poblados."
            )
        )
