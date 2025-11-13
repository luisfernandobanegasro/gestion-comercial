# reportes/dsl.py
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any
import dateparser

OrderDir = Literal["asc","desc"]

@dataclass
class Filter:
    field: str  # e.g., "categoria"
    op: Literal["eq","contains","lt","lte","gt","gte","isnull","notnull","neq"]
    value: Any = None

@dataclass
class Spec:
    # núcleo de la consulta
    intent: Literal["ventas","stock","precios","sin_movimiento","top","custom"] = "ventas"
    metrics: List[str] = field(default_factory=lambda:["monto_total"])
    dimensions: List[str] = field(default_factory=lambda:["producto"])
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    filters: List[Filter] = field(default_factory=list)
    order_by: Optional[str] = None  # clave de métrica o dimensión
    order_dir: OrderDir = "desc"
    limit: Optional[int] = None
    format: Literal["pantalla","pdf","excel"] = "pantalla"

    def ensure_defaults(self):
        if not self.metrics: self.metrics = ["monto_total"]
        if not self.dimensions: self.dimensions = ["producto"]
        if not self.start_date and not self.end_date:
            # por defecto últimos 30 días
            self.start_date = dateparser.parse("30 days ago").date().isoformat()
            self.end_date = dateparser.parse("today").date().isoformat()

# === utilidades ===
RELATIVE_KEYWORDS = [
    "hoy", "ayer", "esta semana", "últimos 7 días", "últimos 30 días",
    "este mes", "mes pasado", "este año", "últimos 12 meses"
]

def parse_relative(text:str):
    dt = dateparser.parse(text, languages=["es"])
    return dt.date().isoformat() if dt else None
