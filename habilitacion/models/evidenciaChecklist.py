"""
habilitacion/models.py

Modelos transaccionales para la habilitación de servicios de salud.
Integración con los modelos core (Company, Headquarters).
DatosPrestador vinculado a Headquarters (OneToOne) para permitir habilitación
de una única sede o múltiples sedes de la misma empresa.
"""

from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import os
import uuid

from companies.models import Company, Headquarters
from normativity.models import Criterio
from processes.models import Documento
from habilitacion.models import DatosPrestador
from habilitacion.models import ServicioSede
from habilitacion.models import NovedadREPS
from habilitacion.models import RequisitoDocumental
from habilitacion.models import ChecklistVerificacion
from habilitacion.models import ChecklistItem   


User = get_user_model()

class EvidenciaChecklist(models.Model):
    """Evidencia documental cargada para cada ítem del checklist."""

    TIPO_CHOICES = [
        ('DOCUMENTO', 'Documento'),
        ('CERTIFICADO', 'Certificado'),
        ('ACTA', 'Acta'),
        ('OTRO', 'Otro'),
    ]

    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE,
        related_name='evidencias',
        verbose_name='Ítem de Checklist'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='DOCUMENTO', verbose_name='Tipo')
    nombre = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nombre')
    archivo = models.FileField(
        upload_to=checklist_upload_path,
        validators=[validate_checklist_extension],
        verbose_name='Archivo'
    )
    hash_integridad = models.CharField(max_length=128, blank=True, null=True, verbose_name='Hash de Integridad')
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidencias_checklist_subidas',
        verbose_name='Subido por'
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
