from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import DatosPrestador, ServicioSede
from ..serializers import (
    AutoevaluacionListSerializer,
    DatosPrestadorDetailSerializer,
    DatosPrestadorListSerializer,
    ServicioSedeListSerializer,
)


class DatosPrestadorViewSet(viewsets.ModelViewSet):
    """
    API para gestionar datos de habilitacion de prestadores.

    - GET /api/habilitacion/prestadores/ -> Listar todos
    - POST /api/habilitacion/prestadores/ -> Crear nuevo
    - GET /api/habilitacion/prestadores/{id}/ -> Detalle
    - PUT /api/habilitacion/prestadores/{id}/ -> Actualizar completo
    - PATCH /api/habilitacion/prestadores/{id}/ -> Actualizar parcial
    - DELETE /api/habilitacion/prestadores/{id}/ -> Eliminar

    Acciones personalizadas:
    - GET /api/habilitacion/prestadores/proximos_a_vencer/ -> Vencimiento proximo
    - GET /api/habilitacion/prestadores/{id}/servicios/ -> Servicios del prestador
    - GET /api/habilitacion/prestadores/{id}/renovar/ -> Preparar renovacion
    """

    queryset = DatosPrestador.objects.select_related(
        'headquarters', 'headquarters__company', 'usuario_responsable'
    )
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
        'headquarters__company__name',
        'nombre_prestador',
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
        """Prestadores con habilitacion proxima a vencer (proximos 90 dias)."""
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=90)

        queryset = self.queryset.filter(
            fecha_vencimiento_habilitacion__gte=hoy,
            fecha_vencimiento_habilitacion__lte=limite,
            estado_habilitacion='HABILITADA',
        ).order_by('fecha_vencimiento_habilitacion')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DatosPrestadorListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DatosPrestadorListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """Prestadores con habilitacion vencida."""
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
        servicios = ServicioSede.objects.filter(prestador=prestador)

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
        """Iniciar proceso de renovacion de habilitacion."""
        prestador = self.get_object()

        if not prestador.esta_proxima_a_vencer(dias=180):
            return Response(
                {
                    'error': 'Solo se puede renovar hasta 180 dias antes del vencimiento.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        prestador.estado_habilitacion = 'EN_PROCESO'
        prestador.save()

        serializer = self.get_serializer(prestador)
        return Response(serializer.data)