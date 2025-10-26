from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from clientes.models import Cliente

def _crear_o_actualizar_perfil_cliente(usuario):
    """Función helper para crear el perfil de cliente si tiene el rol."""
    if usuario.roles.filter(nombre="Cliente").exists():
        # get_or_create previene duplicados y es seguro de ejecutar múltiples veces.
        Cliente.objects.get_or_create(
            usuario=usuario,
            defaults={
                'nombre': usuario.get_full_name() or usuario.username,
                'email': usuario.email,
            }
        )

@receiver(m2m_changed, sender=get_user_model().roles.through)
def manejar_cambio_de_roles(sender, instance, action, **kwargs):
    """Se dispara cuando los roles de un usuario cambian."""
    if action == "post_add":
        # 'instance' aquí es el objeto Usuario
        _crear_o_actualizar_perfil_cliente(instance)