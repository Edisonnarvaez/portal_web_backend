from datetime import date

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Autoevaluacion(models.Model):
    """Autoevaluacion anual de la IPS contra los criterios de la Resolucion 3100."""

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

    datos_prestador = models.ForeignKey(
        'DatosPrestador',
        on_delete=models.PROTECT,
        related_name='autoevaluaciones',
        verbose_name='Prestador',
    )
    periodo = models.IntegerField(choices=PERIODO_CHOICES, verbose_name='Periodo Fiscal')
    numero_autoevaluacion = models.CharField(
        max_length=50,
        verbose_name='Numero de Autoevaluacion',
        help_text='Identificador unico: AUT-CODIGO_REPS-PERIODO',
    )
    version = models.PositiveIntegerField(default=1, verbose_name='Version')
    fecha_inicio = models.DateField(auto_now_add=True, verbose_name='Fecha de Inicio')
    fecha_completacion = models.DateField(blank=True, null=True, verbose_name='Fecha de Completacion')
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Vencimiento',
        help_text='Fecha hasta la cual esta autoevaluacion es valida',
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR', verbose_name='Estado')
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='autoevaluaciones_responsable',
        verbose_name='Responsable',
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_autoevaluacion'
        verbose_name = 'Autoevaluacion'
        verbose_name_plural = 'Autoevaluaciones'
        unique_together = ('datos_prestador', 'periodo', 'version')
        ordering = ['-periodo', '-version']
        indexes = [
            models.Index(fields=['datos_prestador', 'periodo']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'AUT-{self.datos_prestador.codigo_reps}-{self.periodo} v{self.version}'

    def save(self, *args, **kwargs):
        if not self.numero_autoevaluacion:
            self.numero_autoevaluacion = f'AUT-{self.datos_prestador.codigo_reps}-{self.periodo}'
        if not self.fecha_vencimiento and self.periodo:
            self.fecha_vencimiento = date(self.periodo, 12, 31)
        super().save(*args, **kwargs)

    def porcentaje_cumplimiento(self):
        total = self.cumplimientos.count()
        if total == 0:
            return 0
        cumplidos = self.cumplimientos.filter(cumple__in=['CUMPLE', 'PARCIALMENTE']).count()
        return round((cumplidos / total) * 100, 2)

    def esta_vigente(self):
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento >= timezone.now().date()
