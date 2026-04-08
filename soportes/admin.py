from django.contrib import admin

from .models import CategoriaSoporte, SoporteDocumental, TipoDocumentoSoporte


@admin.register(CategoriaSoporte)
class CategoriaSoporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)
    ordering = ('nombre',)


@admin.register(TipoDocumentoSoporte)
class TipoDocumentoSoporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'es_obligatorio', 'requiere_vencimiento', 'activo')
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('categoria', 'es_obligatorio', 'requiere_vencimiento', 'activo')
    ordering = ('nombre',)


@admin.register(SoporteDocumental)
class SoporteDocumentalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nivel',
        'tipo_documento',
        'empresa',
        'sede',
        'servicio',
        'version',
        'es_vigente',
        'fecha_emision',
        'fecha_vencimiento',
        'fecha_carga',
        'estado_color'
    )
    search_fields = ('tipo_documento__nombre', 'observaciones')
    list_filter = (
        'nivel',
        'es_vigente',
        'tipo_documento__categoria',
        'tipo_documento',
        'fecha_vencimiento'
    )
    ordering = ('-fecha_carga',)
    readonly_fields = ('version', 'fecha_carga')
    
    def estado_color(self, obj):
        if not obj.es_vigente:
            return "❌ No vigente"
        if obj.fecha_vencimiento and obj.fecha_vencimiento < timezone.now().date():
            return "🔴 Vencido"
        return "🟢 Vigente"

    estado_color.short_description = "Estado"
