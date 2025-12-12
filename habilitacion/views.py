"""
habilitacion/views.py

ViewSets para la API de habilitación de servicios de salud.
Incluye lógica transaccional, filtrado avanzado y acciones personalizadas.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg, Case, When, IntegerField
from datetime import timedelta

from .models import DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento
from .serializers import (
    DatosPrestadorListSerializer,
    DatosPrestadorDetailSerializer,
    ServicioSedeListSerializer,
    ServicioSedeDetailSerializer,
    AutoevaluacionListSerializer,
    AutoevaluacionDetailSerializer,
    CumplimientoListSerializer,
    CumplimientoDetailSerializer,
)


class DatosPrestadorViewSet(viewsets.ModelViewSet):
    """
    API para gestionar datos de habilitación de prestadores.
    
    - GET /api/habilitacion/prestadores/ → Listar todos
    - POST /api/habilitacion/prestadores/ → Crear nuevo
    - GET /api/habilitacion/prestadores/{id}/ → Detalle
    - PUT /api/habilitacion/prestadores/{id}/ → Actualizar completo
    - PATCH /api/habilitacion/prestadores/{id}/ → Actualizar parcial
    - DELETE /api/habilitacion/prestadores/{id}/ → Eliminar
    
    Acciones personalizadas:
    - GET /api/habilitacion/prestadores/proximos_a_vencer/ → Vencimiento próximo
    - GET /api/habilitacion/prestadores/{id}/servicios/ → Servicios del prestador
    - GET /api/habilitacion/prestadores/{id}/renovar/ → Preparar renovación
    """
    
    queryset = DatosPrestador.objects.select_related('company', 'usuario_responsable')
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        'estado_habilitacion',
        'clase_prestador',
    ]
    search_fields = [
        'codigo_reps',
        'company__name',
    ]
    ordering_fields = [
        'fecha_vencimiento_habilitacion',
        'fecha_creacion',
    ]
    ordering = ['-fecha_creacion']
    
    def get_serializer_class(self):
        """Usa serializer simplificado para list, detallado para otros."""
        if self.action == 'list':
            return DatosPrestadorListSerializer
        return DatosPrestadorDetailSerializer
    
    def perform_create(self, serializer):
        """Asignar usuario responsable al crear."""
        serializer.save(usuario_responsable=self.request.user)
    
    @action(detail=False, methods=['get'])
    def proximos_a_vencer(self, request):
        """Prestadores con habilitación próxima a vencer (próximos 90 días)."""
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=90)
        
        queryset = self.queryset.filter(
            fecha_vencimiento_habilitacion__gte=hoy,
            fecha_vencimiento_habilitacion__lte=limite,
            estado_habilitacion='HABILITADA'
        ).order_by('fecha_vencimiento_habilitacion')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DatosPrestadorListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = DatosPrestadorListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """Prestadores con habilitación vencida."""
        hoy = timezone.now().date()
        queryset = self.queryset.filter(
            fecha_vencimiento_habilitacion__lt=hoy
        ).order_by('fecha_vencimiento_habilitacion')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DatosPrestadorListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = DatosPrestadorListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def servicios(self, request, pk=None):
        """Servicios habilitados de un prestador (por sede)."""
        prestador = self.get_object()
        servicios = ServicioSede.objects.filter(
            sede__company=prestador.company
        )
        
        serializer = ServicioSedeListSerializer(servicios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def autoevaluaciones(self, request, pk=None):
        """Historial de autoevaluaciones de un prestador."""
        prestador = self.get_object()
        autoevaluaciones = prestador.autoevaluaciones.all().order_by('-periodo')
        
        page = self.paginate_queryset(autoevaluaciones)
        if page is not None:
            serializer = AutoevaluacionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AutoevaluacionListSerializer(autoevaluaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def iniciar_renovacion(self, request, pk=None):
        """Iniciar proceso de renovación de habilitación."""
        prestador = self.get_object()
        
        # Validar que pueda renovarse
        if not prestador.esta_proxima_a_vencer(dias=180):
            return Response(
                {
                    'error': 'Solo se puede renovar hasta 180 días antes del vencimiento.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar estado a EN_PROCESO
        prestador.estado_habilitacion = 'EN_PROCESO'
        prestador.save()
        
        serializer = self.get_serializer(prestador)
        return Response(serializer.data)


class ServicioSedeViewSet(viewsets.ModelViewSet):
    """
    API para gestionar servicios de salud por sede.
    
    Acciones personalizadas:
    - GET /api/habilitacion/servicios/proximos_a_vencer/ → Servicios próximos a vencer
    - GET /api/habilitacion/servicios/por_complejidad/?complejidad=ALTA → Filtrar por complejidad
    - GET /api/habilitacion/servicios/{id}/cumplimientos/ → Cumplimientos del servicio
    """
    
    queryset = ServicioSede.objects.select_related('sede', 'sede__company')
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        'sede',
        'modalidad',
        'complejidad',
        'estado_habilitacion',
    ]
    search_fields = [
        'codigo_servicio',
        'nombre_servicio',
        'sede__name',
    ]
    ordering_fields = [
        'fecha_vencimiento',
        'complejidad',
    ]
    ordering = ['-fecha_vencimiento']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServicioSedeListSerializer
        return ServicioSedeDetailSerializer
    
    @action(detail=False, methods=['get'])
    def proximos_a_vencer(self, request):
        """Servicios próximos a vencer (próximos 90 días)."""
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=90)
        
        queryset = self.queryset.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite,
            estado_habilitacion='HABILITADO'
        ).order_by('fecha_vencimiento')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ServicioSedeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ServicioSedeListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_complejidad(self, request):
        """Filtrar servicios por nivel de complejidad."""
        complejidad = request.query_params.get('complejidad')
        if not complejidad:
            return Response(
                {'error': 'Parámetro complejidad requerido (BAJA, MEDIA, ALTA)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(
            complejidad=complejidad
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ServicioSedeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ServicioSedeListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cumplimientos(self, request, pk=None):
        """Cumplimientos evaluados del servicio en autoevaluaciones."""
        servicio = self.get_object()
        
        # Filtrar por autoevaluación si se especifica
        autoevaluacion_id = request.query_params.get('autoevaluacion_id')
        cumplimientos = servicio.cumplimientos.all()
        
        if autoevaluacion_id:
            cumplimientos = cumplimientos.filter(
                autoevaluacion_id=autoevaluacion_id
            )
        
        page = self.paginate_queryset(cumplimientos.order_by('-fecha_actualizacion'))
        if page is not None:
            serializer = CumplimientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CumplimientoListSerializer(cumplimientos, many=True)
        return Response(serializer.data)


class AutoevaluacionViewSet(viewsets.ModelViewSet):
    """
    API para gestionar autoevaluaciones anuales.
    
    Acciones personalizadas:
    - GET /api/habilitacion/autoevaluaciones/por_completar/ → Pendientes de completar
    - GET /api/habilitacion/autoevaluaciones/{id}/resumen/ → Resumen estadístico
    - POST /api/habilitacion/autoevaluaciones/{id}/validar/ → Validar autoevaluación
    - POST /api/habilitacion/autoevaluaciones/{id}/duplicar/ → Crear nueva versión (copiar)
    """
    
    queryset = Autoevaluacion.objects.select_related(
        'datos_prestador',
        'datos_prestador__company',
        'usuario_responsable'
    ).prefetch_related('cumplimientos')
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        'datos_prestador',
        'periodo',
        'estado',
    ]
    search_fields = [
        'numero_autoevaluacion',
        'datos_prestador__codigo_reps',
    ]
    ordering_fields = [
        'periodo',
        'estado',
        'fecha_vencimiento',
    ]
    ordering = ['-periodo', '-version']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AutoevaluacionListSerializer
        return AutoevaluacionDetailSerializer
    
    def perform_create(self, serializer):
        """Asignar usuario responsable y generar número."""
        autoevaluacion = serializer.save(usuario_responsable=self.request.user)
        # Generar número único
        autoevaluacion.numero_autoevaluacion = (
            f"AUT-{autoevaluacion.datos_prestador.codigo_reps}"
            f"-{autoevaluacion.periodo}-v{autoevaluacion.version}"
        )
        autoevaluacion.save()
    
    @action(detail=False, methods=['get'])
    def por_completar(self, request):
        """Autoevaluaciones no completadas."""
        queryset = self.queryset.filter(
            estado__in=['BORRADOR', 'EN_CURSO']
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AutoevaluacionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AutoevaluacionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resumen(self, request, pk=None):
        """Resumen estadístico de la autoevaluación."""
        autoevaluacion = self.get_object()
        
        cumplimientos = autoevaluacion.cumplimientos.all()
        
        stats = {
            'numero_autoevaluacion': autoevaluacion.numero_autoevaluacion,
            'periodo': autoevaluacion.periodo,
            'estado': autoevaluacion.get_estado_display(),
            'total_cumplimientos': cumplimientos.count(),
            'resumen_por_resultado': {
                'cumple': cumplimientos.filter(cumple='CUMPLE').count(),
                'no_cumple': cumplimientos.filter(cumple='NO_CUMPLE').count(),
                'parcialmente': cumplimientos.filter(cumple='PARCIALMENTE').count(),
                'no_aplica': cumplimientos.filter(cumple='NO_APLICA').count(),
            },
            'porcentaje_cumplimiento': round(
                autoevaluacion.porcentaje_cumplimiento(), 2
            ),
            'pendientes_mejora': cumplimientos.filter(
                plan_mejora__isnull=False
            ).count(),
            'mejoras_vencidas': cumplimientos.filter(
                fecha_compromiso__lt=timezone.now().date(),
                cumple='NO_CUMPLE'
            ).count(),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def validar(self, request, pk=None):
        """Cambiar estado a VALIDADA."""
        autoevaluacion = self.get_object()
        
        if autoevaluacion.estado == 'VALIDADA':
            return Response(
                {'error': 'La autoevaluación ya fue validada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        autoevaluacion.estado = 'VALIDADA'
        autoevaluacion.fecha_completacion = timezone.now().date()
        autoevaluacion.save()
        
        serializer = self.get_serializer(autoevaluacion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicar(self, request, pk=None):
        """
        Crear nueva versión copiando datos de esta autoevaluación.
        Útil para renovación anual.
        """
        autoevaluacion = self.get_object()
        
        # Calcular próximo periodo y versión
        siguiente_periodo = autoevaluacion.periodo + 1
        siguiente_version = 1
        
        # Crear nueva autoevaluación
        nueva_autoevaluacion = Autoevaluacion.objects.create(
            datos_prestador=autoevaluacion.datos_prestador,
            periodo=siguiente_periodo,
            version=siguiente_version,
            fecha_vencimiento=(
                timezone.now().date() + timedelta(days=365)
            ),
            estado='BORRADOR',
            usuario_responsable=request.user,
            observaciones=f"Copia del período {autoevaluacion.periodo}"
        )
        
        # Generar número
        nueva_autoevaluacion.numero_autoevaluacion = (
            f"AUT-{nueva_autoevaluacion.datos_prestador.codigo_reps}"
            f"-{siguiente_periodo}-v1"
        )
        nueva_autoevaluacion.save()
        
        serializer = self.get_serializer(nueva_autoevaluacion)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class CumplimientoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar registros de cumplimiento de criterios.
    
    Acciones personalizadas:
    - GET /api/habilitacion/cumplimientos/sin_cumplir/ → No cumplen
    - GET /api/habilitacion/cumplimientos/con_plan_mejora/ → Con plan de mejora
    - GET /api/habilitacion/cumplimientos/mejoras_vencidas/ → Compromisos vencidos
    """
    
    queryset = Cumplimiento.objects.select_related(
        'autoevaluacion',
        'servicio_sede',
        'criterio',
        'responsable_mejora'
    ).prefetch_related('documentos_evidencia')
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        'autoevaluacion',
        'servicio_sede',
        'criterio',
        'cumple',
    ]
    search_fields = [
        'criterio__codigo',
        'criterio__nombre',
    ]
    ordering_fields = [
        'fecha_creacion',
        'fecha_compromiso',
    ]
    ordering = ['-fecha_actualizacion']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CumplimientoListSerializer
        return CumplimientoDetailSerializer
    
    @action(detail=False, methods=['get'])
    def sin_cumplir(self, request):
        """Criterios no cumplidos con planes de mejora."""
        queryset = self.queryset.filter(
            cumple='NO_CUMPLE'
        ).order_by('fecha_compromiso')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CumplimientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CumplimientoListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def con_plan_mejora(self, request):
        """Cumplimientos con plan de mejora pendiente."""
        queryset = self.queryset.filter(
            plan_mejora__isnull=False
        ).exclude(plan_mejora='')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CumplimientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CumplimientoListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mejoras_vencidas(self, request):
        """Planes de mejora con fecha comprometida vencida."""
        hoy = timezone.now().date()
        queryset = self.queryset.filter(
            fecha_compromiso__lt=hoy,
            cumple='NO_CUMPLE'
        ).order_by('fecha_compromiso')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CumplimientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CumplimientoListSerializer(queryset, many=True)
        return Response(serializer.data)
