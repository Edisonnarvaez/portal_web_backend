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

class Autoevaluacion(models.Model):
    """
    Autoevaluación anual de la IPS contra los criterios de la Resolución 3100.
    Control de vigencia: Las autoevaluaciones son anuales.
    """
    
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('EN_CURSO', 'En Curso'),
        ('COMPLETADA', 'Completada'),
        ('REVISADA', 'Revisada por Auditor'),
        ('VALIDADA', 'Validada'),
    ]
    
    PERIODO_CHOICES = [
        (2024, '2024'),
        (2025, '2025'),
        (2026, '2026'),
        (2027, '2027'),
        (2028, '2028'),
    ]
    
    datos_prestador = models.ForeignKey(DatosSede,on_delete=models.PROTECT,related_name='autoevaluaciones',verbose_name="Prestador")
    # Identificación
    periodo = models.IntegerField(choices=PERIODO_CHOICES,verbose_name="Período Fiscal")
    numero_autoevaluacion = models.CharField(max_length=50,verbose_name="Número de Autoevaluación",help_text="Identificador único: AUT-CODIGO_REPS-PERIODO")
    # Control de versiones
    version = models.PositiveIntegerField(default=1,verbose_name="Versión")
    # Fechas
    fecha_inicio = models.DateField(auto_now_add=True,verbose_name="Fecha de Inicio")
    fecha_completacion = models.DateField(blank=True,null=True,verbose_name="Fecha de Completación")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento",help_text="Fecha hasta la cual esta autoevaluación es válida")
    # Estado
    estado = models.CharField(max_length=20,choices=ESTADO_CHOICES,default='BORRADOR',verbose_name="Estado")
    # Responsable
    usuario_responsable = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='autoevaluaciones_responsable',verbose_name="Responsable")
    # Notas
    observaciones = models.TextField(blank=True,null=True,verbose_name="Observaciones")
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True,verbose_name="Fecha de Actualización")
    
    class Meta:
        db_table = "habilitacion_autoevaluacion"
        verbose_name = "Autoevaluación"
        verbose_name_plural = "Autoevaluaciones"
        unique_together = ('datos_prestador', 'periodo', 'version')
        ordering = ['-periodo', '-version']
        indexes = [
            models.Index(fields=['datos_prestador', 'periodo']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"AUT-{self.datos_prestador.codigo_reps}-{self.periodo} v{self.version}"
    
    def save(self, *args, **kwargs):
        """Generar automáticamente el número de autoevaluación si no existe."""
        if not self.numero_autoevaluacion:
            self.numero_autoevaluacion = f"AUT-{self.datos_prestador.codigo_reps}-{self.periodo}"
        super().save(*args, **kwargs)
    
    def porcentaje_cumplimiento(self):
        """Calcular porcentaje general de cumplimiento."""
        total = self.cumplimientos.count()
        if total == 0:
            return 0
        # Contar solo CUMPLE y PARCIALMENTE como cumplimientos
        cumplidos = self.cumplimientos.filter(
            cumple__in=['CUMPLE', 'PARCIALMENTE']
        ).count()
        return round((cumplidos / total) * 100, 2)
    
    def esta_vigente(self):
        """Verificar si la autoevaluación está vigente."""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento >= timezone.now().date()

