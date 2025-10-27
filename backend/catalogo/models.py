from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


# ==========================
# Helpers para código único
# ==========================
def _prefijo_categoria(nombre_categoria: str | None) -> str:
    """
    Genera un prefijo de 3 letras en MAYÚSCULAS a partir del nombre de la categoría.
    Si no hay nombre, usa 'GEN'.
    """
    base = slugify(nombre_categoria or "GEN").replace("-", "")
    base = (base[:3] or "gen").upper()
    return base


def _siguiente_codigo_unico(prefijo: str) -> str:
    """
    Devuelve un código único con el formato PREFIJO-###.
    Busca el siguiente correlativo disponible, evitando colisiones.
    """
    from catalogo.models import Producto  # import local para evitar ciclos
    sec = Producto.objects.filter(codigo__startswith=f"{prefijo}-").count() + 1
    # En caso de huecos por eliminaciones, garantizamos unicidad con un loop
    while True:
        codigo = f"{prefijo}-{sec:03d}"
        if not Producto.objects.filter(codigo=codigo).exists():
            return codigo
        sec += 1


# ==========================
# Modelos
# ==========================
class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class OfertaManager(models.Manager):
    def activas(self):
        """Devuelve solo las ofertas que están actualmente vigentes."""
        now = timezone.now()
        return self.get_queryset().filter(
            activa=True,
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        )

class Oferta(models.Model):
    """Modelo para gestionar descuentos y promociones."""
    nombre = models.CharField(max_length=150)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ej: 20.00 para un 20% de descuento")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    activa = models.BooleanField(default=True)

    # Campos para aplicar la oferta de forma flexible
    marcas = models.ManyToManyField('catalogo.Marca', blank=True, related_name='ofertas')
    categorias = models.ManyToManyField('catalogo.Categoria', blank=True, related_name='ofertas')
    productos_especificos = models.ManyToManyField('catalogo.Producto', blank=True, related_name='ofertas_especificas')

    objects = OfertaManager()

    class Meta:
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje_descuento}%)"


class Producto(models.Model):
    """
    - 'codigo' puede dejarse vacío al crear: se autogenera como PREF-###.
    - Si se proporciona un 'codigo' manual, se respeta (debe ser único).
    - En ediciones posteriores NO se regenera automáticamente; puedes editarlo.
    """
    codigo = models.CharField(
        max_length=50,
        unique=True,
        null=True,    # permite múltiples NULL en Postgres sin romper unique
        blank=True,
        default=None, # evita default ""
        help_text="Código interno del producto (único). Si lo dejas vacío al crear, se autogenera."
    )
    nombre = models.CharField(max_length=120)
    modelo = models.CharField(max_length=100, blank=True, help_text="Ej: G502 Hero, Viper Mini, etc.")
    caracteristicas = models.TextField(blank=True, help_text="Características adicionales del producto, una por línea.")
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos"
    )
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    
    class Meta:
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["nombre"]),
        ]

    def __str__(self) -> str:
        return f"{self.codigo or 'SIN-CODIGO'} - {self.nombre}"

    @property
    def oferta_activa(self):
        """
        Busca la mejor oferta activa para este producto.
        La prioridad es: oferta específica > oferta de marca > oferta de categoría.
        Devuelve el objeto Oferta o None.
        """
        from django.db.models import Q

        # Construir el filtro para buscar ofertas aplicables a este producto
        filtro_aplicable = Q(productos_especificos=self)
        if self.marca_id:
            filtro_aplicable |= Q(marcas=self.marca)
        if self.categoria_id:
            filtro_aplicable |= Q(categorias=self.categoria)

        # Buscar la mejor oferta (mayor descuento) que aplique
        mejor_oferta = Oferta.objects.activas().filter(filtro_aplicable).order_by('-porcentaje_descuento').first()
        return mejor_oferta

    @property
    def precio_final(self):
        """Calcula el precio final aplicando el mejor descuento activo."""
        oferta = self.oferta_activa
        if not oferta:
            return self.precio
        
        descuento = self.precio * (oferta.porcentaje_descuento / 100)
        return self.precio - descuento

    def save(self, *args, **kwargs):
        """
        Autogenera 'codigo' SOLO al CREAR y cuando viene vacío/None.
        Si ya existe (update) o se proporciona manualmente, se respeta.
        """
        creating = self._state.adding
        super().save(*args, **kwargs)  # guardamos primero para tener PK

        if creating and not self.codigo:
            pref = _prefijo_categoria(getattr(self.categoria, "nombre", None))
            self.codigo = _siguiente_codigo_unico(pref)
            super().save(update_fields=["codigo"])  # segunda pasada: solo 'codigo'


TIPO_MOV = (("IN", "Entrada"), ("OUT", "Salida"))


class MovimientoInventario(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="movimientos"
    )
    tipo = models.CharField(max_length=3, choices=TIPO_MOV)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=120, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self) -> str:
        return f"{self.creado_en:%Y-%m-%d %H:%M} {self.tipo} {self.cantidad} {self.producto_id}"
