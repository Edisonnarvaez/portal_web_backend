from django.db import models


class RequisitoDocumental(models.Model):
    """Catalogo de requisitos del Anexo 2 para inscripcion, novedades y visitas."""

    TIPO_TRAMITE_CHOICES = [
        ('INSCRIPCION', 'Inscripcion'),
        ('NOVEDAD', 'Novedad'),
        ('VISITA_PREVIA', 'Visita Previa'),
        ('VISITA_CERTIFICACION', 'Visita de Certificacion'),
        ('VISITA_REACTIVACION', 'Visita de Reactivacion'),
    ]

    codigo = models.CharField(max_length=30, unique=True, verbose_name='Codigo')
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    tipo_tramite = models.CharField(max_length=30, choices=TIPO_TRAMITE_CHOICES, verbose_name='Tipo de Tramite')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripcion')
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualizacion')

    class Meta:
        db_table = 'habilitacion_requisitodocumental'
        verbose_name = 'Requisito Documental'
        verbose_name_plural = 'Requisitos Documentales'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['tipo_tramite', 'activo']),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
