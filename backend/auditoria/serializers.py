from rest_framework import serializers
from .models import RegistroAuditoria

class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.SerializerMethodField()

    class Meta:
        model = RegistroAuditoria
        fields = [
            "id", "creado_en", "fecha", "hora",
            "usuario", "usuario_username",
            "modulo", "accion", "ip", "user_agent",
            "ruta", "metodo", "estado", "payload",
        ]

    def get_usuario_username(self, obj):
        return getattr(obj.usuario, "username", None)
