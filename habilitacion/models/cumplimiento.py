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

class Cumplimiento(models.Model):
    """
    Registro de cumplimiento de un criterio específico.
    Pivote: Autoevaluacion + ServicioSede + Criterio.
    
    Enlaza la autoevaluación con la evidencia documental (app processes).
    """
    
    RESULTADO_CHOICES = [
        ('CUMPLE', 'Cumple'),
        ('NO_CUMPLE', 'No Cumple'),
        ('PARCIALMENTE', 'Parcialmente'),
        ('NO_APLICA', 'No Aplica'),
    ]
    
    autoevaluacion = models.ForeignKey(Autoevaluacion,on_delete=models.PROTECT,related_name='cumplimientos',verbose_name="Autoevaluación")
    servicio_sede = models.ForeignKey(ServicioSede,on_delete=models.PROTECT,related_name='cumplimientos',verbose_name="Servicio de Sede")
    criterio = models.ForeignKey(Criterio,on_delete=models.PROTECT,related_name='cumplimientos',verbose_name="Criterio")
    # Evaluación
    cumple = models.CharField(max_length=20,choices=RESULTADO_CHOICES,verbose_name="Resultado de Cumplimiento")
    # Evidencia
    documentos_evidencia = models.ManyToManyField(Documento,blank=True,related_name='cumplimientos',verbose_name="Documentos de Evidencia")
    # Análisis
    hallazgo = models.TextField(blank=True,null=True,verbose_name="Hallazgo/Observación")
    plan_mejora = models.TextField(blank=True,null=True,verbose_name="Plan de Mejora")
    responsable_mejora = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='cumplimientos_responsable',verbose_name="Responsable de Mejora")
    fecha_compromiso = models.DateField(blank=True,null=True,verbose_name="Fecha Comprometida para Mejora")
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True,verbose_name="Fecha de Actualización")
    
    class Meta:
        db_table = "habilitacion_cumplimiento"
        verbose_name = "Cumplimiento"
        verbose_name_plural = "Cumplimientos"
        unique_together = ('autoevaluacion', 'servicio_sede', 'criterio')
        indexes = [
            models.Index(fields=['autoevaluacion', 'cumple']),
            models.Index(fields=['criterio']),
        ]
    
    def __str__(self):
        return f"{self.autoevaluacion} - {self.criterio.codigo}: {self.cumple}"
    
    def tiene_plan_mejora(self):
        """Verificar si hay plan de mejora pendiente."""
        return self.plan_mejora and not self.fecha_compromiso
    
    def mejora_vencida(self):
        """Verificar si la fecha de compromiso ya pasó."""
        if not self.fecha_compromiso:
            return False
        return self.fecha_compromiso < timezone.now().date()


ALLOWED_CHECKLIST_EXTENSIONS = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.xls', '.xlsx']


def checklist_upload_path(instance, filename):
    """Ruta de soportes del checklist: media/habilitacion/checklists/<id>/<uuid>_archivo."""
    unique_name = f"{uuid.uuid4().hex[:12]}_{filename}"
    checklist_id = instance.checklist_item.checklist_id if instance.checklist_item_id else 'sin_checklist'
    return os.path.join('habilitacion', 'checklists', str(checklist_id), unique_name)


def validate_checklist_extension(value):
    """Valida extensiones permitidas para soportes documentales de checklist."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_CHECKLIST_EXTENSIONS:
        raise ValidationError(
            f'Extensión "{ext}" no permitida. '
            f'Extensiones válidas: {", ".join(ALLOWED_CHECKLIST_EXTENSIONS)}'
        )

