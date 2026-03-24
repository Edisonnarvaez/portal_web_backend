"""
habilitacion/models.py

Modelos transaccionales para la habilitación de servicios de salud.
Integración con los modelos core (Company, Headquarters).
DatosPrestador vinculado a Headquarters (OneToOne) para permitir habilitación
de una única sede o múltiples sedes de la misma empresa.
"""

from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import os
import uuid

from companies.models import Company, Headquarters
from normativity.models import Criterio
from processes.models import Documento

User = get_user_model()


class DatosPrestador(models.Model):
    """
    Datos específicos de habilitación vinculados a una Headquarters (Sede).
    ForeignKey: Una sede puede tener múltiples prestadores habilitados.
    Cada prestador está identificado únicamente por su código REPS.
    """
    
    CLASE_PRESTADOR_CHOICES = [
        ('IPS', 'Institución Prestadora de Servicios'),
        ('PROF', 'Profesional de Salud'),
        ('PH', 'Persona Humana'),
        ('PJ', 'Persona Jurídica'),
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
        verbose_name="Sede (Headquarters)"
    )
    
    # Identificación REPS
    codigo_reps = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código REPS",
        help_text="Código de registro en REPS de la Superintendencia de Salud"
    )
    nombre_prestador = models.CharField(
        max_length=255,
        verbose_name="Nombre del Prestador",
        help_text="Nombre del prestador de servicios de salud"
    )
    sede_principal = models.BooleanField(
        default=False,
        verbose_name="Es Sede Principal",
        help_text="Indica si esta es la sede principal del prestador"
    )
    clase_prestador = models.CharField(
        max_length=10,
        choices=CLASE_PRESTADOR_CHOICES,
        verbose_name="Clase de Prestador"
    )
    
    # Información de habilitación
    estado_habilitacion = models.CharField(
        max_length=20,
        choices=ESTADO_HABILITACION_CHOICES,
        default='EN_PROCESO',
        verbose_name="Estado de Habilitación"
    )
    fecha_inscripcion = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Inscripción en REPS"
    )
    fecha_renovacion = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Última Renovación"
    )
    fecha_vencimiento_habilitacion = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Vencimiento de Habilitación"
    )
    
    # Información complementaria
    aseguradora_pep = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Aseguradora de Responsabilidad Civil"
    )
    numero_poliza = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número de Póliza"
    )
    vigencia_poliza = models.DateField(
        blank=True,
        null=True,
        verbose_name="Vigencia de Póliza"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='datos_prestador_creado',
        verbose_name="Usuario Responsable"
    )
    
    class Meta:
        db_table = "habilitacion_datosprestador"
        verbose_name = "Datos de Prestador"
        verbose_name_plural = "Datos de Prestadores"
    
    def __str__(self):
        return f"{self.codigo_reps} - {self.headquarters.name}"
    
    def dias_para_vencimiento(self):
        """Calcular días para vencimiento de habilitación."""
        if not self.fecha_vencimiento_habilitacion:
            return None
        delta = self.fecha_vencimiento_habilitacion - timezone.now().date()
        return delta.days
    
    def esta_proxima_a_vencer(self, dias=90):
        """Verificar si la habilitación está próxima a vencer."""
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return 0 <= dias_falta <= dias
    
    def esta_vencida(self):
        """Verificar si la habilitación ya venció."""
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return dias_falta < 0


class ServicioSede(models.Model):
    """
    Servicios de salud habilitados en una sede específica.
    Un servicio es la combinación de modalidad + tipo en una sede determinada.
    """
    
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
        DatosPrestador,
        on_delete=models.PROTECT,
        related_name='servicios_salud',
        verbose_name="Prestador",
    )
    
    # Identificación del servicio
    codigo_servicio = models.CharField(
        max_length=20,
        verbose_name="Código del Servicio",
        help_text="Código asignado por REPS para este servicio"
    )
    nombre_servicio = models.CharField(
        max_length=255,
        verbose_name="Nombre del Servicio"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción del Servicio"
    )
    
    # Clasificación
    modalidad = models.CharField(
        max_length=20,
        choices=MODALIDAD_CHOICES,
        verbose_name="Modalidad"
    )
    complejidad = models.CharField(
        max_length=10,
        choices=COMPLEJIDAD_CHOICES,
        verbose_name="Complejidad"
    )
    
    # Estado
    estado_habilitacion = models.CharField(
        max_length=20,
        choices=ESTADO_HABILITACION_CHOICES,
        default='EN_PROCESO',
        verbose_name="Estado de Habilitación"
    )
    fecha_habilitacion = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Habilitación"
    )
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Vencimiento"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        db_table = "habilitacion_serviciosede"
        verbose_name = "Servicio de Prestador"
        verbose_name_plural = "Servicios de Prestador"
        unique_together = ('prestador', 'codigo_servicio')
        indexes = [
            models.Index(fields=['prestador', 'estado_habilitacion']),
            models.Index(fields=['estado_habilitacion']),
        ]
    
    def __str__(self):
        return f"{self.codigo_servicio} - {self.nombre_servicio}"
    
    def dias_para_vencimiento(self):
        """Calcular días para vencimiento del servicio."""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days
    
    def esta_vencido(self):
        """Verificar si el servicio está vencido."""
        dias_falta = self.dias_para_vencimiento()
        if dias_falta is None:
            return False
        return dias_falta < 0


class Autoevaluacion(models.Model):
    """
    Autoevaluación anual de la IPS contra los criterios de la Resolución 3100.
    Control de vigencia: Las autoevaluaciones son anuales.
    """
    
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
        DatosPrestador,
        on_delete=models.PROTECT,
        related_name='autoevaluaciones',
        verbose_name="Prestador"
    )
    
    # Identificación
    periodo = models.IntegerField(
        choices=PERIODO_CHOICES,
        verbose_name="Período Fiscal"
    )
    numero_autoevaluacion = models.CharField(
        max_length=50,
        verbose_name="Número de Autoevaluación",
        help_text="Identificador único: AUT-CODIGO_REPS-PERIODO"
    )
    
    # Control de versiones
    version = models.PositiveIntegerField(
        default=1,
        verbose_name="Versión"
    )
    
    # Fechas
    fecha_inicio = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha de Inicio"
    )
    fecha_completacion = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Completación"
    )
    fecha_vencimiento = models.DateField(
        verbose_name="Fecha de Vencimiento",
        help_text="Fecha hasta la cual esta autoevaluación es válida"
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='BORRADOR',
        verbose_name="Estado"
    )
    
    # Responsable
    usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='autoevaluaciones_responsable',
        verbose_name="Responsable"
    )
    
    # Notas
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        db_table = "habilitacion_autoevaluacion"
        verbose_name = "Autoevaluación"
        verbose_name_plural = "Autoevaluaciones"
        unique_together = ('datos_prestador', 'periodo', 'version')
        ordering = ['-periodo', '-version']
        indexes = [
            models.Index(fields=['datos_prestador', 'periodo']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"AUT-{self.datos_prestador.codigo_reps}-{self.periodo} v{self.version}"
    
    def save(self, *args, **kwargs):
        """Generar automáticamente el número de autoevaluación si no existe."""
        if not self.numero_autoevaluacion:
            self.numero_autoevaluacion = f"AUT-{self.datos_prestador.codigo_reps}-{self.periodo}"
        super().save(*args, **kwargs)
    
    def porcentaje_cumplimiento(self):
        """Calcular porcentaje general de cumplimiento."""
        total = self.cumplimientos.count()
        if total == 0:
            return 0
        # Contar solo CUMPLE y PARCIALMENTE como cumplimientos
        cumplidos = self.cumplimientos.filter(
            cumple__in=['CUMPLE', 'PARCIALMENTE']
        ).count()
        return round((cumplidos / total) * 100, 2)
    
    def esta_vigente(self):
        """Verificar si la autoevaluación está vigente."""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento >= timezone.now().date()


class Cumplimiento(models.Model):
    """
    Registro de cumplimiento de un criterio específico.
    Pivote: Autoevaluacion + ServicioSede + Criterio.
    
    Enlaza la autoevaluación con la evidencia documental (app processes).
    """
    
    RESULTADO_CHOICES = [
        ('CUMPLE', 'Cumple'),
        ('NO_CUMPLE', 'No Cumple'),
        ('PARCIALMENTE', 'Parcialmente'),
        ('NO_APLICA', 'No Aplica'),
    ]
    
    autoevaluacion = models.ForeignKey(
        Autoevaluacion,
        on_delete=models.PROTECT,
        related_name='cumplimientos',
        verbose_name="Autoevaluación"
    )
    servicio_sede = models.ForeignKey(
        ServicioSede,
        on_delete=models.PROTECT,
        related_name='cumplimientos',
        verbose_name="Servicio de Sede"
    )
    criterio = models.ForeignKey(
        Criterio,
        on_delete=models.PROTECT,
        related_name='cumplimientos',
        verbose_name="Criterio"
    )
    
    # Evaluación
    cumple = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        verbose_name="Resultado de Cumplimiento"
    )
    
    # Evidencia
    documentos_evidencia = models.ManyToManyField(
        Documento,
        blank=True,
        related_name='cumplimientos',
        verbose_name="Documentos de Evidencia"
    )
    
    # Análisis
    hallazgo = models.TextField(
        blank=True,
        null=True,
        verbose_name="Hallazgo/Observación"
    )
    plan_mejora = models.TextField(
        blank=True,
        null=True,
        verbose_name="Plan de Mejora"
    )
    responsable_mejora = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cumplimientos_responsable',
        verbose_name="Responsable de Mejora"
    )
    fecha_compromiso = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha Comprometida para Mejora"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        db_table = "habilitacion_cumplimiento"
        verbose_name = "Cumplimiento"
        verbose_name_plural = "Cumplimientos"
        unique_together = ('autoevaluacion', 'servicio_sede', 'criterio')
        indexes = [
            models.Index(fields=['autoevaluacion', 'cumple']),
            models.Index(fields=['criterio']),
        ]
    
    def __str__(self):
        return f"{self.autoevaluacion} - {self.criterio.codigo}: {self.cumple}"
    
    def tiene_plan_mejora(self):
        """Verificar si hay plan de mejora pendiente."""
        return self.plan_mejora and not self.fecha_compromiso
    
    def mejora_vencida(self):
        """Verificar si la fecha de compromiso ya pasó."""
        if not self.fecha_compromiso:
            return False
        return self.fecha_compromiso < timezone.now().date()


ALLOWED_CHECKLIST_EXTENSIONS = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.xls', '.xlsx']


def checklist_upload_path(instance, filename):
    """Ruta de soportes del checklist: media/habilitacion/checklists/<id>/<uuid>_archivo."""
    unique_name = f"{uuid.uuid4().hex[:12]}_{filename}"
    checklist_id = instance.checklist_item.checklist_id if instance.checklist_item_id else 'sin_checklist'
    return os.path.join('habilitacion', 'checklists', str(checklist_id), unique_name)


def validate_checklist_extension(value):
    """Valida extensiones permitidas para soportes documentales de checklist."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_CHECKLIST_EXTENSIONS:
        raise ValidationError(
            f'Extensión "{ext}" no permitida. '
            f'Extensiones válidas: {", ".join(ALLOWED_CHECKLIST_EXTENSIONS)}'
        )


class CapacidadInstalada(models.Model):
    """Capacidad instalada reportada por servicio (REPS)."""

    TIPO_CHOICES = [
        ('AMBULANCIA', 'Ambulancias'),
        ('CAMA', 'Camas'),
        ('APOYO_TERAPEUTICO', 'Apoyo Terapéutico'),
        ('SALA', 'Salas'),
        ('OTRO', 'Otro'),
    ]

    servicio_sede = models.ForeignKey(
        ServicioSede,
        on_delete=models.CASCADE,
        related_name='capacidades_instaladas',
        verbose_name='Servicio de Sede'
    )
    tipo_capacidad = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Capacidad'
    )
    subtipo = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name='Subtipo'
    )
    cantidad = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad'
    )
    unidad = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Unidad'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_capacidadinstalada'
        verbose_name = 'Capacidad Instalada'
        verbose_name_plural = 'Capacidades Instaladas'
        indexes = [
            models.Index(fields=['servicio_sede', 'tipo_capacidad']),
            models.Index(fields=['tipo_capacidad']),
        ]

    def __str__(self):
        return f"{self.servicio_sede.codigo_servicio} - {self.get_tipo_capacidad_display()} ({self.cantidad})"


class MedidaSeguridadServicio(models.Model):
    """Medidas de seguridad aplicadas al servicio habilitado."""

    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('LEVANTADA', 'Levantada'),
        ('EN_SEGUIMIENTO', 'En Seguimiento'),
    ]

    servicio_sede = models.ForeignKey(
        ServicioSede,
        on_delete=models.CASCADE,
        related_name='medidas_seguridad',
        verbose_name='Servicio de Sede'
    )
    norma_referencia = models.CharField(
        max_length=120,
        default='Ley 9 de 1979 - Artículo 576',
        verbose_name='Norma de Referencia'
    )
    descripcion = models.TextField(verbose_name='Descripción de la Medida')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVA', verbose_name='Estado')
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')
    autoridad = models.CharField(max_length=200, blank=True, null=True, verbose_name='Autoridad')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_medidaseguridad'
        verbose_name = 'Medida de Seguridad'
        verbose_name_plural = 'Medidas de Seguridad'
        indexes = [
            models.Index(fields=['servicio_sede', 'estado']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.servicio_sede.codigo_servicio} - {self.estado}"


class SancionServicio(models.Model):
    """Sanciones aplicadas al servicio habilitado."""

    TIPO_CHOICES = [
        ('PECUNIARIA', 'Pecuniaria'),
        ('TEMPORAL', 'Suspensión Temporal'),
        ('DEFINITIVA', 'Cierre Definitivo'),
        ('OTRA', 'Otra'),
    ]

    ESTADO_CHOICES = [
        ('VIGENTE', 'Vigente'),
        ('CUMPLIDA', 'Cumplida'),
        ('REVOCADA', 'Revocada'),
    ]

    servicio_sede = models.ForeignKey(
        ServicioSede,
        on_delete=models.CASCADE,
        related_name='sanciones',
        verbose_name='Servicio de Sede'
    )
    norma_referencia = models.CharField(
        max_length=120,
        default='Ley 9 de 1979 - Artículo 577',
        verbose_name='Norma de Referencia'
    )
    tipo_sancion = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Sanción')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='VIGENTE', verbose_name='Estado')
    acto_administrativo = models.CharField(max_length=120, blank=True, null=True, verbose_name='Acto Administrativo')
    autoridad = models.CharField(max_length=200, blank=True, null=True, verbose_name='Autoridad')
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_sancionservicio'
        verbose_name = 'Sanción de Servicio'
        verbose_name_plural = 'Sanciones de Servicio'
        indexes = [
            models.Index(fields=['servicio_sede', 'estado']),
            models.Index(fields=['tipo_sancion']),
        ]

    def __str__(self):
        return f"{self.servicio_sede.codigo_servicio} - {self.get_tipo_sancion_display()}"


class NovedadREPS(models.Model):
    """Novedad reportada al REPS para prestador, sede, servicio o capacidad instalada."""

    TIPO_CHOICES = [
        ('PRESTADOR', 'Novedad del Prestador'),
        ('SEDE', 'Novedad de la Sede'),
        ('SERVICIO', 'Novedad de Servicios'),
        ('CAPACIDAD', 'Novedad de Capacidad Instalada'),
    ]

    SUBTIPO_CHOICES = [
        ('CAMBIO_CONTACTO', 'Cambio de datos de contacto'),
        ('REACTIVACION', 'Reactivación del servicio'),
        ('APERTURA_MODALIDAD', 'Apertura de modalidad'),
        ('CIERRE_MODALIDAD', 'Cierre de modalidad'),
        ('CAMBIO_HORARIO', 'Cambio de horario de prestación'),
        ('CAMBIO_COMPLEJIDAD', 'Cambio de complejidad'),
        ('TRASLADO_SERVICIO', 'Traslado de servicio'),
        ('OTRA', 'Otra'),
    ]

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('RADICADA', 'Radicada'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('APLICADA', 'Aplicada en REPS'),
    ]

    codigo_novedad = models.CharField(max_length=60, unique=True, verbose_name='Código de Novedad')
    tipo_novedad = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Novedad')
    subtipo_novedad = models.CharField(max_length=30, choices=SUBTIPO_CHOICES, verbose_name='Subtipo de Novedad')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR', verbose_name='Estado')

    datos_prestador = models.ForeignKey(
        DatosPrestador,
        on_delete=models.CASCADE,
        related_name='novedades_reps',
        verbose_name='Prestador'
    )
    sede = models.ForeignKey(
        Headquarters,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='novedades_reps',
        verbose_name='Sede'
    )
    servicio_sede = models.ForeignKey(
        ServicioSede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='novedades_reps',
        verbose_name='Servicio'
    )
    requiere_visita_previa = models.BooleanField(default=False, verbose_name='Requiere Visita Previa')
    fecha_radicacion = models.DateField(blank=True, null=True, verbose_name='Fecha de Radicación')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='novedades_reps_creadas',
        verbose_name='Creado por'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_novedadreps'
        verbose_name = 'Novedad REPS'
        verbose_name_plural = 'Novedades REPS'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['tipo_novedad', 'estado']),
            models.Index(fields=['datos_prestador', 'estado']),
        ]

    def __str__(self):
        return f"{self.codigo_novedad} - {self.get_tipo_novedad_display()}"


class RequisitoDocumental(models.Model):
    """Catálogo de requisitos del Anexo 2 para inscripción, novedades y visitas."""

    TIPO_TRAMITE_CHOICES = [
        ('INSCRIPCION', 'Inscripción'),
        ('NOVEDAD', 'Novedad'),
        ('VISITA_PREVIA', 'Visita Previa'),
        ('VISITA_CERTIFICACION', 'Visita de Certificación'),
        ('VISITA_REACTIVACION', 'Visita de Reactivación'),
    ]

    codigo = models.CharField(max_length=30, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    tipo_tramite = models.CharField(max_length=30, choices=TIPO_TRAMITE_CHOICES, verbose_name='Tipo de Trámite')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_requisitodocumental'
        verbose_name = 'Requisito Documental'
        verbose_name_plural = 'Requisitos Documentales'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['tipo_tramite', 'activo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class ChecklistVerificacion(models.Model):
    """Checklist de verificación documental para un trámite REPS."""

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETO', 'Completo'),
        ('CERRADO', 'Cerrado'),
    ]

    codigo_checklist = models.CharField(max_length=60, unique=True, verbose_name='Código Checklist')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR', verbose_name='Estado')
    novedad = models.ForeignKey(
        NovedadREPS,
        on_delete=models.CASCADE,
        related_name='checklists',
        verbose_name='Novedad REPS'
    )
    servicio_sede = models.ForeignKey(
        ServicioSede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklists_verificacion',
        verbose_name='Servicio de Sede'
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklists_verificacion',
        verbose_name='Responsable'
    )
    fecha_cierre = models.DateField(blank=True, null=True, verbose_name='Fecha de Cierre')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_checklistverificacion'
        verbose_name = 'Checklist de Verificación'
        verbose_name_plural = 'Checklists de Verificación'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['novedad', 'estado']),
        ]

    def __str__(self):
        return f"{self.codigo_checklist} - {self.estado}"

    SUBTIPO_NOVEDAD_PREFIX_RULES = {
        'CAMBIO_CONTACTO': ['NOV-BAS', 'NOV-CON'],
        'CIERRE_MODALIDAD': ['NOV-BAS', 'NOV-CM'],
        'CAMBIO_HORARIO': ['NOV-BAS', 'NOV-HOR'],
        'CAMBIO_COMPLEJIDAD': ['NOV-BAS', 'NOV-CC'],
        'TRASLADO_SERVICIO': ['NOV-BAS', 'NOV-TS'],
        'OTRA': ['NOV-BAS'],
    }

    def get_tipos_tramite_objetivo(self):
        """Determina uno o varios tipos de trámite aplicables según la novedad REPS."""
        if self.novedad.tipo_novedad == 'PRESTADOR':
            return ['INSCRIPCION']

        tipos = ['NOVEDAD']

        if self.novedad.subtipo_novedad == 'REACTIVACION':
            tipos.append('VISITA_REACTIVACION')
        elif self.novedad.subtipo_novedad == 'APERTURA_MODALIDAD':
            tipos.append('VISITA_CERTIFICACION')

        if self.novedad.requiere_visita_previa:
            tipos.append('VISITA_PREVIA')

        return list(dict.fromkeys(tipos))

    def _aplicar_reglas_subtipo_novedad(self, requisitos):
        """Restringe requisitos tipo NOVEDAD por subtipo sin afectar requisitos de visitas."""
        prefijos = self.SUBTIPO_NOVEDAD_PREFIX_RULES.get(self.novedad.subtipo_novedad)
        if not prefijos:
            return requisitos

        q_prefijos = models.Q()
        for prefijo in prefijos:
            q_prefijos |= models.Q(codigo__startswith=prefijo)

        return requisitos.filter(
            models.Q(tipo_tramite__in=['VISITA_PREVIA', 'VISITA_CERTIFICACION', 'VISITA_REACTIVACION'])
            | (models.Q(tipo_tramite='NOVEDAD') & q_prefijos)
            | models.Q(tipo_tramite='INSCRIPCION')
        )

    def get_requisitos_aplicables(self):
        """Obtiene requisitos activos para los trámites objetivo del checklist."""
        tipos_tramite = self.get_tipos_tramite_objetivo()
        requisitos = RequisitoDocumental.objects.filter(
            tipo_tramite__in=tipos_tramite,
            activo=True,
        )

        requisitos = self._aplicar_reglas_subtipo_novedad(requisitos)
        return requisitos.order_by('codigo')

    def crear_items_desde_requisitos(self):
        """Crea ítems faltantes en el checklist a partir del catálogo normativo."""
        requisitos = self.get_requisitos_aplicables()
        if not requisitos.exists():
            return 0

        existentes = set(
            self.items.values_list('requisito_id', flat=True)
        )

        nuevos_items = [
            ChecklistItem(
                checklist=self,
                requisito=requisito,
                obligatorio=requisito.obligatorio,
            )
            for requisito in requisitos
            if requisito.id not in existentes
        ]

        if not nuevos_items:
            return 0

        with transaction.atomic():
            ChecklistItem.objects.bulk_create(nuevos_items, ignore_conflicts=True)

        return len(nuevos_items)

    def save(self, *args, **kwargs):
        es_nuevo = self._state.adding
        super().save(*args, **kwargs)
        if es_nuevo:
            self.crear_items_desde_requisitos()


class ChecklistItem(models.Model):
    """Ítem del checklist asociado a un requisito documental del Anexo 2."""

    checklist = models.ForeignKey(
        ChecklistVerificacion,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Checklist'
    )
    requisito = models.ForeignKey(
        RequisitoDocumental,
        on_delete=models.PROTECT,
        related_name='items_checklist',
        verbose_name='Requisito'
    )
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')
    cumple = models.BooleanField(null=True, blank=True, verbose_name='Cumple')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    verificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items_checklist_verificados',
        verbose_name='Verificado por'
    )
    fecha_verificacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Verificación')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'habilitacion_checklistitem'
        verbose_name = 'Ítem de Checklist'
        verbose_name_plural = 'Ítems de Checklist'
        unique_together = ('checklist', 'requisito')
        indexes = [
            models.Index(fields=['checklist', 'cumple']),
        ]

    def __str__(self):
        return f"{self.checklist.codigo_checklist} - {self.requisito.codigo}"


class EvidenciaChecklist(models.Model):
    """Evidencia documental cargada para cada ítem del checklist."""

    TIPO_CHOICES = [
        ('DOCUMENTO', 'Documento'),
        ('CERTIFICADO', 'Certificado'),
        ('ACTA', 'Acta'),
        ('OTRO', 'Otro'),
    ]

    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE,
        related_name='evidencias',
        verbose_name='Ítem de Checklist'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='DOCUMENTO', verbose_name='Tipo')
    nombre = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nombre')
    archivo = models.FileField(
        upload_to=checklist_upload_path,
        validators=[validate_checklist_extension],
        verbose_name='Archivo'
    )
    hash_integridad = models.CharField(max_length=128, blank=True, null=True, verbose_name='Hash de Integridad')
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidencias_checklist_subidas',
        verbose_name='Subido por'
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')

    class Meta:
        db_table = 'habilitacion_evidenciachecklist'
        verbose_name = 'Evidencia de Checklist'
        verbose_name_plural = 'Evidencias de Checklist'
        ordering = ['-fecha_subida']

    def __str__(self):
        return self.nombre or os.path.basename(self.archivo.name)

    def save(self, *args, **kwargs):
        if self.archivo and not self.nombre:
            self.nombre = os.path.basename(self.archivo.name)
        super().save(*args, **kwargs)
