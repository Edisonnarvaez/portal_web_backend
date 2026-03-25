from django.db import models


class CapacidadInstalada(models.Model):
    """Capacidad instalada reportada por servicio (REPS)."""

    TIPO_CHOICES = [
        ('AMBULANCIA', 'Ambulancias'),
        ('CAMA', 'Camas'),
        ('APOYO_TERAPEUTICO', 'Apoyo Terapeutico'),
        ('SALA', 'Salas'),
        ('OTRO', 'Otro'),
    ]

    servicio_sede = models.ForeignKey(
        'ServicioSede',
        on_delete=models.CASCADE,
        related_name='capacidades_instaladas',
        verbose_name='Servicio de Sede',
    )
    tipo_capacidad = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo de Capacidad')
    subtipo = models.CharField(max_length=120, blank=True, null=True, verbose_name='Subtipo')
    cantidad = models.PositiveIntegerField(default=0, verbose_name='Cantidad')
    unidad = models.CharField(max_length=40, blank=True, null=True, verbose_name='Unidad')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_capacidadinstalada'
        verbose_name = 'Capacidad Instalada'
        verbose_name_plural = 'Capacidades Instaladas'
        indexes = [
            models.Index(fields=['servicio_sede', 'tipo_capacidad']),
            models.Index(fields=['tipo_capacidad']),
        ]

    def __str__(self):
        return f'{self.servicio_sede.codigo_servicio} - {self.get_tipo_capacidad_display()} ({self.cantidad})'
