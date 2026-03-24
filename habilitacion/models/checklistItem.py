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

User = get_user_model()


class ChecklistItem(models.Model):
    """Ítem del checklist asociado a un requisito documental del Anexo 2."""

    checklist = models.ForeignKey(
        ChecklistVerificacion,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Checklist'
    )
    requisito = models.ForeignKey(
        RequisitoDocumental,
        on_delete=models.PROTECT,
        related_name='items_checklist',
        verbose_name='Requisito'
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
        verbose_name='Verificado por'
    )
    fecha_verificacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Verificación')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_checklistitem'
        verbose_name = 'Ítem de Checklist'
        verbose_name_plural = 'Ítems de Checklist'
        unique_together = ('checklist', 'requisito')
        indexes = [
            models.Index(fields=['checklist', 'cumple']),
        ]

    def __str__(self):
        return f"{self.checklist.codigo_checklist} - {self.requisito.codigo}"
