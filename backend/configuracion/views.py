from rest_framework import generics, permissions
from .models import Configuracion
from .serializers import ConfiguracionSerializer
from cuentas.permissions import RequierePermisos

class ConfiguracionView(generics.RetrieveUpdateAPIView):
    """
    Vista para obtener (GET) y actualizar (PUT/PATCH) la configuración del sistema.
    No permite creación ni borrado, ya que es un singleton.
    """
    queryset = Configuracion.objects.all()
    serializer_class = ConfiguracionSerializer
    permission_classes = [permissions.IsAuthenticated, RequierePermisos]
    required_perms = ["configuracion.gestionar"]

    def get_object(self):
        """
        Devuelve siempre la única instancia de configuración (pk=1).
        """
        obj = Configuracion.load()
        self.check_object_permissions(self.request, obj)
        return obj