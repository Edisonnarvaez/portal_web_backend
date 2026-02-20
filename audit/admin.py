"""
audit/admin.py

Administración para el módulo de Auditorías con ciclo de vida completo.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Auditoria, EntidadAuditoria, TipoAuditoria,
    MiembroEquipoAuditor, HallazgoAuditoria,
    ActaReunion, ProgramaAuditoria,
)


# ─── Inlines ───

class MiembroEquipoInline(admin.TabularInline):
    model = MiembroEquipoAuditor
    extra = 0
    autocomplete_fields = ['usuario']


class HallazgoAuditoriaInline(admin.TabularInline):
    model = HallazgoAuditoria
    extra = 0
    fields = ['numero', 'tipo', 'descripcion', 'estado', 'responsable_accion', 'fecha_limite_accion']
    show_change_link = True


class ActaReunionInline(admin.TabularInline):
    model = ActaReunion
    extra = 0
    fields = ['tipo_acta', 'fecha', 'lugar', 'asistentes']
    show_change_link = True


# ─── Auditoría ───

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = [
        'auditoria_id', 'auditoria_nombre', 'clasificacion_badge',
        'tipo_nombre', 'fase_badge', 'fecha_programada',
        'auditor_lider', 'total_hallazgos_col',
    ]
    list_filter = ['fase', 'clasificacion', 'auditoria_tipo', 'auditoria_estado']
    search_fields = ['auditoria_nombre', 'auditoria_detalle', 'norma_referencia']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_creacion'
    list_per_page = 25
    inlines = [MiembroEquipoInline, HallazgoAuditoriaInline, ActaReunionInline]

    fieldsets = (
        ('Identificación', {
            'fields': ('auditoria_nombre', 'auditoria_detalle', 'norma_referencia')
        }),
        ('Clasificación', {
            'fields': ('clasificacion', 'auditoria_tipo', 'auditoria_entidad')
        }),
        ('Alcance', {
            'fields': ('auditoria_proceso', 'sede')
        }),
        ('Ciclo de Vida', {
            'fields': (
                'fase', 'auditoria_estado',
                'fecha_programada', 'auditoria_fecha_notificacion',
                'fecha_inicio_ejecucion', 'auditoria_fecha_auditoria',
                'fecha_informe', 'fecha_cierre',
            )
        }),
        ('Equipo', {
            'fields': ('auditor_lider', 'auditoria_responsable')
        }),
        ('Resultados', {
            'fields': ('conclusion', 'recomendaciones'),
            'classes': ('collapse',),
        }),
        ('Relaciones', {
            'fields': ('auditoria_relacionada',),
            'classes': ('collapse',),
        }),
        ('Auditoría de datos', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def tipo_nombre(self, obj):
        return obj.auditoria_tipo.nombre if obj.auditoria_tipo else '-'
    tipo_nombre.short_description = 'Tipo'

    def clasificacion_badge(self, obj):
        colors = {'INTERNA': '#2196F3', 'EXTERNA': '#FF9800'}
        color = colors.get(obj.clasificacion, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_clasificacion_display()
        )
    clasificacion_badge.short_description = 'Clasif.'

    def fase_badge(self, obj):
        colors = {
            'PROGRAMADA': '#9E9E9E',
            'NOTIFICADA': '#FF9800',
            'EN_EJECUCION': '#2196F3',
            'INFORME': '#673AB7',
            'SEGUIMIENTO': '#FFC107',
            'CERRADA': '#4CAF50',
            'CANCELADA': '#F44336',
        }
        color = colors.get(obj.fase, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_fase_display()
        )
    fase_badge.short_description = 'Fase'

    def total_hallazgos_col(self, obj):
        return obj.total_hallazgos
    total_hallazgos_col.short_description = 'Hallazgos'


# ─── Catálogos ───

@admin.register(EntidadAuditoria)
class EntidadAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['entidad_id', 'nombre', 'tipo_entidad', 'contacto', 'activo']
    list_filter = ['tipo_entidad', 'activo']
    search_fields = ['nombre', 'contacto', 'email']


@admin.register(TipoAuditoria)
class TipoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['tipo_id', 'nombre', 'requiere_entidad_externa', 'activo']
    list_filter = ['requiere_entidad_externa', 'activo']
    search_fields = ['nombre', 'descripcion']


# ─── Hallazgos ───

@admin.register(HallazgoAuditoria)
class HallazgoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'auditoria', 'tipo_badge', 'estado_badge', 'responsable_accion', 'fecha_limite_accion']
    list_filter = ['tipo', 'estado', 'auditoria']
    search_fields = ['numero', 'descripcion', 'criterio_norma']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    def tipo_badge(self, obj):
        colors = {
            'NC_MAYOR': '#F44336', 'NC_MENOR': '#FF9800',
            'OBSERVACION': '#FFC107', 'OPORTUNIDAD': '#2196F3',
            'FORTALEZA': '#4CAF50',
        }
        color = colors.get(obj.tipo, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'

    def estado_badge(self, obj):
        colors = {
            'IDENTIFICADO': '#F44336', 'PLAN_ACCION': '#FF9800',
            'EN_SEGUIMIENTO': '#2196F3', 'VERIFICADO': '#8BC34A',
            'CERRADO': '#4CAF50',
        }
        color = colors.get(obj.estado, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'


# ─── Actas ───

@admin.register(ActaReunion)
class ActaReunionAdmin(admin.ModelAdmin):
    list_display = ['auditoria', 'tipo_acta', 'fecha', 'lugar']
    list_filter = ['tipo_acta']
    search_fields = ['auditoria__auditoria_nombre', 'temas_tratados']


# ─── Programas ───

@admin.register(ProgramaAuditoria)
class ProgramaAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'periodo', 'estado', 'responsable', 'total_auditorias_col', 'avance_col']
    list_filter = ['estado', 'periodo']
    search_fields = ['nombre', 'periodo']
    filter_horizontal = ['auditorias']

    def total_auditorias_col(self, obj):
        return obj.total_auditorias
    total_auditorias_col.short_description = 'Total Auditorías'

    def avance_col(self, obj):
        pct = obj.avance_porcentaje
        color = '#4CAF50' if pct >= 80 else ('#FFC107' if pct >= 40 else '#F44336')
        return format_html(
            '<div style="width:80px; background:#e0e0e0; border-radius:4px;">'
            '<div style="width:{}%; background:{}; height:16px; border-radius:4px; '
            'text-align:center; color:white; font-size:11px; line-height:16px;">'
            '{}%</div></div>',
            pct, color, pct
        )
    avance_col.short_description = 'Avance'

