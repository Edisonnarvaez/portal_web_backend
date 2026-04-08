from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    TipoDocumentoSoporte,
    SoporteRequerido,
    SoporteDocumental,
)


# ======================================================
# 🔥 CREACIÓN AUTOMÁTICA DE CHECKLIST (OPTIMIZADO)
# ======================================================
def crear_soportes_requeridos(instance, nivel):

    tipos = TipoDocumentoSoporte.objects.filter(
        nivel_aplica=nivel,
        activo=True
    )

    soportes = []

    for tipo in tipos:
        data = {'tipo_documento': tipo}

        if nivel == 'EMPRESA':
            data['empresa'] = instance

        elif nivel == 'SEDE':
            data['sede'] = instance

        elif nivel == 'SERVICIO':
            data['servicio'] = instance

        soportes.append(SoporteRequerido(**data))

    SoporteRequerido.objects.bulk_create(soportes, ignore_conflicts=True)


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
# 📄 ACTUALIZACIÓN DE ESTADO (ROBUSTO)
# ======================================================
@receiver(post_save, sender=SoporteDocumental)
def actualizar_estado_soporte(sender, instance, **kwargs):

    filtros = {'tipo_documento': instance.tipo_documento}

    if instance.nivel == 'EMPRESA':
        filtros['empresa'] = instance.empresa

    elif instance.nivel == 'SEDE':
        filtros['sede'] = instance.sede

    elif instance.nivel == 'SERVICIO':
        filtros['servicio'] = instance.servicio

    soporte_req = SoporteRequerido.objects.filter(**filtros).first()

    if not soporte_req:
        return

    # 🔥 BUSCAR DOCUMENTO VIGENTE REAL
    vigente = SoporteDocumental.objects.filter(
        tipo_documento=instance.tipo_documento,
        es_vigente=True,
        **{k: v for k, v in filtros.items() if k != 'tipo_documento'}
    ).first()

    if not vigente:
        soporte_req.estado = 'PENDIENTE'

    else:
        if vigente.fecha_vencimiento:
            if vigente.fecha_vencimiento < timezone.now().date():
                soporte_req.estado = 'VENCIDO'
            else:
                soporte_req.estado = 'CARGADO'
        else:
            soporte_req.estado = 'CARGADO'

    soporte_req.save()