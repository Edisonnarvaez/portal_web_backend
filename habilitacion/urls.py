"""
habilitacion/urls.py

Rutas API para habilitación de servicios de salud.
Utiliza DefaultRouter de DRF para registro automático de ViewSets.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DatosPrestadorViewSet,
    ServicioSedeViewSet,
    AutoevaluacionViewSet,
    CumplimientoViewSet,
    CapacidadInstaladaViewSet,
    MedidaSeguridadServicioViewSet,
    SancionServicioViewSet,
    NovedadREPSViewSet,
    RequisitoDocumentalViewSet,
    ChecklistVerificacionViewSet,
    ChecklistItemViewSet,
    EvidenciaChecklistViewSet,
)

# Crear router y registrar viewsets
router = DefaultRouter()
router.register(r'prestadores', DatosPrestadorViewSet, basename='datosprestador')
router.register(r'servicios', ServicioSedeViewSet, basename='serviciosede')
router.register(r'autoevaluaciones', AutoevaluacionViewSet, basename='autoevaluacion')
router.register(r'cumplimientos', CumplimientoViewSet, basename='cumplimiento')
router.register(r'capacidades', CapacidadInstaladaViewSet, basename='capacidadinstalada')
router.register(r'medidas-seguridad', MedidaSeguridadServicioViewSet, basename='medidaseguridad')
router.register(r'sanciones', SancionServicioViewSet, basename='sancionservicio')
router.register(r'novedades-reps', NovedadREPSViewSet, basename='novedadreps')
router.register(r'requisitos-documentales', RequisitoDocumentalViewSet, basename='requisitodocumental')
router.register(r'checklists-verificacion', ChecklistVerificacionViewSet, basename='checklistverificacion')
router.register(r'checklist-items', ChecklistItemViewSet, basename='checklistitem')
router.register(r'evidencias-checklist', EvidenciaChecklistViewSet, basename='evidenciachecklist')

# URLconf
urlpatterns = [
    path('', include(router.urls)),
]
