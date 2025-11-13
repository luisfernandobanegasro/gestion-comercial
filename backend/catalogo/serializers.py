# catalogo/serializers.py
from rest_framework import serializers

from .models import (
    Categoria,
    Marca,
    Producto,
    MovimientoInventario,
    Oferta,
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = [
            "id",
            "nombre",
            "descripcion",
            "activa",
            "creado_en",
            "actualizado_en",
        ]


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = [
            "id",
            "nombre",
            "activa",
            "creado_en",
            "actualizado_en",
        ]


class OfertaSerializer(serializers.ModelSerializer):
    # Relacionamos por ID
    categorias = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Categoria.objects.all(),
        required=False,
    )
    marcas = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Marca.objects.all(),
        required=False,
    )
    productos_especificos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Producto.objects.all(),
        required=False,
    )

    # Versiones “solo nombre” para mostrar en la tabla
    categorias_nombres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="nombre",
        source="categorias",
    )
    marcas_nombres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="nombre",
        source="marcas",
    )
    productos_nombres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="nombre",
        source="productos_especificos",
    )

    class Meta:
        model = Oferta
        fields = [
            "id",
            "nombre",
            "porcentaje_descuento",
            "fecha_inicio",
            "fecha_fin",
            "activa",
            "categorias",
            "marcas",
            "productos_especificos",
            "categorias_nombres",
            "marcas_nombres",
            "productos_nombres",
        ]


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source="categoria.nombre", read_only=True
    )
    marca_nombre = serializers.CharField(
        source="marca.nombre", read_only=True
    )

    # Objeto de la mejor oferta activa (propiedad @property oferta_activa)
    oferta_activa = OfertaSerializer(read_only=True)

    precio_final = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id",
            "codigo",
            "nombre",
            "modelo",
            "caracteristicas",
            "marca",
            "marca_nombre",
            "categoria",
            "categoria_nombre",
            "precio",
            "precio_final",
            "oferta_activa",
            "stock",
            "activo",
            "creado_en",
            "actualizado_en",
            "imagen",
            "imagen_url",
        ]
        extra_kwargs = {
            "imagen": {"write_only": True, "required": False},
        }

    def get_imagen_url(self, obj):
        request = self.context.get("request")
        if obj.imagen and request is not None:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source="producto.nombre", read_only=True
    )
    usuario_username = serializers.CharField(
        source="usuario.username", read_only=True
    )

    class Meta:
        model = MovimientoInventario
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "tipo",
            "cantidad",
            "motivo",
            "usuario",
            "usuario_username",
            "creado_en",
        ]
        read_only_fields = [
            "usuario",
            "creado_en",
            "usuario_username",
            "producto_nombre",
        ]
