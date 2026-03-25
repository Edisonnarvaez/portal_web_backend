from django.db import models
from django.utils import timezone


class ServicioSede(models.Model):
    """Servicios de salud habilitados en una sede especifica."""

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

    prestador = models.ForeignKey(
        'DatosPrestador',
        on_delete=models.PROTECT,
        related_name='servicios_salud',
        verbose_name='Prestador',
    )
    codigo_servicio = models.CharField(
        max_length=20,
        verbose_name='Codigo del Servicio',
        help_text='Codigo asignado por REPS para este servicio',
    )
    nombre_servicio = models.CharField(max_length=255, verbose_name='Nombre del Servicio')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripcion del Servicio')
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, verbose_name='Modalidad')
    complejidad = models.CharField(max_length=10, choices=COMPLEJIDAD_CHOICES, verbose_name='Complejidad')
    estado_habilitacion = models.CharField(
        max_length=20,
        choices=ESTADO_HABILITACION_CHOICES,
        default='EN_PROCESO',
        verbose_name='Estado de Habilitacion',
    )
    fecha_habilitacion = models.DateField(blank=True, null=True, verbose_name='Fecha de Habilitacion')
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_serviciosede'
        verbose_name = 'Servicio de Prestador'
        verbose_name_plural = 'Servicios de Prestador'
        unique_together = ('prestador', 'codigo_servicio')
        indexes = [
            models.Index(fields=['prestador', 'estado_habilitacion']),
            models.Index(fields=['estado_habilitacion']),
        ]

    def __str__(self):
        return f'{self.codigo_servicio} - {self.nombre_servicio}'

    def dias_para_vencimiento(self):
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days

    def esta_vencido(self):
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return dias_falta < 0
