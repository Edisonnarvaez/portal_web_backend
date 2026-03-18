"""
audit/models/tipo_auditoria.py
Catálogo de tipos de auditoría.
"""
from django.db import models


class TipoAuditoria(models.Model):
    """
    Catálogo de tipos de auditoría.
    Ejemplos: Interna, Externa, De habilitación, De calidad, ISO, Fiscal, etc.
    """
    tipo_id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del tipo de auditoría"
    )
    descripcion = models.TextField(
        blank=True, default='',
        verbose_name="Descripción"
    )
    requiere_entidad_externa = models.BooleanField(
        default=False,
        help_text="¿Requiere entidad auditora externa?"
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auditoria_tipoauditoria"
        verbose_name = "Tipo de auditoría"
        verbose_name_plural = "Tipos de auditoría"
        ordering = ['nombre']
