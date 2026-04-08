from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet,
    DepartmentViewSet,
    HeadquartersViewSet,
    ProcessTypeViewSet,
    ProcessViewSet,
    RegionViewSet,
    MunicipalityViewSet,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'headquarters', HeadquartersViewSet)
router.register(r'process_types', ProcessTypeViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'municipalities', MunicipalityViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
