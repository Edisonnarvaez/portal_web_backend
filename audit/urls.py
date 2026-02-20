from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditoriaViewSet, EntidadAuditoriaViewSet, TipoAuditoriaViewSet

router = DefaultRouter()
router.register(r'auditorias', AuditoriaViewSet)
router.register(r'entidades', EntidadAuditoriaViewSet)
router.register(r'tipos', TipoAuditoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
