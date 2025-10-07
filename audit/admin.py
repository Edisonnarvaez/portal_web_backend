from django.contrib import admin
from django import forms
from .models import Auditoria, EntidadAuditoria, TipoAuditoria, SedeAuditada



class AuditoriaForm(forms.ModelForm):
    class Meta:
        model = Auditoria
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AuditoriaForm, self).__init__(*args, **kwargs)
        
        if self.instance.pk and self.instance.auditoria_tipo:
            tipo = self.instance.auditoria_tipo
            self.fields['auditoria_relacionada'].queryset = Auditoria.objects.filter(auditoria_tipo=tipo).exclude(pk=self.instance.pk)
        elif 'auditoria_tipo' in self.data:
            try:
                tipo_id = int(self.data.get('auditoria_tipo'))
                self.fields['auditoria_relacionada'].queryset = Auditoria.objects.filter(auditoria_tipo_id=tipo_id)
            except (ValueError, TypeError):
                self.fields['auditoria_relacionada'].queryset = Auditoria.objects.none()
        else:
            self.fields['auditoria_relacionada'].queryset = Auditoria.objects.none()

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    form = AuditoriaForm
    list_display = (
        'auditoria_id', 'auditoria_nombre', 'auditoria_fecha_notificacion',
        'auditoria_responsable', 'auditoria_detalle', 'auditoria_fecha_auditoria',
        'auditoria_tipo', 'auditoria_entidad', 'auditoria_proceso',
        'auditoria_relacionada',  
        'auditoria_estado'
    )
    search_fields = (
        'auditoria_id', 'auditoria_nombre', 'auditoria_fecha_notificacion',
        'auditoria_responsable', 'auditoria_detalle', 'auditoria_fecha_auditoria',
        'auditoria_tipo__nombre', 'auditoria_entidad__nombre', 'auditoria_proceso__nombre'
    )

@admin.register(EntidadAuditoria)
class EntidadAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('entidad_id', 'nombre')
    search_fields = ('entidad_id', 'nombre')
    
@admin.register(TipoAuditoria)
class TipoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('tipo_id', 'nombre')
    search_fields = ('tipo_id', 'nombre')
    
@admin.register(SedeAuditada)
class SedeAuditadaAdmin(admin.ModelAdmin):
    list_display = ('nombre_sede', 'ciudad', 'pais', 'fecha_auditoria', 'auditor', 'observaciones')
    search_fields = ('nombre_sede', 'ciudad', 'pais', 'auditor__username', 'observaciones')
    list_filter = ('fecha_auditoria', 'ciudad', 'pais')

