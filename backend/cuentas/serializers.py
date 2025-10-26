from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario, Rol, Permiso


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ["id", "codigo", "descripcion"]


class RolSerializer(serializers.ModelSerializer):
    # Para lectura, mostramos los objetos de permisos completos
    permisos_obj = PermisoSerializer(source="permisos", many=True, read_only=True)

    class Meta:
        model = Rol
        fields = ["id", "nombre", "descripcion", "permisos", "permisos_obj"]
        # 'permisos' será una lista de IDs para escritura (crear/actualizar)
        extra_kwargs = {
            "permisos": {"write_only": True, "required": False}
        }


class UsuarioSerializer(serializers.ModelSerializer):
    # Para lectura, mostramos los objetos de roles completos
    roles_obj = RolSerializer(source="roles", many=True, read_only=True)
    # Añadimos la lista de permisos del usuario para que el frontend la consuma
    nombres_roles = serializers.StringRelatedField(source="roles", many=True, read_only=True)
    permisos = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        # Campos que se exponen en la API
        fields = [
            "id", "username", "email", "first_name", "last_name", "is_active", "is_superuser",
            "password", "roles", "roles_obj", "nombres_roles", "permisos"
        ]
        # 'roles' será una lista de IDs para escritura
        # 'password' solo se debe poder escribir, nunca leer
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "roles": {"write_only": True, "required": False},
        }

    def get_permisos(self, obj):
        """Devuelve un set con todos los permisos del usuario."""
        return obj.get_all_permissions()

    def create(self, validated_data):
        # Hashear la contraseña antes de crear el usuario
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Hashear la contraseña si se está actualizando
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)