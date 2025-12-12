"""
habilitacion/models.py

Modelos transaccionales para la habilitación de servicios de salud.
Integración con los modelos core (Company, Headquarters) mediante OneToOne.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from companies.models import Company, Headquarters
from normativity.models import Criterio
from processes.models import Documento

User = get_user_model()


class DatosPrestador(models.Model):
    """
    Datos específicos de habilitación vinculados a una Company.
    OneToOne: Una empresa tiene un único perfil de prestador habilitado.
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
    
    company = models.OneToOneField(
        Company,
        on_delete=models.PROTECT,
        related_name='datos_habilitacion',
        verbose_name="Empresa"
    )
    
    # Identificación REPS
    codigo_reps = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código REPS",
        help_text="Código de registro en REPS de la Superintendencia de Salud"
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
        return f"{self.codigo_reps} - {self.company.name}"
    
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
    
    sede = models.ForeignKey(
        Headquarters,
        on_delete=models.PROTECT,
        related_name='servicios_salud',
        verbose_name="Sede"
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
        verbose_name = "Servicio de Sede"
        verbose_name_plural = "Servicios de Sedes"
        unique_together = ('sede', 'codigo_servicio')
        indexes = [
            models.Index(fields=['sede', 'estado_habilitacion']),
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
    
    def porcentaje_cumplimiento(self):
        """Calcular porcentaje general de cumplimiento."""
        total = self.cumplimientos.count()
        if total == 0:
            return 0
        cumplidos = self.cumplimientos.filter(cumple=True).count()
        return (cumplidos / total) * 100
    
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
