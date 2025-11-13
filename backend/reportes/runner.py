# reportes/runner.py
from typing import Tuple, List, Dict, Any
from .intent_parser import parse_prompt_to_spec
from .query_builder import build_queryset
from .queries_extra import productos_sin_movimiento
from .services import consultar_stock, consultar_stock_bajo, consultar_precios

# ---- Adaptador Spec -> dict (para el builder actual)
def _spec_to_dict(spec) -> Dict[str, Any]:
    return {
        "intent": spec.intent,
        "metrics": list(spec.metrics or []),
        "dimensions": list(spec.dimensions or []),
        "start_date": spec.start_date,
        "end_date": spec.end_date,
        "filters": [f.__dict__ for f in (spec.filters or [])],
        "order_by": spec.order_by,
        "order_dir": spec.order_dir,
        "limit": spec.limit,
        "format": spec.format,
    }

def run_prompt(prompt: str, parse_only: bool = False) -> Tuple[Dict[str, Any], List[str], List[List], List[str]]:
    """
    Traduce el prompt → Spec robusta y ejecuta.
    Devuelve: (spec_dict, headers, rows, warnings)
    """
    spec, warnings = parse_prompt_to_spec(prompt)

    # --- Normalizaciones útiles antes de ejecutar ---
    # 1) "top productos" => asegurar dimensión, orden y límite por defecto
    if spec.intent in ("top_productos",) and ("producto" not in (spec.dimensions or [])):
        spec.dimensions = (spec.dimensions or []) + ["producto"]
    if spec.intent in ("top_productos",) and not spec.order_by:
        spec.order_by = ["-unidades"]   # más vendidos
    # si no llegó limit explícito, deja que el parser lo haya puesto; si no, no forzamos 3

    # 2) Si pide ventas sin dimensiones, deja que builder agregue métricas por defecto
    #    (no hace falta nada aquí)

    # Parse only
    if parse_only:
        return _spec_to_dict(spec)

    # ---- Intenciones no "ventas" (usan services existentes) ----
    if spec.intent == "stock":
        headers, rows = consultar_stock(
            next((f.value for f in spec.filters if f.field == "categoria"), None),
            next((f.value for f in spec.filters if f.field == "marca"), None),
            next((f.value for f in spec.filters if f.field == "producto"), None),
        )
        if spec.order_by == "stock":
            rows.sort(key=lambda r: r[-1], reverse=(spec.order_dir == "desc"))

    elif spec.intent == "stock_bajo":
        threshold = None
        for f in spec.filters:
            if f.field in ("stock", "cantidad") and f.op in ("lt", "lte"):
                threshold = f.value
        headers, rows = consultar_stock_bajo(
            threshold,
            next((f.value for f in spec.filters if f.field == "categoria"), None),
            spec.limit,
        )

    elif spec.intent == "precios":
        headers, rows = consultar_precios(
            next((f.value for f in spec.filters if f.field == "categoria"), None),
            next((f.value for f in spec.filters if f.field == "marca"), None),
            next((f.value for f in spec.filters if f.field == "producto"), None),
        )

    elif spec.intent == "sin_movimiento":
        headers, rows = productos_sin_movimiento(
            spec.start_date,
            spec.end_date,
            next((f.value for f in spec.filters if f.field == "categoria"), None),
        )

    else:
        # ---- Ventas / Top productos con el builder (que espera dict) ----
        spec_dict = _spec_to_dict(spec)
        headers, rows = build_queryset(spec_dict)

    return _spec_to_dict(spec), headers, rows, warnings
