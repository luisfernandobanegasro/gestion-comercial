from django.core.management.base import BaseCommand
from catalogo.models import Categoria, Producto
from django.db import transaction

def gen_code(prefix: str, sec: int) -> str:
    return f"{prefix}-{sec:03d}"

class Command(BaseCommand):
    help = "Crea categorías y productos de ejemplo con códigos únicos"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        data = [
            ("Tecnologia", [  # sin tilde por código
                ("Mouse Gamer", 25.0, 100),
                ("Teclado Mecanico", 55.0, 80),
                ("Auriculares BT", 40.0, 60),
            ], "TEC"),
            ("Hogar", [
                ("Cafetera", 30.0, 40),
                ("Licuadora", 45.0, 30),
            ], "HOG"),
        ]

        for cat_name, productos, pref in data:
            cat, _ = Categoria.objects.get_or_create(nombre=cat_name)
            # averigua cuántos productos con ese prefijo ya existen para no chocar
            existente = Producto.objects.filter(codigo__startswith=pref).count()
            sec = existente + 1

            for nombre, precio, stock in productos:
                # si el producto ya existe por nombre, actualizar y asignar código si no tiene
                prod, created = Producto.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        "categoria": cat,
                        "precio": precio,
                        "stock": stock,
                        "codigo": gen_code(pref, sec),
                    }
                )
                if not created:
                    # asegurar código único si estaba vacío/null o duplicado
                    if not prod.codigo:
                        prod.codigo = gen_code(pref, sec)
                    prod.categoria = cat
                    prod.precio = precio
                    if prod.stock is None or prod.stock < stock:
                        prod.stock = stock
                    prod.save()

                sec += 1

        self.stdout.write(self.style.SUCCESS("✔ Seed catálogo OK (códigos únicos)"))
