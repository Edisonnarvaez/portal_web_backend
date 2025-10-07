from rest_framework.routers import DefaultRouter
from .views import TerceroViewSet
from tercero.views.terceros_paises_view import PaisViewSet
from tercero.views.terceros_departamento_view import DepartamentoViewSet
from tercero.views.terceros_municipios_view import MunicipioViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'terceros', TerceroViewSet, basename='terceros')
router.register(r'paises', PaisViewSet, basename='paises')
router.register(r'departamentos', DepartamentoViewSet, basename='departamentos')
router.register(r'municipios', MunicipioViewSet, basename='municipios')

urlpatterns = [
    path('', include(router.urls)),
]


 