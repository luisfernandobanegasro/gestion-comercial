from rest_framework import views, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from .services import parsear_prompt, consultar_ventas, generar_excel, generar_pdf, get_dashboard_data
from cuentas.permissions import RequierePermisos

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, RequierePermisos])
def dashboard_data_view(request):
    """Devuelve todos los datos necesarios para el dashboard principal."""
    data = get_dashboard_data()
    return Response(data)

class ReportePromptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["reportes.generar"]

    def post(self, request):
        prompt = request.data.get("prompt") or ""
        data = parsear_prompt(prompt)

        formato = data["format"]
        if formato in ("pdf", "excel"):
            self.required_perms = ["reportes.exportar"]
            for p in self.permission_classes:
                if hasattr(p, "has_permission"):
                    if not p().has_permission(request, self):
                        return Response({"detail": "No tienes permisos para exportar."}, status=403)

        headers, rows = consultar_ventas(data["start_date"], data["end_date"], data["group_by"])

        if formato == "excel":
            xls = generar_excel(headers, rows)
            resp = HttpResponse(xls, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            resp["Content-Disposition"] = 'attachment; filename="reporte.xlsx"'
            return resp

        if formato == "pdf":
            meta = {
                "start_date": data["start_date"],
                "end_date": data["end_date"],
                "group_by": data["group_by"],
            }
            pdf = generar_pdf(headers, rows, meta)
            resp = HttpResponse(pdf, content_type="application/pdf")
            resp["Content-Disposition"] = 'attachment; filename="reporte.pdf"'
            return resp

        return Response({
            "headers": headers,
            "rows": rows,
            "meta": {
                "start_date": str(data["start_date"]) if data["start_date"] else None,
                "end_date": str(data["end_date"]) if data["end_date"] else None,
                "group_by": data["group_by"],
                "format": data["format"],
                "prompt": prompt,
            }
        })
