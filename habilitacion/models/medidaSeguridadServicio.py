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


class MedidaSeguridadServicio(models.Model):
    """Medidas de seguridad aplicadas al servicio habilitado."""

    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('LEVANTADA', 'Levantada'),
        ('EN_SEGUIMIENTO', 'En Seguimiento'),
    ]

    servicio_sede = models.ForeignKey(ServicioSede,on_delete=models.CASCADE,related_name='medidas_seguridad',verbose_name='Servicio de Sede')
    norma_referencia = models.CharField(max_length=120,default='Ley 9 de 1979 - Artículo 576',verbose_name='Norma de Referencia')
    descripcion = models.TextField(verbose_name='Descripción de la Medida')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVA', verbose_name='Estado')
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')
    autoridad = models.CharField(max_length=200, blank=True, null=True, verbose_name='Autoridad')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_medidaseguridad'
        verbose_name = 'Medida de Seguridad'
        verbose_name_plural = 'Medidas de Seguridad'
        indexes = [
            models.Index(fields=['servicio_sede', 'estado']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.servicio_sede.codigo_servicio} - {self.estado}"
