from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DepartmentViewSet, HeadquartersViewSet, ProcessTypeViewSet, ProcessViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'headquarters', HeadquartersViewSet)
router.register(r'process_types', ProcessTypeViewSet)
router.register(r'processes', ProcessViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
