from django.db import models


class MedidaSeguridadServicio(models.Model):
    """Medidas de seguridad aplicadas al servicio habilitado."""

    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('LEVANTADA', 'Levantada'),
        ('EN_SEGUIMIENTO', 'En Seguimiento'),
    ]

    servicio_sede = models.ForeignKey(
        'ServicioSede',
        on_delete=models.PROTECT,
        related_name='medidas_seguridad',
        verbose_name='Servicio de Sede',
    )
    norma_referencia = models.CharField(
        max_length=120,
        default='Ley 9 de 1979 - Articulo 576',
        verbose_name='Norma de Referencia',
    )
    descripcion = models.TextField(verbose_name='Descripcion de la Medida')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVA', verbose_name='Estado')
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')
    autoridad = models.CharField(max_length=200, blank=True, null=True, verbose_name='Autoridad')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_medidaseguridad'
        verbose_name = 'Medida de Seguridad'
        verbose_name_plural = 'Medidas de Seguridad'
        indexes = [
            models.Index(fields=['servicio_sede', 'estado']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'{self.servicio_sede.codigo_servicio} - {self.estado}'
