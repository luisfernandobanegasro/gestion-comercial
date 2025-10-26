from django.core.management.base import BaseCommand
from cuentas.models import Permiso, Rol, Usuario

PERMISOS = [
    # catálogo
    ("catalogo.ver", "Listar y ver productos/categorías"),
    ("catalogo.crear", "Crear productos/categorías"),
    ("catalogo.editar", "Editar productos/categorías"),
    ("catalogo.eliminar", "Eliminar productos/categorías"),
    # clientes
    ("clientes.ver", "Listar y ver clientes"),
    ("clientes.crear", "Crear clientes"),
    ("clientes.editar", "Editar clientes"),
    ("clientes.eliminar", "Eliminar clientes"),
    # ventas
    ("ventas.ver", "Ver ventas e historial"),
    ("ventas.crear", "Crear ventas (checkout)"),
    ("ventas.anular", "Anular/cancelar ventas"),
    # pagos
    ("pagos.ver", "Ver métodos de pago y estados"),
    ("pagos.crear", "Iniciar/confirmar pagos"),
    # reportes
    ("reportes.generar", "Generar reportes (texto/voz)"),
    ("reportes.exportar", "Exportar PDF/Excel"),
    # analítica/IA
    ("analitica.ver", "Ver KPIs/histórico"),
    ("ia.ver", "Ver predicciones"),
    ("ia.entrenar", "Entrenar modelo"),
    #adutorioa
    ("auditoria.ver", "Ver registros de auditoría"),

    
]

ROLES = {
    "Administrador": {
        "descripcion": "Acceso total al sistema",
        "permisos": [p[0] for p in PERMISOS],  # todos
    },
    "Empleado": {
        "descripcion": "Gestiona catálogo, clientes y ventas",
        "permisos": [
            # catálogo
            "catalogo.ver", "catalogo.crear", "catalogo.editar",
            # clientes
            "clientes.ver", "clientes.crear", "clientes.editar",
            # ventas
            "ventas.ver", "ventas.crear",
            # reportes
            "reportes.generar",
            # analítica (solo ver)
            "analitica.ver", "ia.ver",
        ],
    },
    "Cliente": {
        "descripcion": "Puede comprar y ver sus compras",
        "permisos": [
            "catalogo.ver",        # ver productos
            "ventas.crear",        # checkout (carrito)
            "ventas.ver",          # ver historial propio (tu lógica filtra por usuario/cliente)
        ],
    },
}

class Command(BaseCommand):
    help = "Crea permisos y roles base (Administrador, Empleado, Cliente)."

    def handle(self, *args, **options):
        # Crear/actualizar permisos
        for code, desc in PERMISOS:
            p, created = Permiso.objects.get_or_create(codigo=code, defaults={"descripcion": desc})
            if not created and p.descripcion != desc:
                p.descripcion = desc
                p.save()

        # Crear roles y asignar permisos
        for nombre, data in ROLES.items():
            rol, _ = Rol.objects.get_or_create(nombre=nombre, defaults={"descripcion": data["descripcion"]})
            codigos = data["permisos"]
            perms = list(Permiso.objects.filter(codigo__in=codigos))
            rol.permisos.set(perms)

        self.stdout.write(self.style.SUCCESS("Permisos y roles base creados/actualizados."))

        # Crear superuser admin si no existe
        if not Usuario.objects.filter(username="admin").exists():
            u = Usuario.objects.create_superuser("admin", "admin@local", "admin123")
            admin_rol = Rol.objects.get(nombre="Administrador")
            u.roles.add(admin_rol)
            self.stdout.write(self.style.SUCCESS("Superusuario admin creado y rol Administrador asignado."))
        else:
            self.stdout.write(self.style.WARNING("Superusuario admin ya existe."))
