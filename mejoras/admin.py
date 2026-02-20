"""
mejoras/admin.py

Administración para Planes de Mejora y Hallazgos.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import PlanMejora, Hallazgo


@admin.register(PlanMejora)
class PlanMejoraAdmin(admin.ModelAdmin):
    list_display = [
        'numero_plan', 'descripcion_corta', 'origen_badge',
        'estado_badge', 'porcentaje_barra',
        'fecha_vencimiento', 'responsable',
    ]
    list_filter = ['origen_tipo', 'estado', 'fecha_vencimiento']
    search_fields = ['numero_plan', 'descripcion', 'acciones_implementar']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_editable = ['fecha_vencimiento']
    date_hierarchy = 'fecha_creacion'
    list_per_page = 25

    fieldsets = (
        ('Identificación', {
            'fields': ('numero_plan', 'descripcion')
        }),
        ('Origen', {
            'fields': ('origen_tipo', 'cumplimiento', 'autoevaluacion',
                        'criterio', 'auditoria', 'resultado_indicador')
        }),
        ('Plan de Acción', {
            'fields': (
                'estado_cumplimiento_actual', 'objetivo_mejorado',
                'acciones_implementar', 'responsable',
            )
        }),
        ('Seguimiento', {
            'fields': (
                'fecha_inicio', 'fecha_vencimiento', 'fecha_implementacion',
                'porcentaje_avance', 'estado',
            )
        }),
        ('Evidencia y Notas', {
            'fields': ('evidencia', 'observaciones'),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + '...' if len(obj.descripcion) > 60 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'

    def origen_badge(self, obj):
        colors = {
            'HABILITACION': '#2196F3',
            'AUDITORIA': '#FF9800',
            'INDICADOR': '#9C27B0',
        }
        color = colors.get(obj.origen_tipo, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_origen_tipo_display()
        )
    origen_badge.short_description = 'Origen'

    def estado_badge(self, obj):
        colors = {
            'PENDIENTE': '#FFC107',
            'EN_CURSO': '#2196F3',
            'COMPLETADO': '#4CAF50',
            'VENCIDO': '#F44336',
        }
        color = colors.get(obj.estado, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

    def porcentaje_barra(self, obj):
        color = '#4CAF50' if obj.porcentaje_avance >= 80 else (
            '#FFC107' if obj.porcentaje_avance >= 40 else '#F44336'
        )
        return format_html(
            '<div style="width:100px; background:#e0e0e0; border-radius:4px;">'
            '<div style="width:{}px; background:{}; height:16px; border-radius:4px; '
            'text-align:center; color:white; font-size:11px; line-height:16px;">'
            '{}%</div></div>',
            obj.porcentaje_avance, color, obj.porcentaje_avance
        )
    porcentaje_barra.short_description = 'Avance'


@admin.register(Hallazgo)
class HallazgoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_hallazgo', 'tipo_badge', 'severidad_badge',
        'estado_badge', 'origen_badge',
        'fecha_identificacion', 'plan_mejora',
    ]
    list_filter = ['origen_tipo', 'tipo', 'severidad', 'estado']
    search_fields = ['numero_hallazgo', 'descripcion', 'area_responsable']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_identificacion'
    list_per_page = 25

    fieldsets = (
        ('Identificación', {
            'fields': ('numero_hallazgo', 'descripcion', 'tipo', 'severidad')
        }),
        ('Origen', {
            'fields': ('origen_tipo', 'autoevaluacion', 'datos_prestador',
                        'criterio', 'auditoria', 'resultado_indicador')
        }),
        ('Seguimiento', {
            'fields': ('area_responsable', 'estado', 'plan_mejora',
                        'fecha_identificacion', 'fecha_cierre')
        }),
        ('Notas', {
            'fields': ('observaciones',),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def tipo_badge(self, obj):
        colors = {
            'FORTALEZA': '#4CAF50',
            'OPORTUNIDAD_MEJORA': '#2196F3',
            'NO_CONFORMIDAD': '#F44336',
            'HALLAZGO': '#FF9800',
        }
        color = colors.get(obj.tipo, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'

    def severidad_badge(self, obj):
        colors = {
            'BAJA': '#8BC34A',
            'MEDIA': '#FFC107',
            'ALTA': '#FF9800',
            'CRÍTICA': '#F44336',
        }
        color = colors.get(obj.severidad, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_severidad_display()
        )
    severidad_badge.short_description = 'Severidad'

    def estado_badge(self, obj):
        colors = {
            'ABIERTO': '#F44336',
            'EN_SEGUIMIENTO': '#2196F3',
            'CERRADO': '#4CAF50',
        }
        color = colors.get(obj.estado, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

    def origen_badge(self, obj):
        colors = {
            'HABILITACION': '#2196F3',
            'AUDITORIA': '#FF9800',
            'INDICADOR': '#9C27B0',
        }
        color = colors.get(obj.origen_tipo, '#607D8B')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_origen_tipo_display()
        )
    origen_badge.short_description = 'Origen'
