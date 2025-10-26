import django_filters as df
from .models import Producto

class ProductoFilter(df.FilterSet):
    precio_min = df.NumberFilter(field_name="precio", lookup_expr="gte")
    precio_max = df.NumberFilter(field_name="precio", lookup_expr="lte")
    categoria = df.NumberFilter(field_name="categoria_id", lookup_expr="exact")
    activo = df.BooleanFilter(field_name="activo")
    q = df.CharFilter(method="filter_q")

    class Meta:
        model = Producto
        fields = ["categoria", "activo"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            df.filters.Q(nombre__icontains=value) |
            df.filters.Q(codigo__icontains=value)
        )
