import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def checklist_upload_path(instance, filename):
    """Ruta de soportes del checklist."""

    unique_name = f'{uuid.uuid4().hex[:12]}_{filename}'
    checklist_id = instance.checklist_item.checklist_id if instance.checklist_item_id else 'sin_checklist'
    return os.path.join('habilitacion', 'checklists', str(checklist_id), unique_name)


def validate_checklist_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    allowed_extensions = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.xls', '.xlsx']
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Extension "{ext}" no permitida. '
            f'Extensiones validas: {", ".join(allowed_extensions)}'
        )


class ChecklistItem(models.Model):
    """Item del checklist asociado a un requisito documental del Anexo 2."""

    checklist = models.ForeignKey(
        'ChecklistVerificacion',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Checklist',
    )
    requisito = models.ForeignKey(
        'RequisitoDocumental',
        on_delete=models.PROTECT,
        related_name='items_checklist',
        verbose_name='Requisito',
    )
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')
    cumple = models.BooleanField(null=True, blank=True, verbose_name='Cumple')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    verificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_checklist_verificados',
        verbose_name='Verificado por',
    )
    fecha_verificacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Verificacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_checklistitem'
        verbose_name = 'Item de Checklist'
        verbose_name_plural = 'Items de Checklist'
        unique_together = ('checklist', 'requisito')
        indexes = [
            models.Index(fields=['checklist', 'cumple']),
        ]

    def __str__(self):
        return f'{self.checklist.codigo_checklist} - {self.requisito.codigo}'
