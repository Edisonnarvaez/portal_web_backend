from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo_documento', 'nombre_documento', 'version', 'tipo_documento', 'estado', 'activo', 'fecha_actualizacion')
    list_filter = ('tipo_documento', 'estado', 'activo')
    search_fields = ('codigo_documento', 'nombre_documento')
