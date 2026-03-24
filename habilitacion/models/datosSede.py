"""
habilitacion/models/DatosSede.py

Modelos transaccionales para la habilitación de servicios de salud.
Integración con los modelos core (Company, Headquarters).
DatosSede vinculado a Headquarters (OneToOne) para permitir habilitación
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


class DatosSede(models.Model):
    """
    Datos específicos de habilitación vinculados a una Headquarters (Sede).
    ForeignKey: Una sede puede tener múltiples prestadores habilitados.
    Cada prestador está identificado únicamente por su código REPS.
    """
    
    CLASE_PRESTADOR_CHOICES = [
        ('IPS', 'Institución Prestadora de Servicios'),
        ('PROF', 'Profesional de Salud'),
        ('PH', 'Persona Humana'),
        ('PJ', 'Persona Jurídica'),
    ]
    
    ESTADO_HABILITACION_CHOICES = [
        ('HABILITADA', 'Habilitada'),
        ('EN_PROCESO', 'En Proceso'),
        ('SUSPENDIDA', 'Suspendida'),
        ('NO_HABILITADA', 'No Habilitada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    headquarters = models.ForeignKey(Headquarters,on_delete=models.PROTECT,related_name='prestadores_habilitados',verbose_name="Sede (Headquarters)")
    # Identificación REPS
    codigo_reps = models.CharField(max_length=20,unique=True,verbose_name="Código REPS",help_text="Código de registro en REPS de la Superintendencia de Salud")
    nombre_sede = models.CharField(max_length=255,verbose_name="Nombre de la Sede",help_text="Nombre de la sede de servicios de salud")
    sede_principal = models.BooleanField(default=False,verbose_name="Es Sede Principal",help_text="Indica si esta es la sede principal del prestador")
    clase_sede = models.CharField(max_length=10,choices=CLASE_PRESTADOR_CHOICES,verbose_name="Clase de Prestador")
    # Información de habilitación
    estado_habilitacion = models.CharField(max_length=20,choices=ESTADO_HABILITACION_CHOICES,default='EN_PROCESO',verbose_name="Estado de Habilitación")
    fecha_inscripcion = models.DateField(blank=True,null=True,verbose_name="Fecha de Inscripción en REPS")
    fecha_renovacion = models.DateField(blank=True,null=True,verbose_name="Fecha de Última Renovación")
    fecha_vencimiento_habilitacion = models.DateField(blank=True,null=True,verbose_name="Fecha de Vencimiento de Habilitación")
    # Información complementaria
    aseguradora_pep = models.CharField(max_length=255,blank=True,null=True,verbose_name="Aseguradora de Responsabilidad Civil")
    numero_poliza = models.CharField(max_length=50,blank=True,null=True,verbose_name="Número de Póliza")
    vigencia_poliza = models.DateField(blank=True,null=True,verbose_name="Vigencia de Póliza")
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True,verbose_name="Fecha de Actualización")
    usuario_responsable = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='datos_prestador_creado',verbose_name="Usuario Responsable")
    
    class Meta:
        db_table = "habilitacion_datosprestador"
        verbose_name = "Datos de Prestador"
        verbose_name_plural = "Datos de Prestadores"
    
    def __str__(self):
        return f"{self.codigo_reps} - {self.headquarters.name}"
    
    def dias_para_vencimiento(self):
        """Calcular días para vencimiento de habilitación."""
        if not self.fecha_vencimiento_habilitacion:
            return None
        delta = self.fecha_vencimiento_habilitacion - timezone.now().date()
        return delta.days
    
    def esta_proxima_a_vencer(self, dias=90):
        """Verificar si la habilitación está próxima a vencer."""
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return 0 <= dias_falta <= dias
    
    def esta_vencida(self):
        """Verificar si la habilitación ya venció."""
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return dias_falta < 0


