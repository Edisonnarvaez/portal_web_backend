"""
mejoras/urls.py

Rutas para los endpoints de planes de mejora y hallazgos.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PlanMejoraViewSet, HallazgoViewSet

router = DefaultRouter()
router.register(r'planes-mejora', PlanMejoraViewSet, basename='plan-mejora')
router.register(r'hallazgos', HallazgoViewSet, basename='hallazgo')

urlpatterns = [
    path('', include(router.urls)),
]
