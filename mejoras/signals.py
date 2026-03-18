"""
mejoras/signals.py

Signals para auto-gestión de estados en planes de mejora.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import PlanMejora


@receiver(pre_save, sender=PlanMejora)
def auto_marcar_vencido(sender, instance, **kwargs):
    """
    Automáticamente marca un plan como VENCIDO si la fecha de vencimiento pasó
    y el estado no es COMPLETADO.
    """
    if instance.estado not in ['COMPLETADO', 'VENCIDO']:
        if instance.fecha_vencimiento and instance.fecha_vencimiento < timezone.now().date():
            instance.estado = 'VENCIDO'


@receiver(pre_save, sender=PlanMejora)
def auto_completar_fecha_implementacion(sender, instance, **kwargs):
    """
    Si el estado cambia a COMPLETADO y no tiene fecha_implementacion,
    la establece automáticamente.
    """
    if instance.estado == 'COMPLETADO' and not instance.fecha_implementacion:
        instance.fecha_implementacion = timezone.now().date()
