# ventas/management/commands/seed_demo.py
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from cuentas.models import Rol
from clientes.models import Cliente
from catalogo.models import Categoria, Producto
from ventas.models import Venta, ItemVenta

User = get_user_model()


class Command(BaseCommand):
    help = "Crea roles/usuarios/clientes/catalogo y ventas de demo."

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
        # Usuarios
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

        cliente_u, _ = User.objects.get_or_create(
            username="cliente1", defaults={"email": "cli@demo.com"}
        )
        if not cliente_u.has_usable_password():
            cliente_u.set_password("1234")
            cliente_u.save()
        cliente_u.roles.add(cli_rol)

        # -------------------------
        # Cliente (el perfil se crea automáticamente por el signal al asignar el rol)
        # -------------------------
        try:
            # Obtenemos el perfil de cliente que el signal debió haber creado
            c1 = Cliente.objects.get(usuario=cliente_u)
            self.stdout.write("✔ Perfil de cliente para 'cliente1' encontrado.")
        except Cliente.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ No se encontró el perfil de cliente para 'cliente1'. Revisa los signals."))
            return

        # -------------------------
        # Catálogo (categoría y productos)
        # -------------------------
        cat, _ = Categoria.objects.get_or_create(nombre="Tecnología")

        p1, _ = Producto.objects.get_or_create(
            nombre="Mouse Gamer",
            defaults={"categoria": cat, "precio": Decimal("25.00"), "stock": 100},
        )
        p2, _ = Producto.objects.get_or_create(
            nombre="Teclado Mecánico",
            defaults={"categoria": cat, "precio": Decimal("55.00"), "stock": 50},
        )

        # Asegura que los productos tengan stock (por si ya existían con 0)
        if p1.stock < 10:
            p1.stock = 100
            p1.save(update_fields=["stock"])
        if p2.stock < 10:
            p2.stock = 50
            p2.save(update_fields=["stock"])

        # -------------------------
        # Venta DEMO #1 (PENDIENTE) del cliente
        # -------------------------
        v1, _ = Venta.objects.get_or_create(
            cliente=c1,
            estado="pendiente",
            defaults={"observaciones": "Venta de demostración (pendiente)", "usuario": empleado},
        )
        # reset items
        v1.items.all().delete()
        ItemVenta.objects.create(
            venta=v1,
            producto=p1,
            cantidad=2,
            precio_unit=p1.precio,
            subtotal=p1.precio * Decimal("2"),
        )
        ItemVenta.objects.create(
            venta=v1,
            producto=p2,
            cantidad=1,
            precio_unit=p2.precio,
            subtotal=p2.precio * Decimal("1"),
        )
        v1.recalc_totales()

        # -------------------------
        # Venta DEMO #2 (PAGADA) del cliente
        # -------------------------
        v2, created = Venta.objects.get_or_create(
            cliente=c1,
            estado="pagada",
            defaults={"observaciones": "Venta de demostración (pagada)", "usuario": empleado},
        )
        if created or not v2.items.exists():
            v2.items.all().delete()
            ItemVenta.objects.create(
                venta=v2,
                producto=p1,
                cantidad=3,
                precio_unit=p1.precio,
                subtotal=p1.precio * Decimal("3"),
            )
            v2.recalc_totales()

        self.stdout.write(self.style.SUCCESS("✔ Seed demo creado:"))
        self.stdout.write("- Usuarios: admin/1234, empleado1/1234, cliente1/1234")
        self.stdout.write("- Ventas: 1 pendiente y 1 pagada (para reportes)")
