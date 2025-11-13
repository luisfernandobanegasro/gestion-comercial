# reportes/catalog.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class Dimension:
    key: str
    label: str
    orm_path: str  # ruta válida desde ItemVenta (o alias anotado en query_builder)

@dataclass(frozen=True)
class Metric:
    key: str
    label: str

DIMENSIONS: Dict[str, Dimension] = {
    # ItemVenta -> producto__nombre
    "producto":   Dimension("producto",   "Producto",   "producto__nombre"),
    # ItemVenta -> venta__cliente__nombre
    "cliente":    Dimension("cliente",    "Cliente",    "venta__cliente__nombre"),
    # ItemVenta -> producto__categoria__nombre
    "categoria":  Dimension("categoria",  "Categoría",  "producto__categoria__nombre"),
    # ItemVenta -> producto__marca__nombre
    "marca":      Dimension("marca",      "Marca",      "producto__marca__nombre"),

    # Tiempo (se anotan en query_builder)
    "dia":           Dimension("dia",            "Día",        "dia"),
    "mes":           Dimension("mes",            "Mes",        "mes"),
    "anio":          Dimension("anio",           "Año",        "anio"),
    "semana":        Dimension("semana",         "Semana",     "semana"),      # TruncWeek
    "trimestre":     Dimension("trimestre",      "Trimestre",  "trimestre"),   # ExtractQuarter

    # Alias “directos” que ya estabas usando
    "fecha_dia":     Dimension("fecha_dia",      "Fecha",      "fecha_dia"),
    "fecha_mes":     Dimension("fecha_mes",      "Mes",        "fecha_mes"),
}

METRICS: Dict[str, Metric] = {
    # Ventas
    "monto_total":      Metric("monto_total",      "Monto total"),
    "monto":            Metric("monto",            "Monto total"),
    "cantidad_total":   Metric("cantidad_total",   "Cantidad total"),
    "unidades":         Metric("unidades",         "Cantidad total"),
    "num_ventas":       Metric("num_ventas",       "Número de ventas"),
    "ticket_promedio":  Metric("ticket_promedio",  "Ticket promedio"),
}

# -----------------------------
# Sinónimos ampliados
# -----------------------------
SYNONYMS_DIM: Dict[str, List[str]] = {
    "producto": [
        "producto", "productos", "articulo", "artículos", "item", "ítem", "items", "ítems",
        "referencia", "sku", "mercadería", "mercaderia", "bien"
    ],
    "cliente": [
        "cliente", "clientes", "comprador", "compradores", "persona", "personas",
        "titular", "titulares", "usuario", "usuarios", "consumidor", "consumidores",
        "account", "cuenta"
    ],
    "categoria": [
        "categoria", "categoría", "categorias", "categorías", "rubro", "rubros",
        "familia", "familias", "grupo", "grupos", "segmento", "segmentos"
    ],
    "marca": [
        "marca", "marcas", "fabricante", "fabricantes", "brand", "brands"
    ],
    # Tiempo
    "dia": [
        "dia", "día", "diario", "diaria", "diarios", "daily", "jornada", "fecha"
    ],
    "mes": [
        "mes", "meses", "mensual", "mensuales", "monthly", "periodo", "período", "mensualmente"
    ],
    "anio": [
        "año", "años", "anio", "year", "yearly", "anual", "anualmente"
    ],
    "semana": [
        "semana", "semanal", "semanas", "weekly", "por semana", "sem.",
    ],
    "trimestre": [
        "trimestre", "trimestral", "trimestres", "quarter", "quarterly", "por trimestre"
    ],
    # Alias previos
    "fecha_dia": [
        "fecha", "por dia", "por día", "día a día", "diario", "calendar day"
    ],
    "fecha_mes": [
        "por mes", "mensual", "mes a mes", "mensualmente", "monthly"
    ],
}

SYNONYMS_MET: Dict[str, List[str]] = {
    # --- Monto ---
    "monto_total": [
        "monto_total", "monto", "importe", "total", "ventas", "facturación", "facturacion",
        "ingresos", "recaudacion", "recaudación", "bruto", "neto", "importe_total",
        "suma", "sumatoria", "total_vendido", "total_ventas"
    ],
    "monto": [  # alias directo
        "monto", "importe", "total", "ventas", "facturación", "facturacion", "ingresos",
        "recaudacion", "recaudación", "monto_total"
    ],

    # --- Cantidad / Unidades ---
    # OJO: aquí incluimos “stock” como sinónimo de cantidad (cuando se use en reportes
    # de ventas). Si quisieras consultar inventario real, eso es otro endpoint.
    "cantidad_total": [
        "cantidad_total", "cantidad", "cantidades", "unidades", "items", "ítems",
        "items_vendidos", "unidades_vendidas", "volumen", "volumen_vendido",
        "stock", "existencias", "existencia", "inventario", "qty", "cantidad vendida"
    ],
    "unidades": [
        "unidades", "cantidad", "cantidades", "items", "ítems", "unidades_vendidas",
        "volumen", "volumen_vendido", "stock", "existencias", "inventario", "qty"
    ],

    # --- Número de ventas (transacciones / tickets) ---
    "num_ventas": [
        "número de ventas", "num_ventas", "ventas realizadas", "cantidad de ventas",
        "tickets", "transacciones", "ordenes", "órdenes", "pedidos"
    ],

    # --- Ticket promedio ---
    "ticket_promedio": [
        "ticket promedio", "ticket_promedio", "promedio", "avg", "importe_promedio",
        "venta_promedio", "ticket medio", "ticket_medio", "average ticket"
    ],
}
