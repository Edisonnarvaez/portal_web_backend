from django.contrib.auth import get_user_model
from django.db import models
import os

from .checklistItem import checklist_upload_path, validate_checklist_extension

User = get_user_model()


class EvidenciaChecklist(models.Model):
    """Evidencia documental cargada para cada item del checklist."""

    TIPO_CHOICES = [
        ('DOCUMENTO', 'Documento'),
        ('CERTIFICADO', 'Certificado'),
        ('ACTA', 'Acta'),
        ('OTRO', 'Otro'),
    ]

    checklist_item = models.ForeignKey(
        'ChecklistItem',
        on_delete=models.CASCADE,
        related_name='evidencias',
        verbose_name='Item de Checklist',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='DOCUMENTO', verbose_name='Tipo')
    nombre = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nombre')
    archivo = models.FileField(
        upload_to=checklist_upload_path,
        validators=[validate_checklist_extension],
        verbose_name='Archivo',
    )
    hash_integridad = models.CharField(max_length=128, blank=True, null=True, verbose_name='Hash de Integridad')
    subido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidencias_checklist_subidas',
        verbose_name='Subido por',
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')

    class Meta:
        db_table = 'habilitacion_evidenciachecklist'
        verbose_name = 'Evidencia de Checklist'
        verbose_name_plural = 'Evidencias de Checklist'
        ordering = ['-fecha_subida']

    def __str__(self):
        return self.nombre or os.path.basename(self.archivo.name)

    def save(self, *args, **kwargs):
        if self.archivo and not self.nombre:
            self.nombre = os.path.basename(self.archivo.name)
        super().save(*args, **kwargs)
