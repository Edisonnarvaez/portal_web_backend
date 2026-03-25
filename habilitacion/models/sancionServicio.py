from django.db import models


class SancionServicio(models.Model):
    """Sanciones aplicadas al servicio habilitado."""

    TIPO_CHOICES = [
        ('PECUNIARIA', 'Pecuniaria'),
        ('TEMPORAL', 'Suspension Temporal'),
        ('DEFINITIVA', 'Cierre Definitivo'),
        ('OTRA', 'Otra'),
    ]

    ESTADO_CHOICES = [
        ('VIGENTE', 'Vigente'),
        ('CUMPLIDA', 'Cumplida'),
        ('REVOCADA', 'Revocada'),
    ]

    servicio_sede = models.ForeignKey(
        'ServicioSede',
        on_delete=models.CASCADE,
        related_name='sanciones',
        verbose_name='Servicio de Sede',
    )
    norma_referencia = models.CharField(
        max_length=120,
        default='Ley 9 de 1979 - Articulo 577',
        verbose_name='Norma de Referencia',
    )
    tipo_sancion = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Sancion')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='VIGENTE', verbose_name='Estado')
    acto_administrativo = models.CharField(max_length=120, blank=True, null=True, verbose_name='Acto Administrativo')
    autoridad = models.CharField(max_length=200, blank=True, null=True, verbose_name='Autoridad')
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripcion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_sancionservicio'
        verbose_name = 'Sancion de Servicio'
        verbose_name_plural = 'Sanciones de Servicio'
        indexes = [
            models.Index(fields=['servicio_sede', 'estado']),
            models.Index(fields=['tipo_sancion']),
        ]

    def __str__(self):
        return f'{self.servicio_sede.codigo_servicio} - {self.get_tipo_sancion_display()}'
