from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ServicioSede
from ..serializers import (
    CumplimientoListSerializer,
    ServicioSedeDetailSerializer,
    ServicioSedeListSerializer,
)


class ServicioSedeViewSet(viewsets.ModelViewSet):
    """
    API para gestionar servicios de salud por sede.

    Acciones personalizadas:
    - GET /api/habilitacion/servicios/proximos_a_vencer/ -> Servicios proximos a vencer
    - GET /api/habilitacion/servicios/por_complejidad/?complejidad=ALTA -> Filtrar por complejidad
    - GET /api/habilitacion/servicios/{id}/cumplimientos/ -> Cumplimientos del servicio
    """

    queryset = ServicioSede.objects.select_related(
        'prestador', 'prestador__headquarters', 'prestador__headquarters__company'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        'prestador',
        'modalidad',
        'complejidad',
        'estado_habilitacion',
    ]
    search_fields = [
        'codigo_servicio',
        'nombre_servicio',
        'prestador__codigo_reps',
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
        """Servicios proximos a vencer (proximos 90 dias)."""
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=90)

        queryset = self.queryset.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite,
            estado_habilitacion='HABILITADO',
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
                {'error': 'Parametro complejidad requerido (BAJA, MEDIA, ALTA)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.queryset.filter(complejidad=complejidad)

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

        autoevaluacion_id = request.query_params.get('autoevaluacion_id')
        cumplimientos = servicio.cumplimientos.all()

        if autoevaluacion_id:
            cumplimientos = cumplimientos.filter(autoevaluacion_id=autoevaluacion_id)

        page = self.paginate_queryset(cumplimientos.order_by('-fecha_actualizacion'))
        if page is not None:
            serializer = CumplimientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CumplimientoListSerializer(cumplimientos, many=True)
        return Response(serializer.data)
