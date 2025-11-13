# reportes/intent_parser.py
import re
import unicodedata
from typing import Tuple, List
from rapidfuzz import process, fuzz
import dateparser

from .dsl import Spec, Filter, parse_relative, RELATIVE_KEYWORDS
from .catalog import SYNONYMS_DIM, SYNONYMS_MET, DIMENSIONS, METRICS

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def _clean(t: str) -> str:
    t = (t or "").lower().strip()
    t = _strip_accents(t)
    t = re.sub(r"[^a-z0-9/_\-\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

PLURAL_DIM_MAP = {
    "clientes": "cliente",
    "productos": "producto",
    "categorias": "categoria",
    "marcas": "marca",
    "meses": "fecha_mes",
    "dias": "fecha_dia",
    "semanas": "fecha_semana",
}

def _singular_dim(tok: str) -> str:
    t = _clean(tok)
    if t in PLURAL_DIM_MAP:
        return PLURAL_DIM_MAP[t]
    if t.endswith("s") and t[:-1] in DIMENSIONS:
        return t[:-1]
    return t

def _best_key(token: str, mapping: dict, cutoff=80):
    token = _clean(token)
    if not token:
        return None
    pairs = []
    for k, arr in mapping.items():
        for s in [k] + list(arr or []):
            pairs.append((k, _clean(s)))
    choices = [p[1] for p in pairs if p[1]]
    if not choices:
        return None
    m = process.extractOne(token, choices, scorer=fuzz.WRatio, score_cutoff=cutoff)
    if not m:
        return None
    matched = m[0]
    for k, s in pairs:
        if s == matched:
            return k
    return None

def _relative_range(text: str):
    p = _clean(text)

    if re.search(r"\b(ultimo mes|mes pasado)\b", p):
        a = dateparser.parse("first day of previous month")
        b = dateparser.parse("last day of previous month")
        return a.date().isoformat(), b.date().isoformat()

    if "este mes" in p:
        a = dateparser.parse("first day of this month")
        b = dateparser.parse("today")
        return a.date().isoformat(), b.date().isoformat()

    m = re.search(r"ultimos\s+(\d{1,3})\s+(dias|mes|meses)", p)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit.startswith("dia"):
            a = dateparser.parse(f"{n} days ago")
            b = dateparser.parse("today")
        else:
            a = dateparser.parse(f"{n} months ago")
            b = dateparser.parse("today")
        return a.date().isoformat(), b.date().isoformat()

    m2 = re.search(r"mes de ([a-z]+)(?: (\d{4}))?", p)
    if m2:
        month = m2.group(1)
        year = m2.group(2) or str(dateparser.parse("today").year)
        a = dateparser.parse(f"first day of {month} {year}", languages=["es"])
        b = dateparser.parse(f"last day of {month} {year}", languages=["es"])
        if a and b:
            return a.date().isoformat(), b.date().isoformat()

    return None, None

def parse_prompt_to_spec(prompt: str) -> Tuple[Spec, list]:
    p_raw = (prompt or "").strip()
    p = _clean(p_raw)

    spec = Spec()
    warnings: List[str] = []

    # formato
    if "pdf" in p:
        spec.format = "pdf"
    elif "excel" in p or "xlsx" in p:
        spec.format = "excel"

    # intención (ventas por defecto)
    if re.search(r"\b(stock|inventario)\b", p):
        spec.intent = "stock"
    elif re.search(r"\b(precio|lista de precio|lista de precios)\b", p):
        spec.intent = "precios"
    elif re.search(r"\b(sin venta|no se vendio|sin movimiento)\b", p):
        spec.intent = "sin_movimiento"
    elif re.search(r"\b(top|ranking|mas vendido|mas vendidos)\b", p):
        spec.intent = "top"
    else:
        spec.intent = "ventas"

    # métricas detectadas (si no hay, fijaremos una por defecto abajo)
    mets = []
    for tk in re.findall(r"[a-z0-9/_\-]{3,}", p):
        k = _best_key(tk, SYNONYMS_MET)
        if k and k in METRICS and k not in mets:
            mets.append(k)
    if mets:
        spec.metrics = mets

    # dimensiones
    dims = []
    m_dims = re.search(r"(?:por|agrupado por|agrupados por|group by)\s+([a-z0-9/_\-, y\s]+)", p)
    if m_dims:
        raw = m_dims.group(1)
        parts = [t.strip() for t in re.split(r"[,\s]y\s|,", raw)]
        if len(parts) == 1:
            parts = [t for t in re.split(r"[,\s]+", raw) if t]
        for t in parts:
            t = _singular_dim(t)
            k = _best_key(t, SYNONYMS_DIM)
            if k and k in DIMENSIONS and k not in dims:
                dims.append(k)
    if dims:
        spec.dimensions = dims

    # fechas
    r = re.search(r"del\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s+al\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})", p_raw, flags=re.I)
    if r:
        sd = dateparser.parse(r.group(1), languages=["es"])
        ed = dateparser.parse(r.group(2), languages=["es"])
        if sd and ed:
            spec.start_date = sd.date().isoformat()
            spec.end_date = ed.date().isoformat()
    else:
        a, b = _relative_range(p_raw)
        if not (a and b):
            for kw in RELATIVE_KEYWORDS:
                if kw in p_raw.lower():
                    a, b = parse_relative(kw)
                    break
        if a and b:
            spec.start_date, spec.end_date = a, b

    # filtros: categoria / cliente / producto contiene
    mcat = re.search(r"categor[ií]a\s+([a-z0-9 áéíóúñ\-_/.]+)", p_raw, flags=re.I)
    if mcat:
        spec.filters.append(Filter("categoria", "contains", mcat.group(1).strip()))
    mcli = re.search(r"cliente\s+([a-z0-9 áéíóúñ\-_/.]+)", p_raw, flags=re.I)
    if mcli:
        spec.filters.append(Filter("cliente", "contains", mcli.group(1).strip()))
    mcont = re.search(r"(?:contenga|que contenga|nombre contiene)\s+([a-z0-9 áéíóúñ\-_/.]+)", p_raw, flags=re.I)
    if mcont:
        spec.filters.append(Filter("producto", "contains", mcont.group(1).strip()))

    # top/bottom/los N productos
    mtop = re.search(r"\btop\s+(\d{1,3})\b", p)
    if mtop:
        spec.limit = int(mtop.group(1))
    if spec.limit is None:
        mcount = re.search(r"\b(?:los\s+)?(\d{1,3})\s+productos?\b", p)
        if mcount:
            spec.limit = int(mcount.group(1))
    mbot = re.search(r"\b(bottom|menos)\s+(\d{1,3})\b", p)
    if mbot:
        spec.limit = int(mbot.group(2))
        spec.order_dir = "asc"

    # orden
    mord = re.search(r"orden(?:ar)?\s+por\s+([a-z0-9 _/\-]+)(?:\s+(asc|desc))?", p)
    if mord:
        target = mord.group(1).strip()
        k = _best_key(target, {**SYNONYMS_MET, **SYNONYMS_DIM})
        if k:
            spec.order_by = k
            if mord.group(2) in ("asc", "desc"):
                spec.order_dir = mord.group(2)

    # ------------------ Fallbacks seguros ------------------
    # si piden “clientes” en el texto y no se detectó dimensión, forzar 'cliente'
    if not spec.dimensions and re.search(r"\bclientes?\b", p_raw, flags=re.I):
        spec.dimensions = ["cliente"]

    # si no hay métricas, usar una típica para ventas (monto_total)
    if not spec.metrics:
        # asume que tu DSL tiene 'monto_total' o 'total'
        spec.metrics = ["monto_total"] if "monto_total" in METRICS else [next(iter(METRICS))]

    spec.ensure_defaults()
    return spec, warnings
