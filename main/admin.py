from django.contrib import admin
from .models import Funcionario, ContenidoInformativo, Evento, FelicitacionCumpleanios, Reconocimiento

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'cargo', 'sede', 'correo')

@admin.register(ContenidoInformativo)
class ContenidoInformativoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'urgente', 'fecha')
    list_filter = ('tipo', 'urgente')

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'es_virtual', 'importante')

@admin.register(FelicitacionCumpleanios)
class FelicitacionCumpleaniosAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'created_at')

@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'funcionario', 'fecha', 'tipo', 'publicar')
    list_filter = ('tipo', 'publicar', 'fecha')
    search_fields = ('titulo', 'descripcion', 'funcionario__nombres', 'funcionario__apellidos')
