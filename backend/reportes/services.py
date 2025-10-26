from datetime import datetime
from io import BytesIO
from typing import Tuple, Dict, Any, List
from decimal import Decimal

from django.db.models import Sum, F, Avg
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDay

from ventas.models import Venta, ItemVenta
from clientes.models import Cliente

def parsear_prompt(prompt: str) -> Dict[str, Any]:
    p = (prompt or "").lower()
    out = {"start_date": None, "end_date": None, "group_by": "producto", "format": "pantalla"}

    import re
    fechas = re.findall(r"(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})", p)

    def norm(s):
        if "/" in s:
            d, m, y = s.split("/")
            return f"{y}-{m}-{d}"
        return s

    if len(fechas) >= 1:
        out["start_date"] = norm(fechas[0])
    if len(fechas) >= 2:
        out["end_date"] = norm(fechas[1])

    if "cliente" in p:
        out["group_by"] = "cliente"
    elif "categor" in p:
        out["group_by"] = "categoria"
    elif "mes" in p or "mensual" in p:
        out["group_by"] = "mes"
    else:
        out["group_by"] = "producto"

    if "pdf" in p:
        out["format"] = "pdf"
    elif "excel" in p or "xlsx" in p:
        out["format"] = "excel"
    else:
        out["format"] = "pantalla"

    return out

def consultar_ventas(start_date: str | None, end_date: str | None, group_by: str) -> Tuple[List[str], List[List]]:
    qs = ItemVenta.objects.select_related("venta", "producto", "venta__cliente", "producto__categoria")
    if start_date:
        qs = qs.filter(venta__creado_en__date__gte=start_date)
    if end_date:
        qs = qs.filter(venta__creado_en__date__lte=end_date)
    qs = qs.filter(venta__estado__in=["pagada"])  # ajusta si quieres incluir 'pendiente'

    rows: List[List] = []
    headers: List[str] = []

    if group_by == "producto":
        agg = qs.values(n=F("producto__nombre")).annotate(cantidad=Sum("cantidad"), monto=Sum(F("subtotal")))
        headers = ["Producto","Cantidad total","Monto total"]
        rows = [[r["n"], r["cantidad"] or 0, float(r["monto"] or 0)] for r in agg]

    elif group_by == "cliente":
        agg = qs.values(n=F("venta__cliente__nombre")).annotate(cantidad=Sum("cantidad"), monto=Sum(F("subtotal")))
        headers = ["Cliente","Cantidad total","Monto total"]
        rows = [[r["n"], r["cantidad"] or 0, float(r["monto"] or 0)] for r in agg]

    elif group_by == "categoria":
        agg = qs.values(n=F("producto__categoria__nombre")).annotate(cantidad=Sum("cantidad"), monto=Sum(F("subtotal")))
        headers = ["Categoría","Cantidad total","Monto total"]
        rows = [[r["n"], r["cantidad"] or 0, float(r["monto"] or 0)] for r in agg]

    elif group_by == "mes":
        agg = qs.values(n=F("venta__creado_en__date__month")).annotate(cantidad=Sum("cantidad"), monto=Sum(F("subtotal")))
        headers = ["Mes","Cantidad total","Monto total"]
        rows = [[r["n"], r["cantidad"] or 0, float(r["monto"] or 0)] for r in agg]

    return headers, rows

def generar_excel(headers: List[str], rows: List[List]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"
    ws.append(headers)
    for r in rows:
        ws.append(r)
    out = BytesIO()
    wb.save(out)
    return out.getvalue()

def generar_pdf(headers: List[str], rows: List[List], meta: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    y = h - 2*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, "Reporte de Ventas")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, f"Rango: {meta.get('start_date') or '-'} a {meta.get('end_date') or '-'} | Grupo: {meta.get('group_by')}")
    y -= 1*cm

    c.setFont("Helvetica-Bold", 10)
    x = [2*cm, 9*cm, 14*cm]  # 3 columnas
    for i, htxt in enumerate(headers):
        c.drawString(x[i], y, htxt)
    y -= 0.4*cm
    c.line(2*cm, y, 19*cm, y)
    y -= 0.4*cm

    c.setFont("Helvetica", 10)
    for r in rows:
        for i, val in enumerate(r):
            c.drawString(x[i], y, str(val))
        y -= 0.5*cm
        if y < 3*cm:
            c.showPage()
            y = h - 2*cm

    c.showPage()
    c.save()
    return buffer.getvalue()

def get_dashboard_data():
    """
    Recopila y estructura todos los datos necesarios para el dashboard principal.
    """
    now = timezone.now()
    today = now.date()
    start_of_month = today.replace(day=1)
    start_of_30_days = today - timedelta(days=30)

    # 1. KPIs principales
    ventas_pagadas = Venta.objects.filter(estado='pagada')

    ventas_hoy = ventas_pagadas.filter(creado_en__date=today).aggregate(total=Sum('total'))['total'] or 0
    ventas_mes = ventas_pagadas.filter(creado_en__gte=start_of_month).aggregate(total=Sum('total'))['total'] or 0
    ticket_promedio = ventas_pagadas.filter(creado_en__gte=start_of_month).aggregate(avg=Avg('total'))['avg'] or 0
    nuevos_clientes_mes = Cliente.objects.filter(creado_en__gte=start_of_month).count()

    # 2. Gráfico de ventas de los últimos 30 días
    ventas_diarias = (
        ventas_pagadas.filter(creado_en__gte=start_of_30_days)
        .annotate(dia=TruncDay('creado_en'))
        .values('dia')
        .annotate(total=Sum('total'))
        .order_by('dia')
    )

    # 3. Gráfico de ventas por categoría
    ventas_por_categoria = (
        ventas_pagadas.filter(creado_en__gte=start_of_month)
        .values('items__producto__categoria__nombre')
        .annotate(total=Sum('items__subtotal'))
        .order_by('-total')
    )

    # 4. Tabla de últimas 5 ventas
    ultimas_ventas = ventas_pagadas.order_by('-creado_en')[:5].select_related('cliente')

    return {
        "kpis": {
            "ventas_hoy": f"{ventas_hoy:,.2f}",
            "ventas_mes_actual": f"{ventas_mes:,.2f}",
            "nuevos_clientes_mes": nuevos_clientes_mes,
            "ticket_promedio": f"{ticket_promedio:,.2f}",
        },
        "ventas_ultimos_30_dias": [{"fecha": item['dia'].strftime('%Y-%m-%d'), "total": float(item['total'])} for item in ventas_diarias],
        "ventas_por_categoria": [{"categoria": item['items__producto__categoria__nombre'], "total": float(item['total'])} for item in ventas_por_categoria if item['items__producto__categoria__nombre']],
        "ultimas_ventas": [{"id": v.id, "folio": v.folio, "cliente": v.cliente.nombre if v.cliente else 'N/A', "total": f"{v.total:,.2f}", "fecha": v.creado_en.strftime('%Y-%m-%d %H:%M')} for v in ultimas_ventas]
    }
