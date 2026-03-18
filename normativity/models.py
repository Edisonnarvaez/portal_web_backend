"""
normativity/models.py

Modelos maestros para la taxonomía de la Resolución 3100 de 2019.
Define los Estándares y Criterios que aplican a las IPS.
"""

from django.db import models


class Estandar(models.Model):
    """
    Estándares de la Resolución 3100 de 2019.
    Los 7 estándares principales de habilitación de IPS en Colombia.
    """
    
    ESTANDAR_CHOICES = [
        ('TH', 'Talento Humano'),
        ('INF', 'Infraestructura Física'),
        ('DOT', 'Dotación, Medicamentos e Insumos'),
        ('PO', 'Procesos Organizacionales'),
        ('RS', 'Relacionamiento y Sostenibilidad'),
        ('GI', 'Garantía de Calidad e Información'),
        ('SA', 'Seguridad del Paciente y Ambiente'),
    ]
    
    codigo = models.CharField(
        max_length=10,
        unique=True,
        choices=ESTANDAR_CHOICES,
        verbose_name="Código del estándar"
    )
    nombre = models.CharField(
        max_length=255,
        verbose_name="Nombre del estándar"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción detallada"
    )
    # Metadatos
    estado = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    version_resolucion = models.CharField(
        max_length=20,
        default="3100/2019",
        verbose_name="Versión de la resolución"
    )
    
    class Meta:
        db_table = "normativity_estandar"
        verbose_name = "Estándar"
        verbose_name_plural = "Estándares"
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.get_codigo_display()} - {self.nombre}"


class Criterio(models.Model):
    """
    Criterios de evaluación dentro de cada Estándar.
    Estos criterios definen los requisitos específicos que las IPS deben cumplir.
    """
    
    COMPLEJIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]
    
    estandar = models.ForeignKey(
        Estandar,
        on_delete=models.PROTECT,
        related_name='criterios',
        verbose_name="Estándar"
    )
    codigo = models.CharField(
        max_length=20,
        verbose_name="Código del criterio",
        help_text="Ej: 1.1, 1.2, 2.1 (debe incluir el número del estándar)"
    )
    nombre = models.CharField(
        max_length=255,
        verbose_name="Nombre del criterio"
    )
    descripcion = models.TextField(
        verbose_name="Descripción del criterio"
    )
    # Propiedades del criterio
    complejidad = models.CharField(
        max_length=10,
        choices=COMPLEJIDAD_CHOICES,
        default='MEDIA',
        verbose_name="Complejidad de implementación"
    )
    aplica_todos = models.BooleanField(
        default=False,
        verbose_name="Aplica a todas las IPS",
        help_text="Si es False, aplica solo según el tipo/complejidad de la IPS"
    )
    es_mandatorio = models.BooleanField(
        default=True,
        verbose_name="Es mandatorio"
    )
    # Vinculación con documentos
    requiere_evidencia_documental = models.BooleanField(
        default=False,
        verbose_name="Requiere evidencia documental"
    )
    # Metadatos
    estado = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    notas_interpretacion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas de interpretación"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    class Meta:
        db_table = "normativity_criterio"
        verbose_name = "Criterio"
        verbose_name_plural = "Criterios"
        unique_together = ('estandar', 'codigo')
        ordering = ['estandar', 'codigo']
        indexes = [
            models.Index(fields=['estandar', 'estado']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class DocumentoNormativo(models.Model):
    """
    Referencias a documentos normativos relacionados con los criterios.
    Por ej: Resoluciones, Manuales de la Superintendencia de Salud, etc.
    """
    
    TIPO_DOCUMENTO = [
        ('RESOLUCION', 'Resolución'),
        ('ACUERDO', 'Acuerdo'),
        ('DECRETO', 'Decreto'),
        ('MANUAL', 'Manual'),
        ('GUIA', 'Guía'),
        ('CIRCULAR', 'Circular'),
        ('OTRO', 'Otro'),
    ]
    
    titulo = models.CharField(
        max_length=255,
        verbose_name="Título del documento"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO,
        verbose_name="Tipo de documento"
    )
    numero_referencia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de referencia",
        help_text="Ej: Res. 1234 de 2020"
    )
    fecha_publicacion = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de publicación"
    )
    url_documento = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL del documento"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    criterios_relacionados = models.ManyToManyField(
        Criterio,
        related_name='documentos_normativos',
        blank=True,
        verbose_name="Criterios relacionados"
    )
    
    class Meta:
        db_table = "normativity_documentonormativo"
        verbose_name = "Documento Normativo"
        verbose_name_plural = "Documentos Normativos"
        ordering = ['-fecha_publicacion']
    
    def __str__(self):
        return f"{self.tipo}: {self.titulo}"
