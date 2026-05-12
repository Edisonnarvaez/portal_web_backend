from django.contrib.auth import get_user_model
from django.db import transaction
from django.db import models

from .requisitoDocumental import RequisitoDocumental
from .checklistItem import ChecklistItem

User = get_user_model()


class ChecklistVerificacion(models.Model):
    """Checklist de verificacion documental para un tramite REPS."""

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETO', 'Completo'),
        ('CERRADO', 'Cerrado'),
    ]

    codigo_checklist = models.CharField(max_length=60, unique=True, verbose_name='Codigo Checklist')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR', verbose_name='Estado')
    novedad = models.ForeignKey(
        'NovedadREPS',
        on_delete=models.PROTECT,
        related_name='checklists',
        verbose_name='Novedad REPS',
    )
    servicio_sede = models.ForeignKey(
        'ServicioSede',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklists_verificacion',
        verbose_name='Servicio de Sede',
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklists_verificacion',
        verbose_name='Responsable',
    )
    fecha_cierre = models.DateField(blank=True, null=True, verbose_name='Fecha de Cierre')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_checklistverificacion'
        verbose_name = 'Checklist de Verificacion'
        verbose_name_plural = 'Checklists de Verificacion'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['novedad', 'estado']),
        ]

    def __str__(self):
        return f'{self.codigo_checklist} - {self.estado}'

    SUBTIPO_NOVEDAD_PREFIX_RULES = {
        'CAMBIO_CONTACTO': ['NOV-BAS', 'NOV-CON'],
        'CIERRE_MODALIDAD': ['NOV-BAS', 'NOV-CM'],
        'CAMBIO_HORARIO': ['NOV-BAS', 'NOV-HOR'],
        'CAMBIO_COMPLEJIDAD': ['NOV-BAS', 'NOV-CC'],
        'TRASLADO_SERVICIO': ['NOV-BAS', 'NOV-TS'],
        'OTRA': ['NOV-BAS'],
    }

    def get_tipos_tramite_objetivo(self):
        if self.novedad.tipo_novedad == 'PRESTADOR':
            return ['INSCRIPCION']

        tipos = ['NOVEDAD']

        if self.novedad.subtipo_novedad == 'REACTIVACION':
            tipos.append('VISITA_REACTIVACION')
        elif self.novedad.subtipo_novedad == 'APERTURA_MODALIDAD':
            tipos.append('VISITA_CERTIFICACION')

        if self.novedad.requiere_visita_previa:
            tipos.append('VISITA_PREVIA')

        return list(dict.fromkeys(tipos))

    def _aplicar_reglas_subtipo_novedad(self, requisitos):
        prefijos = self.SUBTIPO_NOVEDAD_PREFIX_RULES.get(self.novedad.subtipo_novedad)
        if not prefijos:
            return requisitos

        q_prefijos = models.Q()
        for prefijo in prefijos:
            q_prefijos |= models.Q(codigo__startswith=prefijo)

        return requisitos.filter(
            models.Q(tipo_tramite__in=['VISITA_PREVIA', 'VISITA_CERTIFICACION', 'VISITA_REACTIVACION'])
            | (models.Q(tipo_tramite='NOVEDAD') & q_prefijos)
            | models.Q(tipo_tramite='INSCRIPCION')
        )

    def get_requisitos_aplicables(self):
        tipos_tramite = self.get_tipos_tramite_objetivo()
        requisitos = RequisitoDocumental.objects.filter(
            tipo_tramite__in=tipos_tramite,
            activo=True,
        )

        requisitos = self._aplicar_reglas_subtipo_novedad(requisitos)
        return requisitos.order_by('codigo')

    def crear_items_desde_requisitos(self):
        requisitos = self.get_requisitos_aplicables()
        if not requisitos.exists():
            return 0

        existentes = set(self.items.values_list('requisito_id', flat=True))

        nuevos_items = [
            ChecklistItem(
                checklist=self,
                requisito=requisito,
                obligatorio=requisito.obligatorio,
            )
            for requisito in requisitos
            if requisito.id not in existentes
        ]

        if not nuevos_items:
            return 0

        with transaction.atomic():
            ChecklistItem.objects.bulk_create(nuevos_items, ignore_conflicts=True)

        return len(nuevos_items)

    def save(self, *args, **kwargs):
        es_nuevo = self._state.adding
        super().save(*args, **kwargs)
        if es_nuevo:
            self.crear_items_desde_requisitos()
