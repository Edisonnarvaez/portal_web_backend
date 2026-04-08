from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import CategoriaSoporte, SoporteDocumental, TipoDocumentoSoporte
from .serializers import (
    CategoriaSoporteSerializer,
    SoporteDocumentalSerializer,
    TipoDocumentoSoporteSerializer,
)


class CategoriaSoporteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CategoriaSoporte.objects.all()
    serializer_class = CategoriaSoporteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class TipoDocumentoSoporteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TipoDocumentoSoporte.objects.select_related('categoria').all()
    serializer_class = TipoDocumentoSoporteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria','nivel_aplica', 'es_obligatorio', 'requiere_vencimiento', 'activo']
    search_fields = ['nombre', 'categoria__nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class SoporteDocumentalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SoporteDocumental.objects.select_related(
        'tipo_documento',
        'tipo_documento__categoria',
        'empresa',
        'sede',
        'servicio',
    ).all().order_by('-fecha_carga')
    serializer_class = SoporteDocumentalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        'nivel',
        'empresa',
        'sede',
        'servicio',
        'tipo_documento',
        'es_vigente',
    ]
    ordering_fields = ['fecha_carga', 'fecha_emision', 'fecha_vencimiento', 'version']
    ordering = ['-fecha_carga']
