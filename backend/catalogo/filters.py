# catalogo/filters.py
import django_filters as df
from django.utils import timezone
from .models import Producto, Oferta

class ProductoFilter(df.FilterSet):
    precio_min = df.NumberFilter(field_name="precio", lookup_expr="gte")
    precio_max = df.NumberFilter(field_name="precio", lookup_expr="lte")
    categoria = df.NumberFilter(field_name="categoria_id", lookup_expr="exact")
    marca = df.NumberFilter(field_name="marca_id", lookup_expr="exact")
    activo = df.BooleanFilter(field_name="activo")
    q = df.CharFilter(method="filter_q")

    class Meta:
        model = Producto
        fields = ["categoria", "marca", "activo"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            df.filters.Q(nombre__icontains=value) |
            df.filters.Q(codigo__icontains=value)
        )


class OfertaFilter(df.FilterSet):
    activa = df.BooleanFilter(field_name="activa")
    vigente = df.BooleanFilter(method="filter_vigente")

    class Meta:
        model = Oferta
        fields = ["activa"]

    def filter_vigente(self, queryset, name, value):
        if not value:
            return queryset
        now = timezone.now()
        return queryset.filter(
            activa=True,
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        )
