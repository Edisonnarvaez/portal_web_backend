from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from companies.models import Headquarters

User = get_user_model()


class DatosPrestador(models.Model):
    """Datos especificos de habilitacion vinculados a una sede."""

    CLASE_PRESTADOR_CHOICES = [
        ('IPS', 'Institucion Prestadora de Servicios'),
        ('PROF', 'Profesional de Salud'),
        ('PH', 'Persona Humana'),
        ('PJ', 'Persona Juridica'),
    ]

    ESTADO_HABILITACION_CHOICES = [
        ('HABILITADA', 'Habilitada'),
        ('EN_PROCESO', 'En Proceso'),
        ('SUSPENDIDA', 'Suspendida'),
        ('NO_HABILITADA', 'No Habilitada'),
        ('CANCELADA', 'Cancelada'),
    ]

    headquarters = models.ForeignKey(
        Headquarters,
        on_delete=models.PROTECT,
        related_name='prestadores_habilitados',
        verbose_name='Sede (Headquarters)',
    )
    codigo_reps = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Codigo REPS',
        help_text='Codigo de registro en REPS de la Superintendencia de Salud',
    )
    nombre_prestador = models.CharField(
        max_length=255,
        verbose_name='Nombre del Prestador',
        help_text='Nombre del prestador de servicios de salud',
    )
    sede_principal = models.BooleanField(
        default=False,
        verbose_name='Es Sede Principal',
        help_text='Indica si esta es la sede principal del prestador',
    )
    clase_prestador = models.CharField(
        max_length=10,
        choices=CLASE_PRESTADOR_CHOICES,
        verbose_name='Clase de Prestador',
    )
    estado_habilitacion = models.CharField(
        max_length=20,
        choices=ESTADO_HABILITACION_CHOICES,
        default='EN_PROCESO',
        verbose_name='Estado de Habilitacion',
    )
    fecha_inscripcion = models.DateField(blank=True, null=True, verbose_name='Fecha de Inscripcion en REPS')
    fecha_renovacion = models.DateField(blank=True, null=True, verbose_name='Fecha de Ultima Renovacion')
    fecha_vencimiento_habilitacion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Vencimiento de Habilitacion',
    )
    aseguradora_pep = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Aseguradora de Responsabilidad Civil',
    )
    numero_poliza = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numero de Poliza')
    vigencia_poliza = models.DateField(blank=True, null=True, verbose_name='Vigencia de Poliza')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='datos_prestador_creado',
        verbose_name='Usuario Responsable',
    )

    class Meta:
        db_table = 'habilitacion_datosprestador'
        verbose_name = 'Datos de Prestador'
        verbose_name_plural = 'Datos de Prestadores'

    def __str__(self):
        return f'{self.codigo_reps} - {self.headquarters.name}'

    def dias_para_vencimiento(self):
        if not self.fecha_vencimiento_habilitacion:
            return None
        delta = self.fecha_vencimiento_habilitacion - timezone.now().date()
        return delta.days

    def esta_proxima_a_vencer(self, dias=90):
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return 0 <= dias_falta <= dias

    def esta_vencida(self):
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return dias_falta < 0


DatosSede = DatosPrestador
