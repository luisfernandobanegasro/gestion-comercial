from rest_framework import serializers
from .models import RegistroAuditoria

class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.SerializerMethodField()
    # Formateamos la fecha para que sea más legible en el frontend
    fecha_hora = serializers.DateTimeField(source="creado_en", format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = RegistroAuditoria
        fields = [
            "id", "fecha_hora",
            "usuario", "usuario_username",
            "modulo", "accion", "ip", "user_agent",
            "ruta", "metodo", "estado", "payload",
        ]

    def get_usuario_username(self, obj):
        return getattr(obj.usuario, "username", "Anónimo")
