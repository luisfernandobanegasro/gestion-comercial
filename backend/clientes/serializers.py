from rest_framework import serializers
from .models import Cliente
from cuentas.models import Usuario

class _UsuarioClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "username", "email"]

class ClienteSerializer(serializers.ModelSerializer):
    usuario_obj = _UsuarioClienteSerializer(source="usuario", read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "id",
            "nombre",
            "email",
            "telefono",
            "documento",      # <-- AGREGADO (CI/NIT)
            # "direccion",     # <-- omitido a propósito del payload
            "activo",
            "creado_en",
            "actualizado_en",
            "usuario",        # write_only
            "usuario_obj",    # read_only
        ]
        extra_kwargs = {
            "usuario": {"write_only": True, "required": False, "allow_null": True},
            # los demás campos quedan opcionales según tu modelo (email/telefono/documento tienen blank=True)
        }
