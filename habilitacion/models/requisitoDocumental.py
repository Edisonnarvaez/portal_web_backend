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

User = get_user_model()

class RequisitoDocumental(models.Model):
    """Catálogo de requisitos del Anexo 2 para inscripción, novedades y visitas."""

    TIPO_TRAMITE_CHOICES = [
        ('INSCRIPCION', 'Inscripción'),
        ('NOVEDAD', 'Novedad'),
        ('VISITA_PREVIA', 'Visita Previa'),
        ('VISITA_CERTIFICACION', 'Visita de Certificación'),
        ('VISITA_REACTIVACION', 'Visita de Reactivación'),
    ]

    codigo = models.CharField(max_length=30, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    tipo_tramite = models.CharField(max_length=30, choices=TIPO_TRAMITE_CHOICES, verbose_name='Tipo de Trámite')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_requisitodocumental'
        verbose_name = 'Requisito Documental'
        verbose_name_plural = 'Requisitos Documentales'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['tipo_tramite', 'activo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

