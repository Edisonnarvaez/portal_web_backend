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
from habilitacion.models import DatosPrestador
from habilitacion.models import ServicioSede
from normativity.models import Criterio
from processes.models import Documento

User = get_user_model()

class NovedadREPS(models.Model):
    """Novedad reportada al REPS para prestador, sede, servicio o capacidad instalada."""

    TIPO_CHOICES = [
        ('PRESTADOR', 'Novedad del Prestador'),
        ('SEDE', 'Novedad de la Sede'),
        ('SERVICIO', 'Novedad de Servicios'),
        ('CAPACIDAD', 'Novedad de Capacidad Instalada'),
    ]

    SUBTIPO_CHOICES = [
        ('CAMBIO_CONTACTO', 'Cambio de datos de contacto'),
        ('REACTIVACION', 'Reactivación del servicio'),
        ('APERTURA_MODALIDAD', 'Apertura de modalidad'),
        ('CIERRE_MODALIDAD', 'Cierre de modalidad'),
        ('CAMBIO_HORARIO', 'Cambio de horario de prestación'),
        ('CAMBIO_COMPLEJIDAD', 'Cambio de complejidad'),
        ('TRASLADO_SERVICIO', 'Traslado de servicio'),
        ('OTRA', 'Otra'),
    ]

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('RADICADA', 'Radicada'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('APLICADA', 'Aplicada en REPS'),
    ]

    codigo_novedad = models.CharField(max_length=60, unique=True, verbose_name='Código de Novedad')
    tipo_novedad = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Novedad')
    subtipo_novedad = models.CharField(max_length=30, choices=SUBTIPO_CHOICES, verbose_name='Subtipo de Novedad')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR', verbose_name='Estado')

    datos_prestador = models.ForeignKey(DatosPrestador,on_delete=models.CASCADE,related_name='novedades_reps',verbose_name='Prestador')
    sede = models.ForeignKey(Headquarters,on_delete=models.SET_NULL,null=True,blank=True,related_name='novedades_reps',verbose_name='Sede')
    servicio_sede = models.ForeignKey(ServicioSede,on_delete=models.SET_NULL,null=True,blank=True,related_name='novedades_reps',verbose_name='Servicio')
    requiere_visita_previa = models.BooleanField(default=False, verbose_name='Requiere Visita Previa')
    fecha_radicacion = models.DateField(blank=True, null=True, verbose_name='Fecha de Radicación')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    creado_por = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='novedades_reps_creadas',verbose_name='Creado por')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_novedadreps'
        verbose_name = 'Novedad REPS'
        verbose_name_plural = 'Novedades REPS'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['tipo_novedad', 'estado']),
            models.Index(fields=['datos_prestador', 'estado']),
        ]

    def __str__(self):
        return f"{self.codigo_novedad} - {self.get_tipo_novedad_display()}"
