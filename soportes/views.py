from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    CategoriaSoporte,
    SoporteDocumental,
    SoporteRequerido,
    TipoDocumentoSoporte,
)
from .serializers import (
    CategoriaSoporteSerializer,
    SoporteDocumentalSerializer,
    SoporteRequeridoSerializer,
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


# ✅ NUEVO VIEWSET PARA SOPORTE REQUERIDO
class SoporteRequeridoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SoporteRequerido.objects.select_related(
        'prestador',
        'tipo_documento',
        'empresa',
        'sede',
        'servicio',
    ).all()
    serializer_class = SoporteRequeridoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # ✅ FILTROS DISPONIBLES
    filterset_fields = [
        'prestador',
        'empresa',
        'sede',
        'servicio',
        'tipo_documento',
        'estado',
    ]
    ordering_fields = ['prestador', 'estado']
    ordering = ['prestador', 'estado']

    def get_queryset(self):
        """✅ FILTRAR AUTOMÁTICAMENTE POR PRESTADOR DEL REQUEST SI SE PROPORCIONA"""
        queryset = super().get_queryset()
        prestador_id = self.request.query_params.get('prestador_id')
        if prestador_id:
            queryset = queryset.filter(prestador_id=prestador_id)
        return queryset


class SoporteDocumentalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SoporteDocumental.objects.select_related(
        'prestador',
        'tipo_documento',
        'tipo_documento__categoria',
        'empresa',
        'sede',
        'servicio',
    ).all().order_by('-fecha_carga')
    serializer_class = SoporteDocumentalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # ✅ AGREGAR prestador AL FILTRO
    filterset_fields = [
        'prestador',
        'nivel',
        'empresa',
        'sede',
        'servicio',
        'tipo_documento',
        'es_vigente',
    ]
    ordering_fields = ['fecha_carga', 'fecha_emision', 'fecha_vencimiento', 'version']
    ordering = ['-fecha_carga']

    def get_queryset(self):
        """✅ FILTRAR AUTOMÁTICAMENTE POR PRESTADOR DEL REQUEST SI SE PROPORCIONA"""
        queryset = super().get_queryset()
        prestador_id = self.request.query_params.get('prestador_id')
        if prestador_id:
            queryset = queryset.filter(prestador_id=prestador_id)
        return queryset
