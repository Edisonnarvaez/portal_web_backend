import os
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from normativity.models import Criterio
from processes.models import Documento
from soportes.models import SoporteDocumental

User = get_user_model()


class Cumplimiento(models.Model):
    """Registro de cumplimiento de un criterio especifico."""

    RESULTADO_CHOICES = [
        ('CUMPLE', 'Cumple'),
        ('NO_CUMPLE', 'No Cumple'),
        ('PARCIALMENTE', 'Parcialmente'),
        ('NO_APLICA', 'No Aplica'),
    ]

    autoevaluacion = models.ForeignKey(
        'Autoevaluacion',
        on_delete=models.PROTECT,
        related_name='cumplimientos',
        verbose_name='Autoevaluacion',
    )
    servicio_sede = models.ForeignKey(
        'ServicioSede',
        on_delete=models.PROTECT,
        related_name='cumplimientos',
        verbose_name='Servicio de Sede',
    )
    criterio = models.ForeignKey(Criterio, on_delete=models.PROTECT, related_name='cumplimientos', verbose_name='Criterio')
    cumple = models.CharField(max_length=20, choices=RESULTADO_CHOICES, verbose_name='Resultado de Cumplimiento')
    documentos = models.ManyToManyField(
        Documento,
        blank=True,
        related_name='cumplimientos_documentos',
        verbose_name='Documentos de Calidad',
    )
    soportes = models.ManyToManyField(
        SoporteDocumental,
        blank=True,
        related_name='cumplimientos_soportes',
        verbose_name='Soportes de Evidencia',
    )
    hallazgo = models.TextField(blank=True, null=True, verbose_name='Hallazgo/Observacion')
    plan_mejora = models.TextField(blank=True, null=True, verbose_name='Plan de Mejora')
    responsable_mejora = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cumplimientos_responsable',
        verbose_name='Responsable de Mejora',
    )
    fecha_compromiso = models.DateField(blank=True, null=True, verbose_name='Fecha Comprometida para Mejora')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_cumplimiento'
        verbose_name = 'Cumplimiento'
        verbose_name_plural = 'Cumplimientos'
        unique_together = ('autoevaluacion', 'servicio_sede', 'criterio')
        indexes = [
            models.Index(fields=['autoevaluacion', 'cumple']),
            models.Index(fields=['criterio']),
        ]

    def __str__(self):
        return f'{self.autoevaluacion} - {self.criterio.codigo}: {self.cumple}'

    def tiene_plan_mejora(self):
        return self.plan_mejora and not self.fecha_compromiso

    def mejora_vencida(self):
        if not self.fecha_compromiso:
            return False
        return self.fecha_compromiso < timezone.now().date()

    @property
    def documentos_evidencia(self):
        """Alias de compatibilidad para clientes que aun consumen documentos_evidencia."""
        return self.documentos


ALLOWED_CHECKLIST_EXTENSIONS = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.xls', '.xlsx']


def checklist_upload_path(instance, filename):
    """Ruta de soportes del checklist: media/habilitacion/checklists/<id>/<uuid>_archivo."""
    unique_name = f'{uuid.uuid4().hex[:12]}_{filename}'
    checklist_id = instance.checklist_item.checklist_id if instance.checklist_item_id else 'sin_checklist'
    return os.path.join('habilitacion', 'checklists', str(checklist_id), unique_name)


def validate_checklist_extension(value):
    """Valida extensiones permitidas para soportes documentales de checklist."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_CHECKLIST_EXTENSIONS:
        raise ValidationError(
            f'Extension "{ext}" no permitida. '
            f'Extensiones validas: {", ".join(ALLOWED_CHECKLIST_EXTENSIONS)}'
        )
