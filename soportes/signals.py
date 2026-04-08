from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    TipoDocumentoSoporte,
    SoporteRequerido,
    SoporteDocumental,
)


# ======================================================
# 🔥 CREACIÓN AUTOMÁTICA DE CHECKLIST
# ======================================================

def crear_soportes_requeridos(instance, nivel):
    """
    Crea automáticamente los soportes requeridos según el nivel
    """

    tipos = TipoDocumentoSoporte.objects.filter(
        nivel_aplica=nivel,
        activo=True
    )

    for tipo in tipos:
        filtros = {
            'tipo_documento': tipo
        }

        if nivel == 'EMPRESA':
            filtros['empresa'] = instance

        elif nivel == 'SEDE':
            filtros['sede'] = instance

        elif nivel == 'SERVICIO':
            filtros['servicio'] = instance

        SoporteRequerido.objects.get_or_create(**filtros)


# ======================================================
# 🏢 EMPRESA
# ======================================================
@receiver(post_save, sender='companies.Company')
def crear_checklist_empresa(sender, instance, created, **kwargs):
    if created:
        crear_soportes_requeridos(instance, 'EMPRESA')


# ======================================================
# 🏥 SEDE
# ======================================================
@receiver(post_save, sender='companies.Headquarters')
def crear_checklist_sede(sender, instance, created, **kwargs):
    if created:
        crear_soportes_requeridos(instance, 'SEDE')


# ======================================================
# 🧪 SERVICIO
# ======================================================
@receiver(post_save, sender='habilitacion.ServicioSede')
def crear_checklist_servicio(sender, instance, created, **kwargs):
    if created:
        crear_soportes_requeridos(instance, 'SERVICIO')


# ======================================================
# 📄 CUANDO SE SUBE UN SOPORTE → ACTUALIZA ESTADO
# ======================================================
@receiver(post_save, sender=SoporteDocumental)
def actualizar_estado_soporte(sender, instance, **kwargs):

    filtros = {
        'tipo_documento': instance.tipo_documento
    }

    if instance.nivel == 'EMPRESA':
        filtros['empresa'] = instance.empresa

    elif instance.nivel == 'SEDE':
        filtros['sede'] = instance.sede

    elif instance.nivel == 'SERVICIO':
        filtros['servicio'] = instance.servicio

    try:
        soporte_req = SoporteRequerido.objects.get(**filtros)

        # 🔥 VALIDAR VENCIMIENTO
        if instance.fecha_vencimiento:
            if instance.fecha_vencimiento < timezone.now().date():
                soporte_req.estado = 'VENCIDO'
            else:
                soporte_req.estado = 'CARGADO'
        else:
            soporte_req.estado = 'CARGADO'

        soporte_req.save()

    except SoporteRequerido.DoesNotExist:
        pass