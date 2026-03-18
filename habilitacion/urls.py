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
)

# Crear router y registrar viewsets
router = DefaultRouter()
router.register(r'prestadores', DatosPrestadorViewSet, basename='datosprestador')
router.register(r'servicios', ServicioSedeViewSet, basename='serviciosede')
router.register(r'autoevaluaciones', AutoevaluacionViewSet, basename='autoevaluacion')
router.register(r'cumplimientos', CumplimientoViewSet, basename='cumplimiento')

# URLconf
urlpatterns = [
    path('', include(router.urls)),
]
