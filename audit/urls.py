from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuditoriaViewSet,
    EntidadAuditoriaViewSet,
    TipoAuditoriaViewSet,
    HallazgoAuditoriaViewSet,
    ActaReunionViewSet,
    ProgramaAuditoriaViewSet,
)

router = DefaultRouter()
router.register(r'auditorias', AuditoriaViewSet)
router.register(r'entidades', EntidadAuditoriaViewSet)
router.register(r'tipos', TipoAuditoriaViewSet)
router.register(r'hallazgos', HallazgoAuditoriaViewSet)
router.register(r'actas', ActaReunionViewSet)
router.register(r'programas', ProgramaAuditoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
