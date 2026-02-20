"""
mejoras/models.py

Modelos transversales para Planes de Mejora y Hallazgos.
App independiente reutilizable por: habilitacion, audit, indicators.

Ciclo PHVA: Un hallazgo (de cualquier origen) genera un plan de mejora
con seguimiento de estado, porcentaje de avance y fechas de vencimiento.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


# ═══════════════════════════════════════════════════════════════════
# MANAGERS
# ═══════════════════════════════════════════════════════════════════

class PlanMejoraManager(models.Manager):
    """Manager personalizado con filtros frecuentes."""

    def vencidos(self):
        return self.filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).exclude(estado='COMPLETADO')

    def proximos_a_vencer(self, dias=30):
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        return self.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date()
        ).exclude(estado__in=['COMPLETADO', 'VENCIDO'])

    def por_origen(self, origen_tipo):
        return self.filter(origen_tipo=origen_tipo)

    def por_autoevaluacion(self, autoevaluacion_id):
        return self.filter(
            origen_tipo='HABILITACION',
            cumplimiento__autoevaluacion_id=autoevaluacion_id
        )

    def por_auditoria(self, auditoria_id):
        return self.filter(
            origen_tipo='AUDITORIA',
            auditoria_id=auditoria_id
        )

    def por_indicador(self, indicador_id):
        return self.filter(
            origen_tipo='INDICADOR',
            resultado_indicador__indicator_id=indicador_id
        )


# ═══════════════════════════════════════════════════════════════════
# PLAN DE MEJORA
# ═══════════════════════════════════════════════════════════════════

class PlanMejora(models.Model):
    """
    Plan de mejora transversal. Puede originarse desde:
    - Autoevaluación de habilitación (origen_tipo='HABILITACION')
    - Auditoría (origen_tipo='AUDITORIA')
    - Indicador por debajo de la meta (origen_tipo='INDICADOR')
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        VENCIDO = 'VENCIDO', 'Vencido'

    class OrigenTipo(models.TextChoices):
        HABILITACION = 'HABILITACION', 'Autoevaluación de Habilitación'
        AUDITORIA = 'AUDITORIA', 'Auditoría'
        INDICADOR = 'INDICADOR', 'Indicador'

    # ─── Identificación ───
    numero_plan = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador único del plan (ej: PM-2026-001)"
    )
    descripcion = models.TextField(
        help_text="Descripción general del plan de mejora"
    )

    # ─── Origen / Trazabilidad ───
    origen_tipo = models.CharField(
        max_length=20,
        choices=OrigenTipo.choices,
        help_text="Módulo que originó este plan de mejora"
    )

    # FK opcionales según el origen
    cumplimiento = models.ForeignKey(
        'habilitacion.Cumplimiento',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='planes_mejora',
        help_text="Cumplimiento de habilitación que originó este plan (origen=HABILITACION)"
    )
    autoevaluacion = models.ForeignKey(
        'habilitacion.Autoevaluacion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='planes_mejora',
        help_text="Autoevaluación asociada (origen=HABILITACION)"
    )
    criterio = models.ForeignKey(
        'normativity.Criterio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planes_mejora',
        help_text="Criterio normativo relacionado"
    )
    auditoria = models.ForeignKey(
        'audit.Auditoria',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='planes_mejora',
        help_text="Auditoría que originó este plan (origen=AUDITORIA)"
    )
    resultado_indicador = models.ForeignKey(
        'indicators.Result',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='planes_mejora',
        help_text="Resultado de indicador que originó este plan (origen=INDICADOR)"
    )

    # ─── Contexto del hallazgo ───
    estado_cumplimiento_actual = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Estado del cumplimiento/indicador al momento de crear el plan"
    )
    objetivo_mejorado = models.TextField(
        blank=True,
        default='',
        help_text="Meta u objetivo que se quiere alcanzar"
    )

    # ─── Plan de acción ───
    acciones_implementar = models.TextField(
        help_text="Acciones concretas a implementar para la mejora"
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planes_mejora_asignados',
        help_text="Usuario responsable de ejecutar el plan"
    )

    # ─── Fechas ───
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio del plan"
    )
    fecha_vencimiento = models.DateField(
        help_text="Fecha límite para completar el plan"
    )
    fecha_implementacion = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en que se completó la implementación"
    )

    # ─── Seguimiento ───
    porcentaje_avance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de avance (0-100)"
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        help_text="Estado actual del plan"
    )
    evidencia = models.TextField(
        blank=True,
        default='',
        help_text="Descripción de la evidencia o referencia a documentos"
    )
    observaciones = models.TextField(
        blank=True,
        default='',
        help_text="Observaciones adicionales"
    )

    # ─── Auditoría ───
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    objects = PlanMejoraManager()

    class Meta:
        db_table = 'mejoras_plan_mejora'
        ordering = ['-fecha_creacion']
        verbose_name = 'Plan de Mejora'
        verbose_name_plural = 'Planes de Mejora'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['origen_tipo']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['autoevaluacion']),
            models.Index(fields=['auditoria']),
            models.Index(fields=['resultado_indicador']),
        ]

    def __str__(self):
        return f"{self.numero_plan} - {self.get_origen_tipo_display()} - {self.descripcion[:50]}"

    # ─── Propiedades calculadas ───

    @property
    def esta_vencido(self) -> bool:
        """True si la fecha de vencimiento ya pasó y no está completado."""
        if self.estado == self.Estado.COMPLETADO:
            return False
        return self.fecha_vencimiento < timezone.now().date()

    @property
    def dias_restantes(self) -> int | None:
        """Días restantes para el vencimiento. Negativo si ya venció."""
        if not self.fecha_vencimiento:
            return None
        return (self.fecha_vencimiento - timezone.now().date()).days

    @property
    def proximo_a_vencer(self) -> bool:
        """True si vence en los próximos 30 días."""
        dias = self.dias_restantes
        if dias is None:
            return False
        return 0 < dias <= 30

    def marcar_vencido(self):
        """Actualiza el estado a VENCIDO si aplica."""
        if self.esta_vencido and self.estado not in [self.Estado.COMPLETADO, self.Estado.VENCIDO]:
            self.estado = self.Estado.VENCIDO
            self.save(update_fields=['estado', 'fecha_actualizacion'])

    @property
    def origen_detalle(self) -> str:
        """Retorna una descripción legible del origen del plan."""
        if self.origen_tipo == self.OrigenTipo.HABILITACION and self.cumplimiento:
            return f"Cumplimiento: {self.cumplimiento}"
        elif self.origen_tipo == self.OrigenTipo.AUDITORIA and self.auditoria:
            return f"Auditoría: {self.auditoria}"
        elif self.origen_tipo == self.OrigenTipo.INDICADOR and self.resultado_indicador:
            return f"Indicador: {self.resultado_indicador.indicator.name}"
        return self.get_origen_tipo_display()


# ═══════════════════════════════════════════════════════════════════
# HALLAZGO
# ═══════════════════════════════════════════════════════════════════

class Hallazgo(models.Model):
    """
    Hallazgo identificado durante una evaluación (de cualquier origen).
    Puede estar vinculado a un plan de mejora.
    """

    class TipoHallazgo(models.TextChoices):
        FORTALEZA = 'FORTALEZA', 'Fortaleza'
        OPORTUNIDAD_MEJORA = 'OPORTUNIDAD_MEJORA', 'Oportunidad de Mejora'
        NO_CONFORMIDAD = 'NO_CONFORMIDAD', 'No Conformidad'
        HALLAZGO = 'HALLAZGO', 'Hallazgo'

    class Severidad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRÍTICA', 'Crítica'

    class EstadoHallazgo(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        EN_SEGUIMIENTO = 'EN_SEGUIMIENTO', 'En Seguimiento'
        CERRADO = 'CERRADO', 'Cerrado'

    class OrigenTipo(models.TextChoices):
        HABILITACION = 'HABILITACION', 'Autoevaluación de Habilitación'
        AUDITORIA = 'AUDITORIA', 'Auditoría'
        INDICADOR = 'INDICADOR', 'Indicador'

    # ─── Identificación ───
    numero_hallazgo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador único del hallazgo (ej: HAL-2026-001)"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del hallazgo"
    )
    tipo = models.CharField(
        max_length=30,
        choices=TipoHallazgo.choices,
        help_text="Tipo de hallazgo"
    )
    severidad = models.CharField(
        max_length=10,
        choices=Severidad.choices,
        help_text="Nivel de severidad"
    )

    # ─── Origen / Trazabilidad ───
    origen_tipo = models.CharField(
        max_length=20,
        choices=OrigenTipo.choices,
        help_text="Módulo donde se identificó este hallazgo"
    )

    # FK opcionales según el origen
    autoevaluacion = models.ForeignKey(
        'habilitacion.Autoevaluacion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Autoevaluación donde se identificó (origen=HABILITACION)"
    )
    datos_prestador = models.ForeignKey(
        'habilitacion.DatosPrestador',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Prestador asociado (origen=HABILITACION)"
    )
    criterio = models.ForeignKey(
        'normativity.Criterio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Criterio normativo relacionado"
    )
    auditoria = models.ForeignKey(
        'audit.Auditoria',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Auditoría donde se identificó (origen=AUDITORIA)"
    )
    resultado_indicador = models.ForeignKey(
        'indicators.Result',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Resultado de indicador que generó el hallazgo (origen=INDICADOR)"
    )

    # ─── Relación con Plan de Mejora ───
    plan_mejora = models.ForeignKey(
        PlanMejora,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Plan de mejora asociado para resolver este hallazgo"
    )

    # ─── Datos adicionales ───
    area_responsable = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Área o departamento responsable"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoHallazgo.choices,
        default=EstadoHallazgo.ABIERTO,
        help_text="Estado actual del hallazgo"
    )
    fecha_identificacion = models.DateField(
        help_text="Fecha en que se identificó el hallazgo"
    )
    fecha_cierre = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en que se cerró el hallazgo"
    )
    observaciones = models.TextField(
        blank=True,
        default='',
        help_text="Observaciones adicionales"
    )

    # ─── Auditoría ───
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mejoras_hallazgo'
        ordering = ['-fecha_creacion']
        verbose_name = 'Hallazgo'
        verbose_name_plural = 'Hallazgos'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['tipo']),
            models.Index(fields=['severidad']),
            models.Index(fields=['origen_tipo']),
            models.Index(fields=['autoevaluacion']),
            models.Index(fields=['auditoria']),
        ]

    def __str__(self):
        return f"{self.numero_hallazgo} - {self.get_tipo_display()} ({self.get_severidad_display()})"

    @property
    def origen_detalle(self) -> str:
        """Retorna una descripción legible del origen del hallazgo."""
        if self.origen_tipo == self.OrigenTipo.HABILITACION and self.autoevaluacion:
            return f"Autoevaluación: {self.autoevaluacion}"
        elif self.origen_tipo == self.OrigenTipo.AUDITORIA and self.auditoria:
            return f"Auditoría: {self.auditoria}"
        elif self.origen_tipo == self.OrigenTipo.INDICADOR and self.resultado_indicador:
            return f"Indicador: {self.resultado_indicador.indicator.name}"
        return self.get_origen_tipo_display()
