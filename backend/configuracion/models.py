from django.db import models

class Configuracion(models.Model):
    """
    Modelo Singleton para guardar la configuración global del sistema.
    Solo debe existir una instancia de este modelo.
    """
    nombre_banco = models.CharField(max_length=100, blank=True, help_text="Nombre del banco para transferencias o pagos QR.")
    numero_cuenta = models.CharField(max_length=50, blank=True, help_text="Número de cuenta bancaria.")
    nombre_titular = models.CharField(max_length=150, blank=True, help_text="Nombre del titular de la cuenta.")
    documento_titular = models.CharField(max_length=20, blank=True, help_text="CI o NIT del titular de la cuenta.")
    glosa_qr = models.CharField(max_length=100, blank=True, default="Pago de productos", help_text="Concepto o glosa que aparecerá en el QR.")

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"

    def save(self, *args, **kwargs):
        """Asegura que solo exista una instancia."""
        self.pk = 1
        super(Configuracion, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Carga la única instancia de configuración, creándola si no existe.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuración General del Sistema"