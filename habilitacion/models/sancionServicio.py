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

from habilitacion.models import ServicioSede

User = get_user_model()

class SancionServicio(models.Model):
    """Sanciones aplicadas al servicio habilitado."""

    TIPO_CHOICES = [
        ('PECUNIARIA', 'Pecuniaria'),
        ('TEMPORAL', 'Suspensión Temporal'),
        ('DEFINITIVA', 'Cierre Definitivo'),
        ('OTRA', 'Otra'),
    ]

    ESTADO_CHOICES = [
        ('VIGENTE', 'Vigente'),
        ('CUMPLIDA', 'Cumplida'),
        ('REVOCADA', 'Revocada'),
    ]

    servicio_sede = models.ForeignKey(ServicioSede,on_delete=models.CASCADE,related_name='sanciones',verbose_name='Servicio de Sede')
    norma_referencia = models.CharField(max_length=120,default='Ley 9 de 1979 - Artículo 577',verbose_name='Norma de Referencia')
    tipo_sancion = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Sanción')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='VIGENTE', verbose_name='Estado')
    acto_administrativo = models.CharField(max_length=120, blank=True, null=True, verbose_name='Acto Administrativo')
    autoridad = models.CharField(max_length=200, blank=True, null=True, verbose_name='Autoridad')
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_sancionservicio'
        verbose_name = 'Sanción de Servicio'
        verbose_name_plural = 'Sanciones de Servicio'
        indexes = [
            models.Index(fields=['servicio_sede', 'estado']),
            models.Index(fields=['tipo_sancion']),
        ]

    def __str__(self):
        return f"{self.servicio_sede.codigo_servicio} - {self.get_tipo_sancion_display()}"

