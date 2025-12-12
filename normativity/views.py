"""
normativity/views.py

Views para consulta de datos maestros normativos.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Estandar, Criterio, DocumentoNormativo
from .serializers import (
    EstandarSerializer,
    EstandarListSerializer,
    CriterioSerializer,
    DocumentoNormativoSerializer,
)


class EstandarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar Estándares.
    
    Los estándares son datos maestros, por lo que son solo lectura.
    """
    
    permission_classes = [AllowAny]
    queryset = Estandar.objects.filter(estado=True).prefetch_related('criterios')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'descripcion']
    filterset_fields = ['codigo', 'estado']
    
    def get_serializer_class(self):
        """Usar serializer simplificado en list, detallado en retrieve."""
        if self.action == 'list':
            return EstandarListSerializer
        return EstandarSerializer
    
    @action(detail=False, methods=['get'])
    def todos(self, request):
        """
        Endpoint para obtener todos los estándares con sus criterios.
        Útil para cargar toda la taxonomía en el frontend.
        """
        estandares = self.get_queryset()
        serializer = EstandarSerializer(estandares, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def criterios(self, request, pk=None):
        """
        Obtener todos los criterios de un estándar específico.
        """
        estandar = self.get_object()
        criterios = estandar.criterios.filter(estado=True)
        serializer = CriterioSerializer(criterios, many=True)
        return Response(serializer.data)


class CriterioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar Criterios.
    
    Los criterios pueden filtrarse por estándar y complejidad.
    """
    
    permission_classes = [AllowAny]
    queryset = Criterio.objects.filter(estado=True).select_related('estandar')
    serializer_class = CriterioSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'descripcion']
    filterset_fields = ['estandar', 'complejidad', 'aplica_todos', 'es_mandatorio']
    ordering_fields = ['codigo', 'nombre', 'complejidad']
    ordering = ['codigo']
    
    @action(detail=False, methods=['get'])
    def por_complejidad(self, request):
        """
        Agrupar criterios por complejidad.
        """
        complejidad = request.query_params.get('complejidad')
        
        if not complejidad:
            return Response(
                {'error': 'Parámetro "complejidad" requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        criterios = self.get_queryset().filter(complejidad=complejidad)
        serializer = self.get_serializer(criterios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mandatorios(self, request):
        """
        Obtener solo criterios mandatorios.
        """
        criterios = self.get_queryset().filter(es_mandatorio=True)
        serializer = self.get_serializer(criterios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def con_evidencia(self, request):
        """
        Obtener criterios que requieren evidencia documental.
        """
        criterios = self.get_queryset().filter(requiere_evidencia_documental=True)
        serializer = self.get_serializer(criterios, many=True)
        return Response(serializer.data)


class DocumentoNormativoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar Documentos Normativos.
    
    Proporciona acceso a referencias de leyes, resoluciones, manuales, etc.
    """
    
    permission_classes = [AllowAny]
    queryset = DocumentoNormativo.objects.all().prefetch_related('criterios_relacionados')
    serializer_class = DocumentoNormativoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['titulo', 'numero_referencia', 'descripcion']
    filterset_fields = ['tipo']
    ordering_fields = ['fecha_publicacion', 'titulo']
    ordering = ['-fecha_publicacion']
    
    @action(detail=True, methods=['get'])
    def criterios(self, request, pk=None):
        """
        Obtener criterios relacionados con un documento normativo.
        """
        documento = self.get_object()
        criterios = documento.criterios_relacionados.all()
        serializer = CriterioSerializer(criterios, many=True)
        return Response(serializer.data)
