# analitica/services.py
from __future__ import annotations

from datetime import timedelta, date
from typing import List, Dict, Any, Optional, Tuple

from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate

from ventas.models import Venta, ItemVenta
from catalogo.models import Producto


# ============================
# Helpers de fechas / periodos
# ============================

def _resolve_period_days(period: str | None) -> int:
    """
    Convierte un código de periodo a cantidad de días.

    - 7d   → 7 días
    - 30d  → 30 días (default)
    - 365d → 365 días
    """
    if not period:
        return 30
    period = period.lower()
    if period == "7d":
        return 7
    if period == "365d":
        return 365
    return 30


def _daterange(start: date, days: int) -> List[date]:
    return [start + timedelta(days=i) for i in range(days)]


# ============================
# Serie diaria de ventas
# ============================

def get_daily_sales_series(
    days_back: int,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Devuelve la serie de ventas diarias (total Bs) de los últimos `days_back` días.

    Filtros opcionales:
      - product_id  → solo ventas de ese producto
      - category_id → solo productos de esa categoría
    """
    today = timezone.now().date()
    start_date = today - timedelta(days=days_back - 1)

    qs = Venta.objects.filter(
        estado="pagada",
        creado_en__date__gte=start_date,
        creado_en__date__lte=today,
    )

    if product_id:
        qs = qs.filter(items__producto_id=product_id)

    if category_id:
        qs = qs.filter(items__producto__categoria_id=category_id)

    # Agregamos por día
    daily = (
        qs.annotate(dia=TruncDate("creado_en"))
        .values("dia")
        .annotate(total=Sum("total"))
        .order_by("dia")
    )

    mapping = {item["dia"]: float(item["total"] or 0.0) for item in daily}

    # Aseguramos continuidad de fechas (aunque un día no tenga ventas)
    serie: List[Dict[str, Any]] = []
    for d in _daterange(start_date, days_back):
        serie.append(
            {
                "fecha": d.strftime("%Y-%m-%d"),
                "total": float(mapping.get(d, 0.0)),
            }
        )
    return serie


def get_daily_product_series(
    product_id: int,
    days_back: int,
) -> Dict[str, Any]:
    """
    Serie diaria de un producto específico:
    - cantidad vendida
    - total en Bs
    """
    today = timezone.now().date()
    start_date = today - timedelta(days=days_back - 1)

    qs = (
        ItemVenta.objects.select_related("venta", "producto")
        .filter(
            venta__estado="pagada",
            venta__creado_en__date__gte=start_date,
            venta__creado_en__date__lte=today,
            producto_id=product_id,
        )
    )

    agg = (
        qs.annotate(dia=TruncDate("venta__creado_en"))
        .values("dia")
        .annotate(
            cantidad=Sum("cantidad"),
            total=Sum("subtotal"),
        )
        .order_by("dia")
    )

    by_day = {
        item["dia"]: {
            "cantidad": int(item["cantidad"] or 0),
            "total": float(item["total"] or 0.0),
        }
        for item in agg
    }

    serie: List[Dict[str, Any]] = []
    for d in _daterange(start_date, days_back):
        info = by_day.get(d, {"cantidad": 0, "total": 0.0})
        serie.append(
            {
                "fecha": d.strftime("%Y-%m-%d"),
                "cantidad": info["cantidad"],
                "total": info["total"],
            }
        )

    try:
        prod = Producto.objects.get(pk=product_id)
        nombre = prod.nombre
    except Producto.DoesNotExist:
        nombre = ""

    return {
        "producto_id": product_id,
        "producto_nombre": nombre,
        "serie": serie,
    }


# ============================
# Modelo de regresión lineal
# ============================

def _linear_regression_xy(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    """
    Ajuste lineal simple y = a*x + b.
    Devuelve (a, b). Si la varianza de xs es 0 → a = 0.
    """
    n = len(xs)
    if n == 0:
        return 0.0, 0.0

    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs) or 1.0

    a = num / den
    b = mean_y - a * mean_x
    return float(a), float(b)


def generate_sales_predictions(
    period: str = "30d",
    days_override: Optional[int] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Genera predicciones diarias de ventas totales usando regresión lineal sobre
    la serie histórica, opcionalmente filtrada por producto / categoría.

    - period: "7d" | "30d" | "365d" (define horizonte de predicción)
    - days_override: si se pasa, se usa como cantidad de días a predecir.
    """
    days_pred = days_override or _resolve_period_days(period)
    days_train = max(90, days_pred)

    # Serie histórica para entrenamiento (ya filtrada)
    serie = get_daily_sales_series(
        days_back=days_train,
        product_id=product_id,
        category_id=category_id,
    )

    ys = [p["total"] for p in serie]
    xs = list(range(len(ys)))

    if len(ys) < 5:
        # Muy pocos datos → predicción = promedio plano
        avg = sum(ys) / len(ys) if ys else 0.0
        today = timezone.now().date()
        return [
            {
                "fecha": (today + timedelta(days=i + 1)).strftime("%Y-%m-%d"),
                "prediccion": float(max(0.0, avg)),
            }
            for i in range(days_pred)
        ]

    a, b = _linear_regression_xy(xs, ys)

    last_date = timezone.now().date()
    preds: List[Dict[str, Any]] = []

    for i in range(days_pred):
        x = len(ys) + i
        y_hat = a * x + b
        # No permitimos valores negativos
        y_hat = max(0.0, float(y_hat))
        d = last_date + timedelta(days=i + 1)
        preds.append(
            {
                "fecha": d.strftime("%Y-%m-%d"),
                "prediccion": y_hat,
            }
        )

    return preds
