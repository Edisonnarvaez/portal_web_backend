from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaSoporteViewSet,
    SoporteDocumentalViewSet,
    TipoDocumentoSoporteViewSet,
)

router = DefaultRouter()
router.register(r'categorias', CategoriaSoporteViewSet, basename='soporte-categoria')
router.register(r'tipos-documento', TipoDocumentoSoporteViewSet, basename='soporte-tipo-documento')
router.register(r'documentos', SoporteDocumentalViewSet, basename='soporte-documental')

urlpatterns = [
    path('', include(router.urls)),
]
