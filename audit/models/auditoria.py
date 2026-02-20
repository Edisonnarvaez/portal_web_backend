"""
audit/models/auditoria.py

Modelo principal de Auditoría con ciclo de vida completo.
Fases: PROGRAMADA → NOTIFICADA → EN_EJECUCION → INFORME → SEGUIMIENTO → CERRADA
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models.process import Process
from .tipo_auditoria import TipoAuditoria
from .entidad_auditoria import EntidadAuditoria


class Auditoria(models.Model):
    """
    Modelo principal de auditoría con ciclo de vida completo.
    Mantiene compatibilidad con campos existentes (auditoria_id como PK).
    """

    class Fase(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        NOTIFICADA = 'NOTIFICADA', 'Notificada'
        EN_EJECUCION = 'EN_EJECUCION', 'En Ejecución'
        INFORME = 'INFORME', 'Informe'
        SEGUIMIENTO = 'SEGUIMIENTO', 'Seguimiento'
        CERRADA = 'CERRADA', 'Cerrada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    class Clasificacion(models.TextChoices):
        INTERNA = 'INTERNA', 'Interna'
        EXTERNA = 'EXTERNA', 'Externa'

    # ─── Identificación (campos originales preservados) ───
    auditoria_id = models.AutoField(primary_key=True, verbose_name="ID")
    auditoria_nombre = models.CharField(
        max_length=200, default="", verbose_name="Nombre de la auditoría"
    )
    auditoria_detalle = models.TextField(
        blank=True, default='', verbose_name="Objetivo / Alcance"
    )

    # ─── Clasificación ───
    clasificacion = models.CharField(
        max_length=10,
        choices=Clasificacion.choices,
        default=Clasificacion.INTERNA,
        verbose_name="Clasificación"
    )
    auditoria_tipo = models.ForeignKey(
        TipoAuditoria,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias',
        verbose_name="Tipo de auditoría"
    )
    auditoria_entidad = models.ForeignKey(
        EntidadAuditoria,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias',
        verbose_name="Entidad auditora"
    )

    # ─── Alcance ───
    auditoria_proceso = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias',
        verbose_name="Proceso auditado"
    )
    sede = models.ForeignKey(
        'companies.Headquarters',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias',
        verbose_name="Sede auditada"
    )
    norma_referencia = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name="Norma de referencia",
        help_text="Ej: ISO 9001:2015, Resolución 3100/2019"
    )

    # ─── Ciclo de vida ───
    fase = models.CharField(
        max_length=15,
        choices=Fase.choices,
        default=Fase.PROGRAMADA,
        verbose_name="Fase actual"
    )
    auditoria_estado = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Si está desactivada no aparece en listados activos"
    )

    # ─── Fechas del ciclo ───
    fecha_programada = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha programada"
    )
    auditoria_fecha_notificacion = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha de notificación"
    )
    fecha_inicio_ejecucion = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha inicio ejecución"
    )
    auditoria_fecha_auditoria = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha fin ejecución"
    )
    fecha_informe = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha de informe"
    )
    fecha_cierre = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha de cierre"
    )

    # ─── Equipo auditor ───
    auditor_lider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias_lider',
        verbose_name="Auditor líder"
    )
    auditoria_responsable = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name="Responsable del proceso auditado"
    )

    # ─── Resultados ───
    conclusion = models.TextField(
        blank=True, default='',
        verbose_name="Conclusiones generales"
    )
    recomendaciones = models.TextField(
        blank=True, default='',
        verbose_name="Recomendaciones"
    )

    # ─── Relación ───
    auditoria_relacionada = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias_hijas',
        verbose_name="Auditoría de seguimiento a"
    )

    # ─── Auditoría de datos ───
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='auditorias_creadas',
        verbose_name="Creado por"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Auditoría"
        verbose_name_plural = "Auditorías"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['fase']),
            models.Index(fields=['clasificacion']),
            models.Index(fields=['auditoria_tipo']),
            models.Index(fields=['fecha_programada']),
        ]

    def __str__(self):
        return f"AUD-{self.auditoria_id:04d} {self.auditoria_nombre}"

    # ─── Propiedades calculadas ───

    @property
    def esta_activa(self):
        return self.fase not in [self.Fase.CERRADA, self.Fase.CANCELADA]

    @property
    def dias_para_ejecucion(self):
        """Días restantes hasta la fecha programada."""
        if not self.fecha_programada:
            return None
        delta = (self.fecha_programada - timezone.now().date()).days
        return delta

    @property
    def duracion_dias(self):
        """Duración de la ejecución en días."""
        if self.fecha_inicio_ejecucion and self.auditoria_fecha_auditoria:
            return (self.auditoria_fecha_auditoria - self.fecha_inicio_ejecucion).days + 1
        return None

    @property
    def total_hallazgos(self):
        return self.hallazgos_auditoria.count()

    @property
    def total_no_conformidades(self):
        return self.hallazgos_auditoria.filter(tipo__in=['NC_MAYOR', 'NC_MENOR']).count()

    # ─── Transiciones de fase ───

    def puede_avanzar_a(self, nueva_fase):
        """Validar transiciones permitidas."""
        transiciones = {
            self.Fase.PROGRAMADA: [self.Fase.NOTIFICADA, self.Fase.CANCELADA],
            self.Fase.NOTIFICADA: [self.Fase.EN_EJECUCION, self.Fase.CANCELADA],
            self.Fase.EN_EJECUCION: [self.Fase.INFORME],
            self.Fase.INFORME: [self.Fase.SEGUIMIENTO, self.Fase.CERRADA],
            self.Fase.SEGUIMIENTO: [self.Fase.CERRADA],
            self.Fase.CERRADA: [],
            self.Fase.CANCELADA: [],
        }
        return nueva_fase in transiciones.get(self.fase, [])

    def avanzar_fase(self, nueva_fase):
        """Avanzar a la siguiente fase con validación."""
        if not self.puede_avanzar_a(nueva_fase):
            raise ValueError(
                f"No se puede avanzar de {self.fase} a {nueva_fase}. "
                f"Transiciones permitidas: {self._transiciones_permitidas()}"
            )
        self.fase = nueva_fase
        # Auto-rellenar fechas
        hoy = timezone.now().date()
        if nueva_fase == self.Fase.NOTIFICADA and not self.auditoria_fecha_notificacion:
            self.auditoria_fecha_notificacion = hoy
        elif nueva_fase == self.Fase.EN_EJECUCION and not self.fecha_inicio_ejecucion:
            self.fecha_inicio_ejecucion = hoy
        elif nueva_fase == self.Fase.INFORME and not self.fecha_informe:
            self.fecha_informe = hoy
            if not self.auditoria_fecha_auditoria:
                self.auditoria_fecha_auditoria = hoy
        elif nueva_fase == self.Fase.CERRADA and not self.fecha_cierre:
            self.fecha_cierre = hoy
        self.save()

    def _transiciones_permitidas(self):
        transiciones = {
            self.Fase.PROGRAMADA: ['NOTIFICADA', 'CANCELADA'],
            self.Fase.NOTIFICADA: ['EN_EJECUCION', 'CANCELADA'],
            self.Fase.EN_EJECUCION: ['INFORME'],
            self.Fase.INFORME: ['SEGUIMIENTO', 'CERRADA'],
            self.Fase.SEGUIMIENTO: ['CERRADA'],
            self.Fase.CERRADA: [],
            self.Fase.CANCELADA: [],
        }
        return transiciones.get(self.fase, [])


class MiembroEquipoAuditor(models.Model):
    """Miembros del equipo auditor de una auditoría."""

    class Rol(models.TextChoices):
        AUDITOR_LIDER = 'LIDER', 'Auditor Líder'
        AUDITOR = 'AUDITOR', 'Auditor'
        OBSERVADOR = 'OBSERVADOR', 'Observador'
        EXPERTO_TECNICO = 'EXPERTO', 'Experto Técnico'

    auditoria = models.ForeignKey(
        Auditoria,
        on_delete=models.CASCADE,
        related_name='equipo_auditor'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participaciones_auditoria'
    )
    rol = models.CharField(
        max_length=15,
        choices=Rol.choices,
        default=Rol.AUDITOR
    )
    area_responsable = models.CharField(
        max_length=200, blank=True, default='',
        help_text="Área o proceso que tiene asignado auditar"
    )

    class Meta:
        db_table = 'audit_miembro_equipo'
        verbose_name = 'Miembro del equipo auditor'
        verbose_name_plural = 'Equipo auditor'
        unique_together = ('auditoria', 'usuario')

    def __str__(self):
        return f"{self.usuario} - {self.get_rol_display()} en {self.auditoria}"


class HallazgoAuditoria(models.Model):
    """
    Hallazgo identificado durante una auditoría.
    Se integra con mejoras/Hallazgo a través de FK opcional.
    """

    class TipoHallazgo(models.TextChoices):
        NO_CONFORMIDAD_MAYOR = 'NC_MAYOR', 'No Conformidad Mayor'
        NO_CONFORMIDAD_MENOR = 'NC_MENOR', 'No Conformidad Menor'
        OBSERVACION = 'OBSERVACION', 'Observación'
        OPORTUNIDAD_MEJORA = 'OPORTUNIDAD', 'Oportunidad de Mejora'
        FORTALEZA = 'FORTALEZA', 'Fortaleza'

    class Estado(models.TextChoices):
        IDENTIFICADO = 'IDENTIFICADO', 'Identificado'
        PLAN_ACCION = 'PLAN_ACCION', 'Con Plan de Acción'
        EN_SEGUIMIENTO = 'EN_SEGUIMIENTO', 'En Seguimiento'
        VERIFICADO = 'VERIFICADO', 'Verificado'
        CERRADO = 'CERRADO', 'Cerrado'

    auditoria = models.ForeignKey(
        Auditoria,
        on_delete=models.CASCADE,
        related_name='hallazgos_auditoria'
    )
    numero = models.CharField(
        max_length=30,
        verbose_name="Número de hallazgo"
    )
    tipo = models.CharField(
        max_length=15,
        choices=TipoHallazgo.choices,
        verbose_name="Tipo de hallazgo"
    )
    criterio_norma = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name="Criterio / Numeral de norma",
        help_text="Requisito de la norma incumplido"
    )
    descripcion = models.TextField(
        verbose_name="Descripción del hallazgo"
    )
    evidencia_objetiva = models.TextField(
        blank=True, default='',
        verbose_name="Evidencia objetiva"
    )
    proceso_afectado = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='hallazgos_auditoria',
        verbose_name="Proceso afectado"
    )
    responsable_accion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='hallazgos_asignados',
        verbose_name="Responsable de acción"
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.IDENTIFICADO
    )
    fecha_limite_accion = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha límite para acción"
    )
    fecha_verificacion = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha de verificación"
    )

    # ─── Integración con mejoras ───
    hallazgo_mejora = models.ForeignKey(
        'mejoras.Hallazgo',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='hallazgos_auditoria_origen',
        help_text="Hallazgo vinculado en el módulo de mejoras"
    )
    plan_mejora = models.ForeignKey(
        'mejoras.PlanMejora',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='hallazgos_auditoria_origen',
        help_text="Plan de mejora asociado"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'audit_hallazgo_auditoria'
        verbose_name = 'Hallazgo de auditoría'
        verbose_name_plural = 'Hallazgos de auditoría'
        ordering = ['numero']
        unique_together = ('auditoria', 'numero')

    def __str__(self):
        return f"{self.numero} - {self.get_tipo_display()}"

    @property
    def esta_vencido(self):
        if not self.fecha_limite_accion:
            return False
        return (
            self.fecha_limite_accion < timezone.now().date()
            and self.estado not in [self.Estado.VERIFICADO, self.Estado.CERRADO]
        )


class ActaReunion(models.Model):
    """
    Actas de las reuniones de apertura, cierre y seguimiento de la auditoría.
    """

    class TipoActa(models.TextChoices):
        APERTURA = 'APERTURA', 'Acta de Apertura'
        CIERRE = 'CIERRE', 'Acta de Cierre'
        SEGUIMIENTO = 'SEGUIMIENTO', 'Acta de Seguimiento'

    auditoria = models.ForeignKey(
        Auditoria,
        on_delete=models.CASCADE,
        related_name='actas'
    )
    tipo_acta = models.CharField(
        max_length=15,
        choices=TipoActa.choices,
    )
    fecha = models.DateField()
    lugar = models.CharField(max_length=200, blank=True, default='')
    asistentes = models.TextField(
        blank=True, default='',
        help_text="Lista de asistentes (uno por línea)"
    )
    temas_tratados = models.TextField(
        blank=True, default='',
        verbose_name="Temas tratados / Orden del día"
    )
    compromisos = models.TextField(
        blank=True, default='',
        verbose_name="Compromisos y acuerdos"
    )
    observaciones = models.TextField(blank=True, default='')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_acta_reunion'
        verbose_name = 'Acta de reunión'
        verbose_name_plural = 'Actas de reunión'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_acta_display()} - {self.auditoria}"


class ProgramaAuditoria(models.Model):
    """
    Programa anual de auditorías.
    Agrupa las auditorías planificadas para un período.
    """

    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        APROBADO = 'APROBADO', 'Aprobado'
        EN_EJECUCION = 'EN_EJECUCION', 'En Ejecución'
        COMPLETADO = 'COMPLETADO', 'Completado'

    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del programa"
    )
    periodo = models.CharField(
        max_length=20,
        verbose_name="Período",
        help_text="Ej: 2026, 2026-S1"
    )
    descripcion = models.TextField(blank=True, default='')
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.BORRADOR
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='programas_auditoria'
    )
    fecha_aprobacion = models.DateField(null=True, blank=True)
    auditorias = models.ManyToManyField(
        Auditoria,
        blank=True,
        related_name='programas',
        verbose_name="Auditorías del programa"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'audit_programa'
        verbose_name = 'Programa de auditoría'
        verbose_name_plural = 'Programas de auditoría'
        ordering = ['-periodo']

    def __str__(self):
        return f"{self.nombre} ({self.periodo})"

    @property
    def total_auditorias(self):
        return self.auditorias.count()

    @property
    def avance_porcentaje(self):
        total = self.auditorias.count()
        if total == 0:
            return 0
        cerradas = self.auditorias.filter(fase='CERRADA').count()
        return round((cerradas / total) * 100, 1)
