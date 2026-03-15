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
    DocumentoNormativoWriteSerializer,
)


"""
View que permite solo lectura sin autenticación.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class PublicReadOnly(BasePermission):
    """
    Permiso que permite lectura pública (GET) pero requiere autenticación para escritura.
    """
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS son permitidos para anyone
        if request.method in SAFE_METHODS:
            return True
        # POST, PUT, DELETE requieren autenticación
        return request.user and request.user.is_authenticated


class EstandarViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de Estándares.
    
    - GET: Acceso público
    - POST/PUT/DELETE: Requiere autenticación
    """
    
    permission_classes = [PublicReadOnly]
    queryset = Estandar.objects.all().prefetch_related('criterios')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'descripcion']
    filterset_fields = ['codigo', 'estado']
    
    def get_queryset(self):
        """En list, mostrar solo estándares activos. En detail, mostrar todos."""
        if self.action == 'list':
            return self.queryset.filter(estado=True)
        return self.queryset
    
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



class CriterioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de Criterios.
    
    - GET: Acceso público
    - POST/PUT/DELETE: Requiere autenticación
    
    Los criterios pueden filtrarse por estándar y complejidad.
    """
    
    permission_classes = [PublicReadOnly]
    queryset = Criterio.objects.all().select_related('estandar')
    serializer_class = CriterioSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'descripcion']
    filterset_fields = ['estandar', 'complejidad', 'aplica_todos', 'es_mandatorio', 'estado']
    ordering_fields = ['codigo', 'nombre', 'complejidad']
    ordering = ['codigo']
    
    def get_queryset(self):
        """En list, mostrar solo criterios activos. En detail, mostrar todos."""
        if self.action == 'list':
            return self.queryset.filter(estado=True)
        return self.queryset
    
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


class DocumentoNormativoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de Documentos Normativos.
    
    - GET: Acceso público
    - POST/PUT/DELETE: Requiere autenticación
    
    Proporciona acceso a referencias de leyes, resoluciones, manuales, etc.
    """
    
    permission_classes = [PublicReadOnly]
    queryset = DocumentoNormativo.objects.all().prefetch_related('criterios_relacionados')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['titulo', 'numero_referencia', 'descripcion']
    filterset_fields = ['tipo']
    ordering_fields = ['fecha_publicacion', 'titulo']
    ordering = ['-fecha_publicacion']
    
    def get_serializer_class(self):
        """Usar diferentes serializers para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return DocumentoNormativoWriteSerializer
        return DocumentoNormativoSerializer
    
    @action(detail=True, methods=['get'])
    def criterios(self, request, pk=None):
        """
        Obtener criterios relacionados con un documento normativo.
        """
        documento = self.get_object()
        criterios = documento.criterios_relacionados.all()
        serializer = CriterioSerializer(criterios, many=True)
        return Response(serializer.data)
