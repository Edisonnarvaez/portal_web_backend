"""
normativity/urls.py

Rutas para los endpoints de normativity.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EstandarViewSet, CriterioViewSet, DocumentoNormativoViewSet

router = DefaultRouter()
router.register(r'estandares', EstandarViewSet, basename='estandar')
router.register(r'criterios', CriterioViewSet, basename='criterio')
router.register(r'documentos', DocumentoNormativoViewSet, basename='documento-normativo')

urlpatterns = [
    path('', include(router.urls)),
]
