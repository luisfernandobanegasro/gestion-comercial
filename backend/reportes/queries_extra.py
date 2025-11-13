# reportes/queries_extra.py
from django.db.models import Sum, Q
from catalogo.models import Producto
from ventas.models import ItemVenta

def productos_sin_movimiento(start_date=None, end_date=None, categoria=None):
    vendidos = ItemVenta.objects.all()
    if start_date: vendidos = vendidos.filter(venta__creado_en__date__gte=start_date)
    if end_date: vendidos = vendidos.filter(venta__creado_en__date__lte=end_date)
    vendidos = vendidos.values_list("producto_id", flat=True).distinct()

    q = Producto.objects.filter(activo=True).exclude(id__in=vendidos)
    if categoria:
        q = q.filter(categoria__nombre__icontains=categoria)

    headers = ["Producto", "Cantidad total", "Monto total"]
    rows = [[p.nombre, 0, 0] for p in q]
    return headers, rows
