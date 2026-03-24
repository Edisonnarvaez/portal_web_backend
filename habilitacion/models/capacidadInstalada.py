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
from habilitacion.models import Autoevaluacion
from habilitacion.models import ServicioSede   

User = get_user_model()

class CapacidadInstalada(models.Model):
    """Capacidad instalada reportada por servicio (REPS)."""

    TIPO_CHOICES = [
        ('AMBULANCIA', 'Ambulancias'),
        ('CAMA', 'Camas'),
        ('APOYO_TERAPEUTICO', 'Apoyo Terapéutico'),
        ('SALA', 'Salas'),
        ('OTRO', 'Otro'),
    ]

    servicio_sede = models.ForeignKey(ServicioSede,on_delete=models.CASCADE,related_name='capacidades_instaladas',verbose_name='Servicio de Sede')
    tipo_capacidad = models.CharField(max_length=30,choices=TIPO_CHOICES,verbose_name='Tipo de Capacidad')
    subtipo = models.CharField(max_length=120,blank=True,null=True,verbose_name='Subtipo')
    cantidad = models.PositiveIntegerField(default=0,verbose_name='Cantidad')
    unidad = models.CharField(max_length=40,blank=True,null=True,verbose_name='Unidad')
    observaciones = models.TextField(blank=True,null=True,verbose_name='Observaciones')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_capacidadinstalada'
        verbose_name = 'Capacidad Instalada'
        verbose_name_plural = 'Capacidades Instaladas'
        indexes = [
            models.Index(fields=['servicio_sede', 'tipo_capacidad']),
            models.Index(fields=['tipo_capacidad']),
        ]

    def __str__(self):
        return f"{self.servicio_sede.codigo_servicio} - {self.get_tipo_capacidad_display()} ({self.cantidad})"

