# reportes/views.py
import re

from django.http import HttpResponse
from django.db.models import Q
from rest_framework import views, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from cuentas.permissions import RequierePermisos
from catalogo.models import Producto
from clientes.models import Cliente

from .runner import run_prompt
from .services import (
    generar_excel,
    generar_pdf,
    get_dashboard_data,
)
from .query_builder import build_queryset  # por si lo usas en el futuro


# ============================
# Utils: fechas desde el prompt
# ============================

_DATE_RE = re.compile(
    r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})"
)


def _norm_fecha(s: str) -> str:
    """
    Normaliza 'DD/MM/YYYY' -> 'YYYY-MM-DD'.
    Si ya viene en 'YYYY-MM-DD', se devuelve igual.
    """
    s = s.strip()
    if "/" in s:
        d, m, y = s.split("/")
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return s


def _ensure_dates_in_spec_from_prompt(spec: dict, prompt: str) -> dict:
    """
    Si el spec NO tiene start_date / end_date, intenta extraerlas del texto.
    Soporta:
      - 'del DD/MM/YYYY al DD/MM/YYYY'
      - cualquier par de fechas en el texto.
    """
    if spec.get("start_date") and spec.get("end_date"):
        return spec  # ya está bien

    p = (prompt or "").lower()

    # 1) Patrón explícito 'del ... al ...'
    m = re.search(
        r"del\s+(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})\s+al\s+"
        r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})",
        p,
    )
    if m:
        spec["start_date"] = _norm_fecha(m.group(1))
        spec["end_date"] = _norm_fecha(m.group(2))
        return spec

    # 2) Cualquier par de fechas en el texto
    fechas = _DATE_RE.findall(p)
    if len(fechas) >= 2:
        spec["start_date"] = _norm_fecha(fechas[0])
        spec["end_date"] = _norm_fecha(fechas[1])
    elif len(fechas) == 1:
        spec["start_date"] = _norm_fecha(fechas[0])

    return spec


# ============================
# Utils: resolver cliente desde el prompt
# ============================

def _resolver_cliente_desde_prompt(prompt: str) -> Cliente | None:
    """
    Intenta encontrar un Cliente a partir del texto del prompt.
    Adaptado a tu modelo actual (nombre, documento, ...).

    Estrategia:
      1) Buscar documento: 'cliente CI 1234567', 'cliente NIT 1234567',
         'cliente documento 1234567'.
      2) Buscar patrón 'cliente Juan Perez ...' y matchear por nombre.
    """
    if not prompt:
        return None

    low = prompt.lower()

    # 1) Documento explícito
    m_ci = re.search(r"(?:ci|c\.i\.|nit|documento)\s+(\d+)", low)
    if m_ci:
        doc = m_ci.group(1)
        cli = Cliente.objects.filter(documento__icontains=doc).first()
        if cli:
            return cli

    # 2) "cliente Juan Perez ..."
    m = re.search(
        r"cliente\s+(.+?)(?:\s+del\s+|\s+desde\s+|\s+entre\s+|\s+agrupad|\s+en\s+pantalla|$)",
        prompt,
        flags=re.IGNORECASE,
    )
    if not m:
        return None

    nombre_raw = m.group(1).strip()
    partes = [p for p in nombre_raw.split() if len(p) > 2]
    if not partes:
        return None

    qs = Cliente.objects.all()
    cond = Q()
    for p in partes:
        # tu modelo solo tiene "nombre"
        cond |= Q(nombre__icontains=p)

    qs = qs.filter(cond).order_by("id")
    return qs.first()


def _to_bool(val) -> bool:
    """
    Convierte cualquier valor de request.data a booleano "real".
    Acepta: True/False, 'true'/'false', '1'/'0', etc.
    """
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return str(val).strip().lower() in ("1", "true", "yes", "y", "on")


# ============================
# Dashboard estático
# ============================

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, RequierePermisos])
def dashboard_data_view(request):
    """
    Datos agregados para el dashboard de reportes.
    """
    data = get_dashboard_data()
    return Response(data)


# ============================
# Vista principal de reportes
# ============================

class ReportePromptView(views.APIView):
    """
    Endpoint principal del generador de reportes.

    Flujo:
      1) Detecta si el prompt es para "agregar al carrito" → responde directo.
      2) Pasa el prompt a run_prompt(prompt, user) → obtiene spec, headers, rows, warnings.
      3) Según 'format' (pantalla / pdf / excel) decide si exporta o previsualiza.
    """

    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["reportes.generar"]  # por defecto: generar/visualizar

    def get_permissions(self):
        """
        Si el usuario está pidiendo exportar (PDF / Excel) y NO es solo preview,
        exigimos permiso 'reportes.exportar' en lugar de 'reportes.generar'.
        """
        self.required_perms = ["reportes.generar"]
        try:
            if self.request.method == "POST":
                data = self.request.data
                prompt = (data.get("prompt") or "").lower()
                formato = (data.get("format") or "").lower().strip()
                force_preview = _to_bool(data.get("force_preview"))

                wants_export = (
                    formato in ("pdf", "excel")
                    or any(k in prompt for k in ("pdf", "excel", "xlsx"))
                )

                if wants_export and not force_preview:
                    self.required_perms = ["reportes.exportar"]
        except Exception:
            # en cualquier error, por seguridad dejamos el permiso más restrictivo
            self.required_perms = ["reportes.exportar"]

        return [p() for p in self.permission_classes]

    # ------------------------------------
    # POST /api/reportes/prompt/
    # ------------------------------------
    def post(self, request):
        prompt = request.data.get("prompt") or ""
        formato_cliente = (request.data.get("format") or "").lower().strip() or "auto"
        force_preview = _to_bool(request.data.get("force_preview"))

        # ------------------------------------------------------------------
        # 1) INTENCIÓN ESPECIAL: agregar al carrito (detección inmediata)
        # ------------------------------------------------------------------
        low = prompt.lower()
        if re.search(r"\b(carrito|compra|pedido)\b", low):
            m = re.search(
                r"(?:agrega|añade|pon|mete|quiero)\s+(?:(\d+)\s+)?(.+?)\s+"
                r"(?:al|a la)\s+(?:carrito|compra|pedido)",
                low,
            )
            if m:
                cantidad = int(m.group(1) or 1)
                nombre = m.group(2).strip()
                prod = (
                    Producto.objects.filter(
                        nombre__icontains=nombre, activo=True
                    ).first()
                )
                if not prod:
                    return Response(
                        {"error": f"Producto '{nombre}' no encontrado."},
                        status=404,
                    )
                return Response(
                    {
                        "intent": "agregar_carrito",
                        "producto": {
                            "id": prod.id,
                            "nombre": prod.nombre,
                            "precio": float(prod.precio),
                        },
                        "cantidad": cantidad,
                    }
                )

        # ------------------------------------------------------------------
        # 2) Interpretar y ejecutar reporte con el motor de IA / reglas
        # ------------------------------------------------------------------
        try:
            # run_prompt devuelve: (spec_dict, headers, rows, warnings)
            spec, headers, rows, warnings = run_prompt(
                prompt, user=request.user, parse_only=False
            )
        except Exception as e:
            return Response(
                {"error": "No pude generar el reporte.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        spec = spec or {}

        # Aseguramos fechas a partir del texto si el spec no las trajo
        spec = _ensure_dates_in_spec_from_prompt(spec, prompt)

        # ------------------------------------------------------------------
        # 3) Ajuste extra para reportes de ventas con cliente específico
        # ------------------------------------------------------------------
        intent = (spec.get("intent") or "").lower()

        if "venta" in intent or "cliente" in intent:
            if not spec.get("cliente"):
                cli_obj = _resolver_cliente_desde_prompt(prompt)
                if cli_obj:
                    # usamos documento si existe, si no el nombre
                    spec["cliente"] = cli_obj.documento or cli_obj.nombre

        # ------------------------------------------------------------------
        # 4) Resolver formato final (pantalla / pdf / excel)
        # ------------------------------------------------------------------
        formato_spec = (spec.get("format") or "").lower().strip()

        if formato_cliente in ("pantalla", "pdf", "excel"):
            formato_final = formato_cliente
        else:
            formato_final = formato_spec or "pantalla"

        if force_preview:
            formato_final = "pantalla"

        spec["format"] = formato_final

        # ------------------------------------------------------------------
        # 5) Sugerencias UX (hints)
        # ------------------------------------------------------------------
        hints = []
        if not spec.get("start_date") and not spec.get("end_date"):
            hints.append(
                "No detecté rango de fechas. Usé últimos 30 días (según el servicio). "
                "Puedes decir: 'del 01/09/2025 al 30/09/2025' o 'este mes'."
            )
        if not spec.get("group_by"):
            hints.append(
                "No detecté agrupación. Prueba: 'por producto', 'por cliente', "
                "'por categoría' o combinaciones en prompts futuros."
            )

        # ------------------------------------------------------------------
        # 6) Salidas: Excel / PDF / Pantalla
        # ------------------------------------------------------------------
        if formato_final == "excel":
            if not headers and not rows and build_queryset is not None:
                try:
                    headers, rows = build_queryset(spec)
                except Exception:
                    pass

            if not headers and not rows:
                return Response(
                    {"error": "El reporte no devolvió datos para generar Excel."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            xls = generar_excel(headers, rows)
            resp = HttpResponse(
                xls,
                content_type=(
                    "application/"
                    "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )
            resp["Content-Disposition"] = 'attachment; filename="reporte.xlsx"'
            return resp

        if formato_final == "pdf":
            if not headers and not rows and build_queryset is not None:
                try:
                    headers, rows = build_queryset(spec)
                except Exception:
                    pass

            if not headers and not rows:
                return Response(
                    {"error": "El reporte no devolvió datos para generar PDF."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            meta = {
                "start_date": spec.get("start_date"),
                "end_date": spec.get("end_date"),
                "group_by": spec.get("group_by"),
                "metrics": spec.get("metrics"),
                "intent": spec.get("intent"),
            }
            pdf = generar_pdf(headers, rows, meta)
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = 'attachment; filename=\"reporte.pdf\"'
            return resp

        # Preview en pantalla
        return Response(
            {
                "headers": headers,
                "rows": rows,
                "meta": spec,
                "warnings": warnings,
                "hints": hints,
            }
        )
