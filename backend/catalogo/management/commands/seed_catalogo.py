# catalogo/management/commands/seed_catalogo.py
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from catalogo.models import Categoria, Producto, Marca


class Command(BaseCommand):
    help = "Crea categorías, marcas y un catálogo amplio de productos de ejemplo."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # ============================
        # CATEGORÍAS
        # ============================
        categorias_def = [
            ("Tecnología", "Dispositivos electrónicos y gadgets"),
            ("Telefonía", "Smartphones y accesorios móviles"),
            ("Computación", "Laptops, PCs y periféricos"),
            ("Audio y Video", "TV, parlantes, audífonos, etc."),
            ("Electrodomésticos", "Electrodomésticos para el hogar"),
            ("Hogar", "Productos generales para el hogar"),
            ("Gaming", "Consolas, accesorios y sillas gamer"),
            ("Accesorios", "Cables, cargadores y otros accesorios"),
            ("Cosmética y Belleza", "Maquillaje, cuidado de la piel y fragancias"),
            ("Cuidado Personal", "Higiene personal y cuidado diario"),
            ("Supermercado", "Alimentos, snacks y productos básicos"),
        ]

        cats = {}
        for nombre, desc in categorias_def:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": desc, "activa": True},
            )
            if not getattr(cat, "descripcion", ""):
                cat.descripcion = desc
                cat.save(update_fields=["descripcion"])
            cats[nombre] = cat

        # ============================
        # MARCAS
        # ============================
        marcas_nombres = [
            "Apple",
            "Samsung",
            "Xiaomi",
            "Huawei",
            "Motorola",
            "LG",
            "Sony",
            "TCL",
            "Philips",
            "Lenovo",
            "HP",
            "Dell",
            "Acer",
            "Asus",
            "Nvidia",
            "AMD",
            "JBL",
            "Bose",
            "HomeTech",
            "Oster",
            "KitchenAid",
            "Midea",
            "Whirlpool",
            "Logitech",
            "Redragon",
            # Belleza / cuidado
            "L'Oréal",
            "Maybelline",
            "Nivea",
            "Dove",
            "Pantene",
            "Gillette",
            "Colgate",
            # Supermercado
            "Coca-Cola",
            "Pepsi",
            "Nestlé",
            "Arcor",
        ]

        marcas = {}
        for nombre in marcas_nombres:
            marca, _ = Marca.objects.get_or_create(
                nombre=nombre,
                defaults={"activa": True},
            )
            if not marca.activa:
                marca.activa = True
                marca.save(update_fields=["activa"])
            marcas[nombre] = marca

        # ============================
        # Helper para códigos únicos
        # ============================
        def next_codigo(pref: str) -> str:
            """
            Genera un código único con prefijo, buscando el máximo sufijo usado:
            pref-001, pref-002, etc.
            """
            existentes = (
                Producto.objects.filter(
                    Q(codigo__startswith=pref + "-") | Q(codigo__istartswith=pref + "-")
                )
                .exclude(codigo__isnull=True)
                .values_list("codigo", flat=True)
            )

            max_n = 0
            for c in existentes:
                try:
                    parte = c.split("-")[1]
                    n = int(parte)
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue

            max_n += 1
            return f"{pref}-{max_n:03d}"

        # ============================
        # PRODUCTOS
        # ============================
        # nombre, modelo, caracteristicas, precio, stock, categoria_nombre, marca_nombre, prefijo_codigo
        productos_def = [
            # ---------------- Telefonía ----------------
            (
                "iPhone 15",
                "A3100",
                "Smartphone gama alta 256GB, doble cámara",
                "8999.00",
                20,
                "Telefonía",
                "Apple",
                "TEL",
            ),
            (
                "iPhone 15 Pro",
                "A3200",
                "Smartphone gama alta 512GB, triple cámara",
                "10999.00",
                10,
                "Telefonía",
                "Apple",
                "TEL",
            ),
            (
                "Galaxy S24",
                "SM-S921B",
                "Smartphone Android gama alta 256GB",
                "7999.00",
                25,
                "Telefonía",
                "Samsung",
                "TEL",
            ),
            (
                "Galaxy A35",
                "SM-A356E",
                "Smartphone Android gama media 128GB",
                "2999.00",
                40,
                "Telefonía",
                "Samsung",
                "TEL",
            ),
            (
                "Redmi Note 13",
                "23117RAE5G",
                "Smartphone Android gama media 256GB",
                "2499.00",
                35,
                "Telefonía",
                "Xiaomi",
                "TEL",
            ),
            (
                "Moto G85",
                "XT2415",
                "Smartphone Android con 8GB RAM y 256GB",
                "2299.00",
                30,
                "Telefonía",
                "Motorola",
                "TEL",
            ),
            (
                "P40 Lite",
                "JNY-LX1",
                "Smartphone Huawei 128GB, 6GB RAM",
                "2199.00",
                15,
                "Telefonía",
                "Huawei",
                "TEL",
            ),
            (
                "Auriculares BT In-ear",
                "AM61",
                "Auriculares Bluetooth deportivos",
                "199.00",
                60,
                "Telefonía",
                "Huawei",
                "ACC",
            ),
            # ---------------- Audio y Video (TV / sonido) ----------------
            (
                'Smart TV 55" 4K',
                "55PUD7408",
                "Smart TV 4K UHD con HDR y apps",
                "3999.00",
                15,
                "Audio y Video",
                "Philips",
                "TV",
            ),
            (
                'Smart TV 50" 4K QLED',
                "50C645",
                "Smart TV 4K QLED con Dolby Vision",
                "3699.00",
                18,
                "Audio y Video",
                "TCL",
                "TV",
            ),
            (
                'Smart TV 65" 4K',
                "65UQ8050",
                "Smart TV 65 pulgadas 4K con webOS",
                "5299.00",
                10,
                "Audio y Video",
                "LG",
                "TV",
            ),
            (
                'Smart TV 43" FHD',
                "43T5300",
                "Smart TV 43 pulgadas Full HD",
                "2499.00",
                20,
                "Audio y Video",
                "Samsung",
                "TV",
            ),
            (
                "Barra de sonido 2.1",
                "SB202",
                "Barra de sonido con subwoofer inalámbrico",
                "1199.00",
                30,
                "Audio y Video",
                "LG",
                "AUD",
            ),
            (
                "Sistema de sonido 5.1",
                "HT-S500RF",
                "Sistema de teatro en casa 5.1 canales",
                "2599.00",
                8,
                "Audio y Video",
                "Sony",
                "AUD",
            ),
            (
                "Parlante Bluetooth portátil",
                "GO3",
                "Parlante portátil resistente al agua",
                "399.00",
                60,
                "Audio y Video",
                "JBL",
                "AUD",
            ),
            (
                "Auriculares inalámbricos",
                "TWS-01",
                "Auriculares TWS con estuche de carga",
                "259.00",
                70,
                "Audio y Video",
                "Xiaomi",
                "AUD",
            ),
            # ---------------- Computación ----------------
            (
                'Notebook 14" Core i5',
                "14-DQ2511",
                "Laptop 8GB RAM, 512GB SSD, Windows 11",
                "4999.00",
                18,
                "Computación",
                "HP",
                "PC",
            ),
            (
                'Notebook Gamer 15" RTX 4060',
                "G15-4060",
                "Laptop gamer 16GB RAM, 512GB SSD",
                "8999.00",
                12,
                "Computación",
                "Dell",
                "PC",
            ),
            (
                'All in One 23.8"',
                "AIO-24",
                "PC All in One 8GB RAM, 512GB SSD",
                "5699.00",
                10,
                "Computación",
                "Lenovo",
                "PC",
            ),
            (
                'Notebook 15" Ryzen 5',
                "A315-44",
                "Laptop 8GB RAM 512GB SSD, Ryzen 5",
                "4399.00",
                20,
                "Computación",
                "Acer",
                "PC",
            ),
            (
                'Monitor 27" 144Hz',
                "VG27AQ",
                "Monitor IPS 2K 144Hz para gaming",
                "2299.00",
                20,
                "Computación",
                "Asus",
                "MON",
            ),
            (
                'Monitor 24" 75Hz',
                "24MK430",
                "Monitor 24 pulgadas IPS 75Hz",
                "999.00",
                25,
                "Computación",
                "LG",
                "MON",
            ),
            (
                "Teclado Mecánico RGB",
                "K552",
                "Teclado mecánico retroiluminado para gaming",
                "299.00",
                80,
                "Accesorios",
                "Redragon",
                "ACC",
            ),
            (
                "Mouse Gamer Óptico",
                "G203",
                "Mouse gamer 8000 DPI con RGB",
                "189.00",
                100,
                "Accesorios",
                "Logitech",
                "ACC",
            ),
            (
                "Mouse inalámbrico",
                "M185",
                "Mouse inalámbrico 2.4GHz",
                "99.00",
                120,
                "Accesorios",
                "Logitech",
                "ACC",
            ),
            (
                "Teclado inalámbrico",
                "MK270",
                "Combo teclado + mouse inalámbrico",
                "219.00",
                60,
                "Accesorios",
                "Logitech",
                "ACC",
            ),
            (
                "Disco SSD 1TB",
                "SN850X",
                "Unidad SSD NVMe 1TB alta velocidad",
                "799.00",
                25,
                "Computación",
                "Western Digital",
                "PC",
            ),
            # ---------------- Gaming ----------------
            (
                "Consola PS5 Slim",
                "CFI-2016A",
                "Consola PlayStation 5 1TB",
                "5999.00",
                8,
                "Gaming",
                "Sony",
                "GAM",
            ),
            (
                "Control DualSense",
                "CFI-ZCT1W",
                "Control inalámbrico para PS5",
                "499.00",
                25,
                "Gaming",
                "Sony",
                "GAM",
            ),
            (
                "Silla Gamer Ergonómica",
                "SG-500",
                "Silla gamer reclinable con soporte lumbar",
                "899.00",
                15,
                "Gaming",
                "HomeTech",
                "GAM",
            ),
            (
                "Auriculares Gamer",
                "H510",
                "Auriculares gamer con micrófono y RGB",
                "259.00",
                40,
                "Gaming",
                "Redragon",
                "GAM",
            ),
            (
                "Mousepad Gamer XXL",
                "MP-900",
                "Mousepad XXL con bordes cosidos",
                "89.00",
                90,
                "Gaming",
                "HomeTech",
                "GAM",
            ),
            # ---------------- Electrodomésticos grandes (lavadoras, heladeras, etc.) ----------------
            (
                "Heladera No Frost 310L",
                "RF310",
                "Refrigerador No Frost bajo consumo",
                "3999.00",
                10,
                "Electrodomésticos",
                "Midea",
                "ELC",
            ),
            (
                "Heladera No Frost 400L",
                "RF400",
                "Heladera No Frost Inox 400L",
                "4599.00",
                7,
                "Electrodomésticos",
                "Whirlpool",
                "ELC",
            ),
            (
                "Cocina 4 hornallas",
                "CK-4H",
                "Cocina a gas con horno",
                "2499.00",
                8,
                "Electrodomésticos",
                "Midea",
                "ELC",
            ),
            (
                "Lavarropas 12kg",
                "LV1200",
                "Lavarropas automático 12kg",
                "3599.00",
                7,
                "Electrodomésticos",
                "LG",
                "ELC",
            ),
            (
                "Lavarropas 9kg",
                "WT09",
                "Lavarropas semiautomático 9kg",
                "2399.00",
                9,
                "Electrodomésticos",
                "Midea",
                "ELC",
            ),
            (
                "Secadora 8kg",
                "SD800",
                "Secadora eléctrica 8kg",
                "2999.00",
                6,
                "Electrodomésticos",
                "Whirlpool",
                "ELC",
            ),
            # ---------------- Hogar / electrodomésticos pequeños ----------------
            (
                "Cafetera Eléctrica",
                "CM120",
                "Cafetera para 12 tazas con filtro permanente",
                "299.00",
                30,
                "Hogar",
                "Oster",
                "HOG",
            ),
            (
                "Licuadora 600W",
                "BLST4655",
                "Licuadora 600W vaso de vidrio",
                "349.00",
                25,
                "Hogar",
                "Oster",
                "HOG",
            ),
            (
                "Horno eléctrico 45L",
                "HO-45",
                "Horno eléctrico 45L con grill",
                "499.00",
                20,
                "Hogar",
                "HomeTech",
                "HOG",
            ),
            (
                "Microondas 20L",
                "MO-20",
                "Microondas digital 20 litros",
                "399.00",
                22,
                "Hogar",
                "Midea",
                "HOG",
            ),
            (
                "Batidora de mano",
                "BT-150",
                "Batidora de mano 5 velocidades",
                "149.00",
                40,
                "Hogar",
                "KitchenAid",
                "HOG",
            ),
            # ---------------- Accesorios varios ----------------
            (
                "Cargador USB-C 25W",
                "EP-TA800",
                "Cargador rápido USB-C 25W",
                "129.00",
                120,
                "Accesorios",
                "Samsung",
                "ACC",
            ),
            (
                "Cable USB-C 1m",
                "CB-UC100",
                "Cable USB-C a USB-C 1 metro",
                "49.00",
                200,
                "Accesorios",
                "HomeTech",
                "ACC",
            ),
            (
                "Power Bank 10000mAh",
                "PB10000",
                "Batería externa 10000mAh",
                "179.00",
                90,
                "Accesorios",
                "Xiaomi",
                "ACC",
            ),
            (
                "Adaptador HDMI a VGA",
                "AV-01",
                "Adaptador de video HDMI a VGA",
                "69.00",
                80,
                "Accesorios",
                "HomeTech",
                "ACC",
            ),
            # ---------------- Cosmética y Belleza ----------------
            (
                "Base de maquillaje líquida",
                "TrueMatch",
                "Base de maquillaje líquida tono medio",
                "89.00",
                50,
                "Cosmética y Belleza",
                "L'Oréal",
                "COS",
            ),
            (
                "Máscara de pestañas",
                "Colossal",
                "Máscara de pestañas efecto volumen",
                "69.00",
                70,
                "Cosmética y Belleza",
                "Maybelline",
                "COS",
            ),
            (
                "Labial mate",
                "SuperStay",
                "Labial líquido mate larga duración",
                "59.00",
                80,
                "Cosmética y Belleza",
                "Maybelline",
                "COS",
            ),
            (
                "Crema hidratante facial",
                "HydraBoost",
                "Crema hidratante para todo tipo de piel",
                "79.00",
                60,
                "Cosmética y Belleza",
                "Nivea",
                "COS",
            ),
            (
                "Perfume femenino 50ml",
                "Paris Night",
                "Fragancia femenina floral 50ml",
                "199.00",
                35,
                "Cosmética y Belleza",
                "L'Oréal",
                "COS",
            ),
            # ---------------- Cuidado Personal ----------------
            (
                "Shampoo reparación 400ml",
                "Repair&Care",
                "Shampoo reparador para cabello dañado",
                "39.00",
                100,
                "Cuidado Personal",
                "Pantene",
                "CPR",
            ),
            (
                "Acondicionador 400ml",
                "Repair&Care",
                "Acondicionador reparador para cabello dañado",
                "39.00",
                90,
                "Cuidado Personal",
                "Pantene",
                "CPR",
            ),
            (
                "Jabón líquido corporal 500ml",
                "CreamCare",
                "Jabón líquido hidratante para el cuerpo",
                "35.00",
                120,
                "Cuidado Personal",
                "Dove",
                "CPR",
            ),
            (
                "Desodorante aerosol",
                "Men Extra Fresh",
                "Desodorante masculino 48h protección",
                "29.00",
                150,
                "Cuidado Personal",
                "Dove",
                "CPR",
            ),
            (
                "Crema dental 90g",
                "Total12",
                "Pasta dental protección completa",
                "19.00",
                200,
                "Cuidado Personal",
                "Colgate",
                "CPR",
            ),
            (
                "Máquina de afeitar descartable x3",
                "Blue3",
                "Pack de 3 rasuradoras descartables",
                "25.00",
                180,
                "Cuidado Personal",
                "Gillette",
                "CPR",
            ),
            # ---------------- Supermercado / varios ----------------
            (
                "Gaseosa 2.5L",
                "Original",
                "Gaseosa sabor cola 2.5 litros",
                "18.00",
                100,
                "Supermercado",
                "Coca-Cola",
                "SUP",
            ),
            (
                "Gaseosa 2.5L",
                "Light",
                "Gaseosa sabor cola light 2.5 litros",
                "18.00",
                80,
                "Supermercado",
                "Pepsi",
                "SUP",
            ),
            (
                "Pack galletas surtidas 500g",
                "Surtidas",
                "Pack de galletas surtidas 500g",
                "22.00",
                120,
                "Supermercado",
                "Arcor",
                "SUP",
            ),
            (
                "Leche entera 1L",
                "Entera UHT",
                "Leche entera larga vida 1L",
                "9.00",
                200,
                "Supermercado",
                "Nestlé",
                "SUP",
            ),
            (
                "Café instantáneo 200g",
                "Clásico",
                "Café instantáneo clásico 200g",
                "35.00",
                90,
                "Supermercado",
                "Nestlé",
                "SUP",
            ),
        ]

        creados = 0
        for (
            nombre,
            modelo,
            desc,
            precio,
            stock,
            cat_nom,
            marca_nom,
            pref,
        ) in productos_def:
            cat = cats[cat_nom]
            marca = marcas.get(marca_nom)

            prod, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "codigo": next_codigo(pref),
                    "modelo": modelo,
                    "caracteristicas": desc,
                    "precio": Decimal(precio),
                    "stock": stock,
                    "categoria": cat,
                    "marca": marca,
                    "activo": True,
                },
            )

            if not created:
                changed = False
                if not prod.codigo:
                    prod.codigo = next_codigo(pref)
                    changed = True
                if prod.categoria_id != cat.id:
                    prod.categoria = cat
                    changed = True
                if marca and getattr(prod, "marca_id", None) != marca.id:
                    prod.marca = marca
                    changed = True

                prod.precio = Decimal(precio)
                prod.stock = max(prod.stock or 0, stock)
                prod.modelo = modelo or getattr(prod, "modelo", "")
                prod.caracteristicas = desc or getattr(prod, "caracteristicas", "")
                prod.activo = True
                changed = True

                if changed:
                    prod.save()
            else:
                creados += 1

        self.stdout.write(
            self.style.SUCCESS(f"✔ Catálogo listo. Nuevos productos creados: {creados}")
        )
