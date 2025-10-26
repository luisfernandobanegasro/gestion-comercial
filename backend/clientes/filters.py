import django_filters as df
from .models import Cliente

class ClienteFilter(df.FilterSet):
    activo = df.BooleanFilter(field_name="activo")
    q = df.CharFilter(method="filter_q")

    class Meta:
        model = Cliente
        fields = ["activo"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            df.filters.Q(nombre__icontains=value) |
            df.filters.Q(email__icontains=value) |
            df.filters.Q(telefono__icontains=value)
        )
