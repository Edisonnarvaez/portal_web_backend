from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Funcionario, FelicitacionCumpleanios


@receiver(post_save, sender=Funcionario)
def crear_felicitacion_cumpleanos(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta después de guardar un Funcionario.
    Si el funcionario es nuevo (created=True), crea automáticamente
    una felicitación de cumpleaños con un mensaje genérico.
    """
    if created:
        # Verificar que no exista ya una felicitación para este funcionario
        if not FelicitacionCumpleanios.objects.filter(funcionario=instance).exists():
            FelicitacionCumpleanios.objects.create(
                funcionario=instance,
                mensaje="Feliz Cumpleaños"
            )
