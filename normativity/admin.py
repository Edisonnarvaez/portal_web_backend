"""
normativity/admin.py

Configuración del admin para los modelos maestros de normativity.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Estandar, Criterio, DocumentoNormativo


@admin.register(Estandar)
class EstandarAdmin(admin.ModelAdmin):
    """Admin para Estándares con lista de criterios."""
    
    list_display = [
        'codigo_colored',
        'nombre',
        'criterios_count',
        'estado',
        'version_resolucion',
        'fecha_actualizacion',
    ]
    list_filter = ['estado', 'codigo', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Estado', {
            'fields': ('estado', 'version_resolucion')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def codigo_colored(self, obj):
        """Mostrar código con color según el tipo."""
        colors = {
            'TH': '#FF6B6B',   # Rojo
            'INF': '#4ECDC4',  # Turquesa
            'DOT': '#45B7D1',  # Azul
            'PO': '#FFA07A',   # Coral
            'RS': '#98D8C8',   # Verde menta
            'GI': '#F7DC6F',   # Amarillo
            'SA': '#BB8FCE',   # Púrpura
        }
        color = colors.get(obj.codigo, '#999999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_codigo_display()
        )
    codigo_colored.short_description = 'Código'
    
    def criterios_count(self, obj):
        """Contar criterios activos."""
        count = obj.criterios.filter(estado=True).count()
        return format_html(
            '<span style="background-color: #D5F4E6; color: #27AE60; '
            'padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    criterios_count.short_description = 'Criterios Activos'


@admin.register(Criterio)
class CriterioAdmin(admin.ModelAdmin):
    """Admin para Criterios con filtros y búsqueda avanzada."""
    
    list_display = [
        'codigo_badge',
        'nombre',
        'estandar',
        'complejidad_colored',
        'es_mandatorio_badge',
        'aplica_todos_badge',
        'requiere_evidencia_documental',
        'estado',
    ]
    list_filter = [
        'estandar',
        'complejidad',
        'aplica_todos',
        'es_mandatorio',
        'requiere_evidencia_documental',
        'estado',
        'fecha_creacion',
    ]
    search_fields = ['codigo', 'nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('estandar', 'codigo', 'nombre')
        }),
        ('Descripción', {
            'fields': ('descripcion', 'notas_interpretacion')
        }),
        ('Propiedades', {
            'fields': (
                'complejidad',
                'aplica_todos',
                'es_mandatorio',
                'requiere_evidencia_documental'
            )
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def codigo_badge(self, obj):
        """Mostrar código como badge."""
        return format_html(
            '<span style="background-color: #E8F8F5; color: #16A085; '
            'padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            obj.codigo
        )
    codigo_badge.short_description = 'Código'
    
    def complejidad_colored(self, obj):
        """Mostrar complejidad con colores."""
        colors = {
            'BAJA': '#52BE80',    # Verde
            'MEDIA': '#F39C12',   # Naranja
            'ALTA': '#E74C3C',    # Rojo
        }
        color = colors.get(obj.complejidad, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_complejidad_display()
        )
    complejidad_colored.short_description = 'Complejidad'
    
    def es_mandatorio_badge(self, obj):
        """Mostrar si es mandatorio."""
        if obj.es_mandatorio:
            return format_html(
                '<span style="background-color: #E74C3C; color: white; '
                'padding: 4px 8px; border-radius: 3px;">Mandatorio</span>'
            )
        return format_html(
            '<span style="background-color: #95A5A6; color: white; '
            'padding: 4px 8px; border-radius: 3px;">Opcional</span>'
        )
    es_mandatorio_badge.short_description = 'Tipo'
    
    def aplica_todos_badge(self, obj):
        """Mostrar si aplica a todas las IPS."""
        if obj.aplica_todos:
            return format_html(
                '<span style="background-color: #3498DB; color: white; '
                'padding: 4px 8px; border-radius: 3px;">Aplica a Todos</span>'
            )
        return format_html(
            '<span style="background-color: #BDC3C7; color: white; '
            'padding: 4px 8px; border-radius: 3px;">Selectivo</span>'
        )
    aplica_todos_badge.short_description = 'Aplicabilidad'


@admin.register(DocumentoNormativo)
class DocumentoNormativoAdmin(admin.ModelAdmin):
    """Admin para Documentos Normativos."""
    
    list_display = [
        'titulo',
        'tipo_colored',
        'numero_referencia',
        'fecha_publicacion',
        'criterios_count',
        'tiene_url',
    ]
    list_filter = ['tipo', 'fecha_publicacion']
    search_fields = ['titulo', 'numero_referencia', 'descripcion']
    filter_horizontal = ['criterios_relacionados']
    readonly_fields = ['id']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('titulo', 'tipo', 'numero_referencia', 'fecha_publicacion')
        }),
        ('Contenido', {
            'fields': ('descripcion', 'url_documento')
        }),
        ('Relaciones', {
            'fields': ('criterios_relacionados',),
        }),
    )
    
    def tipo_colored(self, obj):
        """Mostrar tipo con colores."""
        colors = {
            'RESOLUCION': '#3498DB',
            'ACUERDO': '#2ECC71',
            'DECRETO': '#E74C3C',
            'MANUAL': '#F39C12',
            'GUIA': '#9B59B6',
            'CIRCULAR': '#1ABC9C',
            'OTRO': '#95A5A6',
        }
        color = colors.get(obj.tipo, '#34495E')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_colored.short_description = 'Tipo'
    
    def criterios_count(self, obj):
        """Contar criterios relacionados."""
        count = obj.criterios_relacionados.count()
        return format_html(
            '<span style="background-color: #E8F8F5; color: #16A085; '
            'padding: 4px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    criterios_count.short_description = 'Criterios Relacionados'
    
    def tiene_url(self, obj):
        """Mostrar si tiene URL."""
        if obj.url_documento:
            return format_html(
                '<a href="{}" target="_blank" style="color: #3498DB; text-decoration: none; '
                'font-weight: bold;">📄 Abrir</a>',
                obj.url_documento
            )
        return format_html(
            '<span style="color: #95A5A6;">Sin URL</span>'
        )
    tiene_url.short_description = 'Documento'
