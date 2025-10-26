from rest_framework import serializers
from .models import Categoria, Marca, Producto, MovimientoInventario, Oferta

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "activa", "creado_en", "actualizado_en"]

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "activa", "creado_en", "actualizado_en"]

class OfertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oferta
        fields = ["id", "nombre", "porcentaje_descuento", "fecha_inicio", "fecha_fin"]

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    marca_nombre = serializers.CharField(source="marca.nombre", read_only=True)
    oferta_activa = OfertaSerializer(read_only=True) # Muestra el objeto de la oferta
    precio_final = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id","codigo","nombre","marca","marca_nombre","categoria","categoria_nombre",
            "precio","precio_final","oferta_activa","stock","activo","creado_en","actualizado_en","imagen", "imagen_url"
        ]   
        extra_kwargs = {'imagen': {'write_only': True, 'required': False}}
    def get_imagen_url(self, obj):
        r = self.context.get('request')
        if obj.imagen and r:
            return r.build_absolute_uri(obj.imagen.url)
        return None


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = ["id","producto","producto_nombre","tipo","cantidad","motivo","usuario","usuario_username","creado_en"]
        read_only_fields = ["usuario","creado_en","usuario_username","producto_nombre"]
