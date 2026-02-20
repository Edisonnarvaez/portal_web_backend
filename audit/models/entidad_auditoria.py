"""
audit/models/entidad_auditoria.py
Catálogo de entidades auditoras.
"""
from django.db import models


class EntidadAuditoria(models.Model):
    """
    Catálogo de entidades que realizan auditorías.
    Para auditorías externas: ente contralor, aseguradora, certificadora, etc.
    Para internas: departamento, área, comité, etc.
    """
    entidad_id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre de la entidad"
    )
    tipo_entidad = models.CharField(
        max_length=30,
        choices=[
            ('ENTE_CONTROL', 'Ente de control'),
            ('CERTIFICADORA', 'Certificadora'),
            ('ASEGURADORA', 'Aseguradora'),
            ('CONSULTORA', 'Consultora'),
            ('INTERNA', 'Interna'),
            ('OTRA', 'Otra'),
        ],
        default='OTRA',
        verbose_name="Tipo de entidad"
    )
    contacto = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name="Contacto"
    )
    telefono = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name="Teléfono"
    )
    email = models.EmailField(blank=True, default='', verbose_name="Email")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auditoria_entidadauditoria"
        verbose_name = "Entidad de auditoría"
        verbose_name_plural = "Entidades de auditoría"
        ordering = ['nombre']
