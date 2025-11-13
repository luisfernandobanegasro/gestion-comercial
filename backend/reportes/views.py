# reportes/views.py
import re
from rest_framework import views, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse

from cuentas.permissions import RequierePermisos
from catalogo.models import Producto
from .runner import run_prompt
from .services import generar_excel, generar_pdf, get_dashboard_data
from .query_builder import build_queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, RequierePermisos])
def dashboard_data_view(request):
    data = get_dashboard_data()
    return Response(data)


class ReportePromptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["reportes.generar"]  # por defecto: ver

    def get_permissions(self):
        # Exportar requiere permiso distinto
        self.required_perms = ["reportes.generar"]
        try:
            if self.request.method == "POST":
                prompt = (self.request.data.get("prompt") or "").lower()
                if "pdf" in prompt or "excel" in prompt or "xlsx" in prompt:
                    self.required_perms = ["reportes.exportar"]
        except Exception:
            pass
        return [p() for p in self.permission_classes]

    def post(self, request):
        prompt = request.data.get("prompt") or ""

        # --- INTENCIÓN: agregar al carrito (detección inmediata, robusta) ---
        if re.search(r"\b(carrito|compra|pedido)\b", prompt.lower()):
            m = re.search(
                r"(?:agrega|añade|pon|mete|quiero)\s+(?:(\d+)\s+)?(.+?)\s+(?:al|a la)\s+(?:carrito|compra|pedido)",
                prompt.lower()
            )
            if m:
                cantidad = int(m.group(1) or 1)
                nombre = m.group(2).strip()
                prod = Producto.objects.filter(nombre__icontains=nombre, activo=True).first()
                if not prod:
                    return Response({"error": f"Producto '{nombre}' no encontrado."}, status=404)
                return Response({
                    "intent": "agregar_carrito",
                    "producto": {"id": prod.id, "nombre": prod.nombre, "precio": float(prod.precio)},
                    "cantidad": cantidad
                })

        # --- Interpretar y ejecutar reporte con el motor robusto ---
        try:
            result = run_prompt(prompt)  # puede devolver (spec, headers, rows, warnings) o solo spec
        except Exception as e:
            return Response(
                {"error": "No pude generar el reporte", "detail": str(e)},
                status=400
            )

        # Normalizar salida de runner
        if isinstance(result, dict):
            spec, headers, rows, warnings = result, [], [], []
        else:
            spec, headers, rows, warnings = result

        # Si el runner no resolvió las filas/encabezados, construimos con query_builder
        if not headers and not rows:
            try:
                headers, rows = build_queryset(spec or {})
            except Exception as e:
                return Response(
                    {"error": "No pude construir el reporte con el query_builder", "detail": str(e)},
                    status=400
                )

        formato = (spec or {}).get("format", "pantalla")

        # Sugerencias UX si faltó info (fechas/agrupación)
        hints = []
        if not (spec or {}).get("start_date") or not (spec or {}).get("end_date"):
            hints.append(
                "No detecté rango de fechas. Usé últimos 30 días. Puedes decir: "
                "'del 01/09/2025 al 30/09/2025' o 'este mes'."
            )
        if not (spec or {}).get("dimensions"):
            hints.append(
                "No detecté agrupación. Prueba: 'por producto', 'por cliente', 'por mes' o varias: 'por cliente y mes'."
            )

        # --- Salidas ---
        if formato == "excel":
            xls = generar_excel(headers, rows)
            resp = HttpResponse(
                xls,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            resp["Content-Disposition"] = 'attachment; filename="reporte.xlsx"'
            return resp

        if formato == "pdf":
            meta = {
                "start_date": (spec or {}).get("start_date"),
                "end_date": (spec or {}).get("end_date"),
                "group_by": (spec or {}).get("dimensions"),
                "metrics": (spec or {}).get("metrics"),
                "intent": (spec or {}).get("intent"),
            }
            pdf = generar_pdf(headers, rows, meta)
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = 'attachment; filename="reporte.pdf"'
            return resp

        # Preview en pantalla
        return Response({
            "headers": headers,
            "rows": rows,
            "meta": spec,
            "warnings": warnings,
            "hints": hints
        })
