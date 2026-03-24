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

from habilitacion.models import DatosSede

User = get_user_model()

class ServicioSede(models.Model):
    """
    Servicios de salud habilitados en una sede específica.
    Un servicio es la combinación de modalidad + tipo en una sede determinada.
    """
    
    MODALIDAD_CHOICES = [
        ('INTRAMURAL', 'Intramural'),
        ('AMBULATORIA', 'Ambulatoria'),
        ('TELEMEDICINA', 'Telemedicina'),
        ('URGENCIAS', 'Urgencias'),
        ('AMBULANCIA', 'Ambulancia'),
    ]
    
    COMPLEJIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]
    
    ESTADO_HABILITACION_CHOICES = [
        ('HABILITADO', 'Habilitado'),
        ('EN_PROCESO', 'En Proceso'),
        ('SUSPENDIDO', 'Suspendido'),
        ('NO_HABILITADO', 'No Habilitado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    prestador = models.ForeignKey(DatosSede,on_delete=models.PROTECT,related_name='servicios_salud',verbose_name="Prestador",)
    # Identificación del servicio
    codigo_servicio = models.CharField(max_length=20,verbose_name="Código del Servicio",help_text="Código asignado por REPS para este servicio")
    nombre_servicio = models.CharField(max_length=255,verbose_name="Nombre del Servicio")
    descripcion = models.TextField(blank=True,null=True,verbose_name="Descripción del Servicio")
    # Clasificación
    modalidad = models.CharField(max_length=20,choices=MODALIDAD_CHOICES,verbose_name="Modalidad")
    complejidad = models.CharField(max_length=10,choices=COMPLEJIDAD_CHOICES,verbose_name="Complejidad")
    # Estado
    estado_habilitacion = models.CharField(max_length=20,choices=ESTADO_HABILITACION_CHOICES,default='EN_PROCESO',verbose_name="Estado de Habilitación")
    fecha_habilitacion = models.DateField(blank=True,null=True,verbose_name="Fecha de Habilitación")
    fecha_vencimiento = models.DateField(blank=True,null=True,verbose_name="Fecha de Vencimiento")
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True,verbose_name="Fecha de Actualización")
    
    class Meta:
        db_table = "habilitacion_serviciosede"
        verbose_name = "Servicio de Prestador"
        verbose_name_plural = "Servicios de Prestador"
        unique_together = ('prestador', 'codigo_servicio')
        indexes = [
            models.Index(fields=['prestador', 'estado_habilitacion']),
            models.Index(fields=['estado_habilitacion']),
        ]
    
    def __str__(self):
        return f"{self.codigo_servicio} - {self.nombre_servicio}"
    
    def dias_para_vencimiento(self):
        """Calcular días para vencimiento del servicio."""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days
    
    def esta_vencido(self):
        """Verificar si el servicio está vencido."""
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return dias_falta < 0

