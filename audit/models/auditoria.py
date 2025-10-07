from django.db import models
from companies.models.process import Process
from .tipo_auditoria import TipoAuditoria 
from .entidad_auditoria import EntidadAuditoria 

class Auditoria(models.Model):
    auditoria_id = models.AutoField(primary_key=True, verbose_name="ID")
    auditoria_nombre = models.CharField(max_length=100, default="", null=True, blank=True, verbose_name="Nombre de la auditoria")
    auditoria_fecha_notificacion = models.DateField(null=True, blank=True, verbose_name="Fecha de notificación")
    auditoria_responsable = models.CharField(max_length=100, default="", null=True, blank=True, verbose_name="Responsable")
    auditoria_detalle = models.TextField(default="", null=True, blank=True, verbose_name="Detalle")
    auditoria_fecha_auditoria = models.DateField(null=True, blank=True, verbose_name="Fecha de la auditoría")
      
    auditoria_tipo = models.ForeignKey(
        TipoAuditoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tipos_auditoria',
        verbose_name="Tipos de auditoria"
    )
    auditoria_entidad = models.ForeignKey(
        EntidadAuditoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,  
        related_name='entidades_auditoria',
        verbose_name="Entidad de auditoría" 
    )
    auditoria_proceso = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias_asociadas',
        verbose_name="Proceso auditado"
    )   

    auditoria_relacionada = models.ForeignKey(  
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='relaciones_auditorias',
        verbose_name="Auditoría relacionada"
    )

    auditoria_estado = models.BooleanField(default=True)

    def __str__(self):
        return f"Auditoría {self.auditoria_nombre or self.auditoria_id}"

    class Meta:
        verbose_name = "Auditorias"
        verbose_name_plural = "Auditorias"
