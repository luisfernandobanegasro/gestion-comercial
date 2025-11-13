# ia/dataset.py
import os, csv
from typing import List, Tuple
from django.conf import settings

# dataset base (semillas)
BASE_DATA: List[Tuple[str, str]] = [
    ("reporte de ventas del mes pasado", "ventas"),
    ("ventas por producto en septiembre", "ventas"),
    ("ventas por cliente del 01/09/2025 al 30/09/2025", "ventas"),
    ("ventas por categoría en excel", "ventas"),
    ("reporte de ventas por mes", "ventas"),
    ("ver inventario", "stock"),
    ("lista de stock por categoria", "stock"),
    ("mostrar stock de productos gamer", "stock"),
    ("reporte de inventario por marca", "stock"),
    ("productos con poco stock", "stock_bajo"),
    ("stock menor a 10 unidades", "stock_bajo"),
    ("reponer productos con stock bajo", "stock_bajo"),
    ("productos con stock por debajo del mínimo", "stock_bajo"),
    ("lista de precios", "precios"),
    ("precios por categoría", "precios"),
    ("catálogo de precios en excel", "precios"),
    ("precios de productos gamer", "precios"),
    ("top 10 productos más vendidos", "top_productos"),
    ("ranking de productos en ventas", "top_productos"),
    ("los más vendidos del mes", "top_productos"),
    ("productos sin ventas", "sin_movimiento"),
    ("artículos sin movimiento en septiembre", "sin_movimiento"),
    ("no se han vendido estos productos", "sin_movimiento"),
    ("productos que no se vendieron el mes pasado", "sin_movimiento"),
]

CSV_PATH = os.path.join(settings.BASE_DIR, "ia", "training_data.csv")

def read_incremental_csv() -> List[Tuple[str, str]]:
    """
    Lee ejemplos etiquetados manualmente desde ia/training_data.csv
    Formato CSV sin cabecera: "texto","etiqueta"
    """
    if not os.path.exists(CSV_PATH):
        return []
    out: List[Tuple[str, str]] = []
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        for row in r:
            if len(row) >= 2:
                text = row[0].strip()
                label = row[1].strip()
                if text and label:
                    out.append((text, label))
    return out

def get_full_dataset() -> List[Tuple[str, str]]:
    return BASE_DATA + read_incremental_csv()
