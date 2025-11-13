# reportes/query_builder.py
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

from django.db.models import Sum, Value
from django.db.models.functions import (
    TruncDay, TruncMonth, TruncWeek, Coalesce, ExtractQuarter
)

from ventas.models import ItemVenta  # ventas_itemventa
# Venta: cliente(FK), fecha(DateTime/Date), estado('Pagada'/'Pendiente'/...), total (Decimal)
# ItemVenta: venta(FK), producto(FK), cantidad, subtotal, precio_unit
# Producto: categoria(FK), marca(FK), nombre

# -----------------------------
# Helpers
# -----------------------------
def _fallback_dates(start: str | None, end: str | None) -> Tuple[datetime, datetime]:
    if start and end:
        # admite ISO "YYYY-MM-DD" o "YYYY-MM-DDTHH:MM:SS"
        try:
            return datetime.fromisoformat(start), datetime.fromisoformat(end)
        except Exception:
            pass
    hoy = datetime.now()
    return hoy - timedelta(days=30), hoy


# Dimensiones soportadas (valor ORM o función de trunc)
DIM_MAP: Dict[str, Tuple[Any, str]] = {
    # Entidades
    "cliente":   ("venta__cliente__nombre", "Cliente"),
    "producto":  ("producto__nombre",       "Producto"),
    "categoria": ("producto__categoria__nombre", "Categoría"),
    "marca":     ("producto__marca__nombre",     "Marca"),

    # Tiempo
    "fecha_dia": (TruncDay("venta__creado_en"),     "Fecha"),
    "fecha_mes": (TruncMonth("venta__creado_en"),   "Mes"),
    "semana":    (TruncWeek("venta__creado_en"),    "Semana"),
    "trimestre": (ExtractQuarter("venta__creado_en"), "Trimestre"),  # 1..4
}

def _has_product_dims(dims: List[str]) -> bool:
    """¿La consulta agrupa por algo del producto? (producto/categoria/marca)"""
    return any(d in {"producto", "categoria", "marca"} for d in dims)


# -----------------------------
# Builder principal
# -----------------------------
def build_queryset(spec: Dict[str, Any]) -> Tuple[List[str], List[List]]:
    intent: str = spec.get("intent") or "ventas"
    dims: List[str] = list(spec.get("dimensions") or [])
    metrics: List[str] = list(spec.get("metrics") or [])
    start = spec.get("start_date")
    end = spec.get("end_date")
    order_by = spec.get("order_by")
    order_dir = spec.get("order_dir")
    limit = spec.get("limit")

    # 1) Base QS: solo ventas confirmadas
    base = (
        ItemVenta.objects
        .select_related(
            "venta",
            "venta__cliente",
            "producto",
            "producto__categoria",
            "producto__marca",
        )
        .filter(venta__estado__iexact="Pagada")
    )

    # 2) Fechas (fallback 30 días)
    dini, dfin = _fallback_dates(start, end)
    base = base.filter(
        venta__creado_en__date__gte=dini.date(),
        venta__creado_en__date__lte=dfin.date()
    )

    # 3) Auto-ajustes por intent
    if intent == "top_productos":
        if "producto" not in dims:
            if "categoria" in dims:
                dims = ["categoria", "producto"]
            else:
                dims = ["producto"]

    # 4) Dimensiones por defecto
    if not dims:
        dims = ["producto"] if intent in ("top_productos",) else ["cliente"]

    # 5) Métricas por defecto
    if not metrics:
        metrics = ["unidades", "monto_total"]

    # 6) Dimensiones → values()/annotate()
    values_fields: List[str] = []
    headers: List[str] = []
    for d in dims:
        dm = DIM_MAP.get(d)
        if not dm:
            # ignora dimensiones desconocidas
            continue
        field_or_func, header = dm
        headers.append(header)
        if callable(field_or_func):
            alias = f"__{d}__"
            base = base.annotate(**{alias: field_or_func})
            values_fields.append(alias)
        else:
            values_fields.append(field_or_func)

    qs = base.values(*values_fields)

    # 7) Métricas (monto_total vs subtotal; unidades)
    product_dims = _has_product_dims(dims)
    ann = {}
    for m in metrics:
        key = m.lower()
        if key in {"monto", "monto_total", "importe", "total", "facturacion", "facturación", "ventas"}:
            if product_dims:
                # Si agrupas por producto/categoría/marca → usar subtotal de ítems
                ann["monto_total"] = Coalesce(Sum("subtotal"), Value(0))
            else:
                # Si NO agrupas por producto → sumar total de la venta (sin duplicar por ítems)
                ann["monto_total"] = Coalesce(Sum("venta__total", distinct=True), Value(0))
        elif key in {"unidades", "cantidad", "cantidad_total", "items", "items_vendidos", "stock", "existencias", "inventario"}:
            ann["unidades"] = Coalesce(Sum("cantidad"), Value(0))
        else:
            continue

    if ann:
        qs = qs.annotate(**ann)

    # 8) Headers: primero dims, luego métricas normalizadas
    metric_headers_ordered: List[str] = []
    if "unidades" in ann:
        metric_headers_ordered.append("Cantidad")
    if "monto_total" in ann:
        metric_headers_ordered.append("Monto Total")

    # Mapea cualquier alias pedido a header amigable
    requested_map = {
        "unidades": "Cantidad",
        "cantidad": "Cantidad",
        "cantidad_total": "Cantidad",
        "items": "Cantidad",
        "items_vendidos": "Cantidad",
        "stock": "Cantidad",
        "existencias": "Cantidad",
        "inventario": "Cantidad",
        "monto_total": "Monto Total",
        "monto": "Monto Total",
        "total": "Monto Total",
        "importe": "Monto Total",
        "facturación": "Monto Total",
        "facturacion": "Monto Total",
        "ventas": "Monto Total",
    }
    for req in metrics:
        lbl = requested_map.get(req.lower())
        if lbl and lbl not in metric_headers_ordered:
            metric_headers_ordered.append(lbl)

    headers.extend(metric_headers_ordered)

    # 9) Orden
    order_fields: List[str] = []
    if order_by:
        if isinstance(order_by, str):
            order_by = [order_by]
        for ob in order_by:
            desc = ob.startswith("-")
            key = ob[1:] if desc else ob
            if key in {"unidades", "monto", "monto_total", "total", "importe"}:
                metric_key = "monto_total" if key in {"monto", "monto_total", "total", "importe"} else "unidades"
                expr = f"-{metric_key}" if desc or (order_dir == "desc") else metric_key
                order_fields.append(expr)
            elif key in dims:
                idx = dims.index(key)
                vf = values_fields[idx]
                expr = f"-{vf}" if desc or (order_dir == "desc") else vf
                order_fields.append(expr)

    if not order_fields:
        # defaults por intent
        if intent == "top_productos":
            order_fields = ["-unidades"]
        else:
            order_fields = ["-monto_total"] if "monto_total" in ann else []

    if order_fields:
        qs = qs.order_by(*order_fields)

    # 10) Límite
    if limit:
        qs = qs[: int(limit)]

    # 11) Construir filas
    rows: List[List] = []
    for item in qs:
        row = []
        # dimensiones
        for i, _d in enumerate(dims):
            alias = values_fields[i]
            row.append(item.get(alias))
        # métricas en el orden de headers de métricas
        for mh in metric_headers_ordered:
            if mh == "Cantidad":
                row.append(item.get("unidades", 0))
            elif mh == "Monto Total":
                row.append(item.get("monto_total", 0))
            else:
                row.append(item.get(mh, 0))
        rows.append(row)

    return headers, rows
