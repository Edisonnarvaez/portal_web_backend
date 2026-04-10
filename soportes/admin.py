from django.contrib import admin
from django.utils import timezone
from datetime import timedelta

from .models import (
    CategoriaSoporte,
    SoporteDocumental,
    SoporteRequerido,
    TipoDocumentoSoporte,
)


@admin.register(CategoriaSoporte)
class CategoriaSoporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)
    ordering = ('nombre',)


@admin.register(TipoDocumentoSoporte)
class TipoDocumentoSoporteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'categoria',
        'nivel_aplica',
        'es_obligatorio',
        'requiere_vencimiento',
        'activo',
    )
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('categoria', 'nivel_aplica', 'es_obligatorio', 'requiere_vencimiento', 'activo')
    fieldsets = (
        ('Información Básica', {
            'fields': ('categoria', 'nombre', 'nivel_aplica', 'activo')
        }),
        ('Configuración', {
            'fields': ('es_obligatorio', 'requiere_vencimiento')
        }),
    )
    ordering = ('nombre',)


@admin.register(SoporteDocumental)
class SoporteDocumentalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'prestador_link',
        'nivel',
        'tipo_documento',
        'empresa',
        'sede',
        'servicio',
        'version',
        'es_vigente',
        'fecha_emision',
        'vencimiento_status',
        'fecha_carga',
    )
    search_fields = (
        'prestador__nombre_prestador',
        'tipo_documento__nombre',
        'observaciones',
    )
    list_filter = (
        'nivel',
        'es_vigente',
        'prestador',
        'tipo_documento__categoria',
        'tipo_documento',
        'fecha_vencimiento',
    )
    fieldsets = (
        ('👤 Propietario', {
            'fields': ('prestador',)
        }),
        ('📋 Clasificación', {
            'fields': ('nivel', 'tipo_documento')
        }),
        ('🏢 Contexto', {
            'fields': ('empresa', 'sede', 'servicio'),
            'classes': ('collapse',)
        }),
        ('📅 Fechas', {
            'fields': ('fecha_emision', 'fecha_vencimiento')
        }),
        ('📄 Archivo', {
            'fields': ('archivo', 'observaciones')
        }),
        ('🔍 Versionamiento (Read-only)', {
            'fields': ('version', 'es_vigente', 'fecha_carga'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('version', 'fecha_carga')
    ordering = ('-fecha_carga',)

    def prestador_link(self, obj):
        """Mostrar prestador con link"""
        if obj.prestador:
            return obj.prestador.nombre_prestador
        return '-'
    prestador_link.short_description = '👤 Prestador'

    def vencimiento_status(self, obj):
        """Mostrar estado de vencimiento con color"""
        if not obj.es_vigente:
            return "❌ No vigente"
        
        if not obj.fecha_vencimiento:
            return "∞ Sin vencimiento"
        
        hoy = timezone.now().date()
        dias_restantes = (obj.fecha_vencimiento - hoy).days
        
        if dias_restantes < 0:
            return f"🔴 Vencido hace {abs(dias_restantes)} días"
        elif dias_restantes < 30:
            return f"🟠 Vence en {dias_restantes} días"
        else:
            return f"🟢 Vence en {dias_restantes} días"
    
    vencimiento_status.short_description = "📅 Vencimiento"


@admin.register(SoporteRequerido)
class SoporteRequeridoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'prestador_link',
        'tipo_documento',
        'empresa',
        'sede',
        'servicio',
        'get_estado_display',
        'created_at',
    )
    search_fields = (
        'prestador__nombre_prestador',
        'tipo_documento__nombre',
    )
    list_filter = (
        'estado',
        'prestador',
        'tipo_documento__categoria',
        'tipo_documento',
    )
    fieldsets = (
        ('👤 Propietario', {
            'fields': ('prestador', 'estado')
        }),
        ('📋 Documento Requerido', {
            'fields': ('tipo_documento',)
        }),
        ('🏢 Contexto (uno debe estar definido)', {
            'fields': ('empresa', 'sede', 'servicio'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('prestador', 'estado')

    def prestador_link(self, obj):
        """Mostrar prestador con link"""
        if obj.prestador:
            return obj.prestador.nombre_prestador
        return '-'
    prestador_link.short_description = '👤 Prestador'

    def created_at(self, obj):
        """Mostrar fecha de creación si existe"""
        if hasattr(obj, 'fecha_creacion'):
            return obj.fecha_creacion.strftime('%Y-%m-%d %H:%M')
        return '-'
    created_at.short_description = '📅 Creado'
