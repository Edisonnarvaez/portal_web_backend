from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    FuncionarioViewSet,
    ContenidoInformativoViewSet,
    EventoViewSet,
    FelicitacionCumpleaniosViewSet,
    ReconocimientoViewSet
)

router = DefaultRouter()
router.register(r'funcionarios', FuncionarioViewSet)
router.register(r'contenidos', ContenidoInformativoViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'felicitaciones', FelicitacionCumpleaniosViewSet)
router.register(r'reconocimientos', ReconocimientoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
