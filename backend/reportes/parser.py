# reportes/parser.py
import re
from typing import Dict, Any

def parse_prompt(prompt: str) -> Dict[str, Any]:
    """
    Extrae:
      - start_date, end_date (YYYY-MM-DD)
      - group_by: 'producto' | 'cliente' | 'mes' | 'categoria'
      - format: 'pantalla' | 'pdf' | 'excel'
    Acepta fechas dd/mm/yyyy o yyyy-mm-dd en el prompt.
    """
    p = (prompt or "").lower()
    out: Dict[str, Any] = {
        "start_date": None,
        "end_date": None,
        "group_by": "producto",
        "format": "pantalla",
    }

    # fechas dd/mm/yyyy o yyyy-mm-dd
    fechas = re.findall(r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})", p)

    def norm(s: str) -> str:
        if "/" in s:
            d, m, y = s.split("/")
            return f"{y}-{m}-{d}"
        return s

    if len(fechas) >= 1:
        out["start_date"] = norm(fechas[0])
    if len(fechas) >= 2:
        out["end_date"] = norm(fechas[1])

    if "producto" in p:
        out["group_by"] = "producto"
    elif "cliente" in p:
        out["group_by"] = "cliente"
    elif "categor" in p:
        out["group_by"] = "categoria"
    elif "mes" in p or "mensual" in p:
        out["group_by"] = "mes"

    if "pdf" in p:
        out["format"] = "pdf"
    elif "excel" in p or "xlsx" in p:
        out["format"] = "excel"
    else:
        out["format"] = "pantalla"

    return out
