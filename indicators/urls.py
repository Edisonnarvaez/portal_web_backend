from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IndicatorViewSet, ResultViewSet

router = DefaultRouter()
router.register(r'indicators', IndicatorViewSet)
router.register(r'results', ResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
