# reportes/parser.py
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from django.conf import settings

try:
    import joblib
except Exception:
    joblib = None

# ------------------------------
# Utiles de fecha (simple)
# ------------------------------
SPANISH_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

def _ultimo_dia_mes(mes: int, year: int) -> int:
    if mes in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if mes == 2:
        # suficiente para reportes (no necesitamos calendario exacto de bisiesto)
        return 29
    return 30

def _norm_fecha(s: str) -> str:
    """
    Normaliza "DD/MM/YYYY" a "YYYY-MM-DD".
    Si ya está en formato ISO, lo deja igual.
    """
    s = s.strip()
    if "/" in s and len(s.split("/")) == 3:
        d, m, y = s.split("/")
        d = d.zfill(2)
        m = m.zfill(2)
        return f"{y}-{m}-{d}"
    return s  # ya está YYYY-MM-DD

# ------------------------------
# Cargador del modelo IA (opcional)
# ------------------------------
_MODEL = None

def _load_model():
    """Carga ia/prompt_intent_model.joblib si existe (silencioso)."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if not joblib:
        return None
    path = os.path.join(settings.BASE_DIR, "ia", "prompt_intent_model.joblib")
    if os.path.exists(path):
        try:
            _MODEL = joblib.load(path)
        except Exception:
            _MODEL = None
    return _MODEL

# ------------------------------
# Parser principal
# ------------------------------
def parse_prompt(prompt: str) -> Dict[str, Any]:
    """
    Devuelve un dict con:
     - intent: ventas | stock | stock_bajo | precios | top_productos | sin_movimiento | agregar_carrito
     - group_by: 'producto' | 'cliente' | 'categoria'
     - start_date, end_date (YYYY-MM-DD o None)
     - format: pantalla | pdf | excel
     - limit, threshold
     - categoria, marca, contiene, cliente
     - order_by, order_dir (para top/menos vendidos)
    """
    p = (prompt or "").lower().strip()

    out: Dict[str, Any] = {
        "intent": "ventas",
        "group_by": "producto",
        "start_date": None,
        "end_date": None,
        "format": "pantalla",
        "limit": None,
        "threshold": None,
        "categoria": None,
        "marca": None,
        "contiene": None,
        "cliente": None,
        "order_by": None,
        "order_dir": None,
    }

    # ---- 0) INTENCIÓN ESPECIAL: agregar al carrito ----
    # ejemplos: "agrega 2 licuadoras al carrito", "quiero 3 mouse gamer a la compra"
    if re.search(r"\b(agrega|añade|quiero|pon|mete)\b", p) and re.search(r"\b(carrito|compra|pedido)\b", p):
        out["intent"] = "agregar_carrito"
        m_prod = re.search(
            r"(?:agrega|añade|quiero|pon|mete)\s+(?:(\d+)\s+)?(.+?)\s+(?:al|a la)\s+(?:carrito|compra|pedido)",
            p
        )
        if m_prod:
            out["limit"] = int(m_prod.group(1) or 1)         # cantidad
            out["contiene"] = m_prod.group(2).strip()        # nombre del producto
        return out  # retornamos de inmediato

    # ---- 1) IA: clasifica intención si hay modelo entrenado ----
    model = _load_model()
    if model is not None:
        try:
            proba = model.predict_proba([p])[0]
            labels = model.classes_
            top_i = int(proba.argmax())
            if proba[top_i] >= 0.60:  # umbral de confianza
                out["intent"] = labels[top_i]
        except Exception:
            pass

    # ---- 2) Reglas complementarias / override ----
    # "compras" se considera ventas (sin cambiar el intent si IA ya puso otro)
    if re.search(r"\b(compra|compras|orden(es)?)\b", p):
        out["intent"] = "ventas"

    if re.search(r"\b(precio|precios|lista de precios)\b", p):
        out["intent"] = "precios"

    elif re.search(r"\b(stock|inventario|existenc)\b", p):
        out["intent"] = "stock"
        if re.search(r"\b(poco|bajo|menor|reponer|renovar)\b.*\bstock\b", p) or \
           re.search(r"\bstock\s+(bajo|menor|crítico|critico)\b", p):
            out["intent"] = "stock_bajo"

    elif re.search(r"(m[aá]s\s+vendid|top\s*\d+|ranking|estrella|populares)", p):
        out["intent"] = "top_productos"

    elif re.search(r"(sin venta|no se vendi[oó]|sin movimiento|no vendidos)", p):
        out["intent"] = "sin_movimiento"
    
    elif re.search(r"(menos\s+vendid)", p):
        # Top invertido: queremos los menos vendidos
        out["intent"] = "top_productos"
        out["order_by"] = "unidades"
        out["order_dir"] = "asc"

    # ---- 3) Fechas ----
    # formato explícito "del DD/MM/YYYY al DD/MM/YYYY" (o YYYY-MM-DD)
    r = re.search(
        r"del\s+(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})\s+al\s+(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
        p
    )
    if r:
        out["start_date"] = _norm_fecha(r.group(1))
        out["end_date"] = _norm_fecha(r.group(2))
    else:
        # fechas sueltas
        fechas = re.findall(r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})", p)
        if len(fechas) >= 1:
            out["start_date"] = _norm_fecha(fechas[0])
        if len(fechas) >= 2:
            out["end_date"] = _norm_fecha(fechas[1])

        # "mes de septiembre", "mensual de octubre"
        if not out["start_date"] and ("mes de " in p or "mensual" in p):
            m = re.search(r"mes de ([a-zñ]+)", p)
            if m:
                month_name = m.group(1)
                mes = SPANISH_MONTHS.get(month_name)
                if mes:
                    year = datetime.now().year
                    out["start_date"] = f"{year}-{mes:02d}-01"
                    out["end_date"] = f"{year}-{mes:02d}-{_ultimo_dia_mes(mes, year):02d}"

        # "este mes"
        if "este mes" in p and not out["start_date"]:
            today = datetime.now().date()
            out["start_date"] = today.replace(day=1).strftime("%Y-%m-%d")
            out["end_date"] = today.strftime("%Y-%m-%d")

        # "hoy"
        if "hoy" in p and not out["start_date"]:
            today = datetime.now().date().strftime("%Y-%m-%d")
            out["start_date"] = today
            out["end_date"] = today

        # "ayer"
        if "ayer" in p and not out["start_date"]:
            d = datetime.now().date() - timedelta(days=1)
            out["start_date"] = d.strftime("%Y-%m-%d")
            out["end_date"] = d.strftime("%Y-%m-%d")

        # "último mes", "mes pasado" (dejamos que el builder use fallback 30 días si no se setea)
        if ("último mes" in p or "ultimo mes" in p or "mes pasado" in p) and not out["start_date"]:
            # sin setear: el service / builder aplica fallback (últimos 30 días)
            pass

    # ---- 4) Formato ----
    if "pdf" in p:
        out["format"] = "pdf"
    elif "excel" in p or "xlsx" in p:
        out["format"] = "excel"
    else:
        out["format"] = "pantalla"

    # ---- 5) Limit (top) ----
    mtop = re.search(r"\btop\s+(\d{1,3})\b", p)
    if mtop:
        out["limit"] = int(mtop.group(1))
    if out["limit"] is None:
        mcount = re.search(r"\b(?:los\s+)?(\d{1,3})\s+(?:productos?|items?)\b", p)
        if mcount:
            out["limit"] = int(mcount.group(1))

    # ---- 6) Threshold (para stock bajo) ----
    mth = re.search(r"(?:menor(?:\s*a)?|<)\s*(\d{1,6})", p)
    if mth:
        out["threshold"] = int(
            mth.group(2) if mth.lastindex and mth.group(2) else mth.group(1)
        )

    # ---- 7) Filtros simples (categoría, marca, nombre de producto) ----
    mc = re.search(r"categor[ií]a\s+([a-z0-9áéíóúñ \-_/]+)", p)
    if mc:
        out["categoria"] = mc.group(1).strip()

    mm = re.search(r"marca\s+([a-z0-9áéíóúñ \-_/]+)", p)
    if mm:
        out["marca"] = mm.group(1).strip()

    mn = re.search(r"(?:que\s+contenga|contiene|con\s+nombre)\s+([a-z0-9áéíóúñ \-_/]+)", p)
    if mn:
        out["contiene"] = mn.group(1).strip()

    # ---- 8) Filtro por cliente (nombre / doc) ----
    # ejemplos:
    #   "del cliente juan perez"
    #   "para el cliente carlos"
    #   "ventas del cliente maria en este mes"
    mcli = re.search(r"(?:del|de|para(?:\s+el)?)\s+cliente\s+([a-z0-9áéíóúñ ]{2,})", p)
    if mcli:
        raw = mcli.group(1).strip()
        # cortamos en palabras típicas que marcan el fin del nombre
        raw = re.split(r"\s+(?:en|del|de|desde|hasta|al|por|y|con|que|mes|año|anio)\b", raw)[0].strip()
        if raw:
            out["cliente"] = raw

    # ---- 9) Orden (legacy: por si lo necesitas desde services) ----
    if re.search(r"(menor a mayor|ascendente|asc\b)", p):
        out["order_dir"] = "asc"
    elif re.search(r"(mayor a menor|descendente|desc\b)", p):
        out["order_dir"] = "desc"

    if re.search(r"ordenad[oa]s?\s+por\s+stock", p):
        out["order_by"] = "stock"

    # ---- 10) Agrupación (group_by) ----
    # "por cliente", "por categoría", "por producto"
    if re.search(r"por\s+cliente", p):
        out["group_by"] = "cliente"
    elif re.search(r"por\s+categori", p):
        out["group_by"] = "categoria"
    elif re.search(r"por\s+producto", p):
        out["group_by"] = "producto"
    # (default ya es "producto")

    return out
