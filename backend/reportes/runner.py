# reportes/runner.py
from typing import List, Dict, Any

from .parser import parse_prompt
from .services import (
    consultar_ventas,
    consultar_top_productos,
    consultar_sin_movimiento,
    consultar_stock,
    consultar_stock_bajo,
    consultar_precios,
)
from .logger import log_prompt

# Si quieres seguir usando query_builder como fallback:
try:
    from .query_builder import build_queryset
except Exception:   # pragma: no cover
    build_queryset = None


def _safe_log(user, prompt: str, spec: Dict[str, Any]) -> None:
    """
    Loguea el prompt sin romper el flujo si hay errores.
    """
    try:
        # De momento no tenemos "predicted" separado del parser,
        # así que lo dejamos en None.
        log_prompt(user, prompt, None, spec.get("intent", "ventas"), spec)
    except Exception:
        pass


def run_prompt(prompt: str, user=None, parse_only: bool = False):
    """
    Interpreta un prompt en lenguaje natural y ejecuta el reporte correspondiente.

    Retorna:
      - Si parse_only=True → solo el spec (dict).
      - Si parse_only=False → (spec, headers, rows, warnings)
    """
    spec = parse_prompt(prompt or "")
    _safe_log(user, prompt, spec)

    if parse_only:
        return spec

    intent = spec.get("intent", "ventas")
    headers: List[str] = []
    rows: List[List[Any]] = []
    warnings: List[str] = []

    start_date = spec.get("start_date")
    end_date = spec.get("end_date")
    group_by = spec.get("group_by") or "producto"
    categoria = spec.get("categoria")
    marca = spec.get("marca")
    contiene = spec.get("contiene")
    cliente = spec.get("cliente")
    limit = spec.get("limit")
    threshold = spec.get("threshold")

    # ----------------------------------------
    # 1) Intención: ventas / productos comprados
    # ----------------------------------------
    if intent == "ventas":
        headers, rows = consultar_ventas(
            start_date,
            end_date,
            group_by,
            cliente=cliente,
            contiene=contiene,
        )

    # ----------------------------------------
    # 2) Intención: ranking de productos
    # ----------------------------------------
    elif intent == "top_productos":
        headers, rows = consultar_top_productos(
            start_date,
            end_date,
            limit,
            categoria=categoria,
        )
        if spec.get("order_dir") == "asc":
            # para "menos vendidos": invertimos el orden
            rows = list(reversed(rows))

    # ----------------------------------------
    # 3) Intención: productos sin movimiento
    # ----------------------------------------
    elif intent == "sin_movimiento":
        headers, rows = consultar_sin_movimiento(
            start_date,
            end_date,
            categoria=categoria,
        )

    # ----------------------------------------
    # 4) Intención: stock / stock bajo / precios
    # ----------------------------------------
    elif intent == "stock":
        headers, rows = consultar_stock(
            categoria=categoria,
            marca=marca,
            contiene=contiene,
        )

    elif intent == "stock_bajo":
        headers, rows = consultar_stock_bajo(
            threshold=threshold,
            categoria=categoria,
            limit=limit,
        )

    elif intent == "precios":
        headers, rows = consultar_precios(
            categoria=categoria,
            marca=marca,
            contiene=contiene,
        )

    # ----------------------------------------
    # 5) Fallback / casos no contemplados
    # ----------------------------------------
    else:
        if build_queryset is not None:
            try:
                headers, rows = build_queryset(spec)
            except Exception as e:
                warnings.append(
                    f"No supe cómo construir un reporte específico para la intención '{intent}'. "
                    f"Detalle: {e}"
                )
        else:
            warnings.append(
                f"No existe implementación para la intención '{intent}'. "
                "Devuelvo un resultado vacío."
            )

    return spec, headers, rows, warnings
