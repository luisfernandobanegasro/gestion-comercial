import django_filters as df
from .models import RegistroAuditoria

class RegistroAuditoriaFilter(df.FilterSet):
    # Rangos de fecha y datetime
    desde = df.IsoDateTimeFilter(field_name="creado_en", lookup_expr="gte")
    hasta = df.IsoDateTimeFilter(field_name="creado_en", lookup_expr="lte")

    # Filtros exactos
    usuario = df.CharFilter(field_name="usuario__username", lookup_expr="iexact")
    modulo = df.CharFilter(field_name="modulo", lookup_expr="iexact")
    metodo = df.CharFilter(field_name="metodo", lookup_expr="iexact")
    estado = df.NumberFilter(field_name="estado", lookup_expr="exact")

    # Búsqueda parcial por ruta/acción
    q = df.CharFilter(method="filter_q")

    class Meta:
        model = RegistroAuditoria
        fields = ["usuario", "modulo", "metodo", "estado"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            df.filters.Q(ruta__icontains=value) |
            df.filters.Q(accion__icontains=value) |
            df.filters.Q(user_agent__icontains=value)
        )
