from rest_framework import serializers
from .models import Cliente
from cuentas.models import Usuario

class _UsuarioClienteSerializer(serializers.ModelSerializer):
    """Serializer reducido para mostrar info del usuario dentro del cliente."""
    class Meta:
        model = Usuario
        fields = ["id", "username", "email"]

class ClienteSerializer(serializers.ModelSerializer):
    # Para lectura, mostramos el objeto de usuario completo (reducido)
    usuario_obj = _UsuarioClienteSerializer(source="usuario", read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "id", "nombre", "email", "telefono", "direccion", "activo",
            "creado_en", "actualizado_en",
            "usuario", # Para escritura (recibe el ID del usuario)
            "usuario_obj" # Para lectura (devuelve el objeto)
        ]
        # Hacemos que 'usuario' sea de solo escritura y no obligatorio al actualizar
        extra_kwargs = {
            "usuario": {"write_only": True, "required": False, "allow_null": True}
        }
