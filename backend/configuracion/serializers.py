from rest_framework import serializers
from .models import Configuracion

class ConfiguracionSerializer(serializers.ModelSerializer):
    """
    Serializer para leer y actualizar el modelo singleton de Configuración.
    """
    class Meta:
        model = Configuracion
        fields = [
            'nombre_banco',
            'numero_cuenta',
            'nombre_titular',
            'documento_titular',
            'glosa_qr',
        ]