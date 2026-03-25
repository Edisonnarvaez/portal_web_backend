from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Autoevaluacion, Cumplimiento, ServicioSede
from ..serializers import (
    CumplimientoDetailSerializer,
    CumplimientoListSerializer,
    ServicioSedeListSerializer,
)


class CumplimientoViewSet(viewsets.ModelViewSet):
    """
    API para gestionar registros de cumplimiento de criterios.

    Acciones personalizadas:
    - GET /api/habilitacion/cumplimientos/sin_cumplir/ -> No cumplen
    - GET /api/habilitacion/cumplimientos/con_plan_mejora/ -> Con plan de mejora
    - GET /api/habilitacion/cumplimientos/mejoras_vencidas/ -> Compromisos vencidos
    - GET /api/habilitacion/cumplimientos/servicios_de_autoevaluacion/ -> Servicios filtrados
    """

    queryset = Cumplimiento.objects.select_related(
        'autoevaluacion',
        'servicio_sede',
        'criterio',
        'responsable_mejora',
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

    def perform_create(self, serializer):
        """Validacion adicional al crear cumplimiento."""
        autoevaluacion = serializer.validated_data.get('autoevaluacion')
        servicio_sede = serializer.validated_data.get('servicio_sede')

        if autoevaluacion and servicio_sede:
            if servicio_sede.prestador != autoevaluacion.datos_prestador:
                raise serializers.ValidationError(
                    {
                        'servicio_sede': [
                            (
                                "El servicio debe pertenecer al prestador "
                                f"'{autoevaluacion.datos_prestador.nombre_prestador}' "
                                'que tiene la autoevaluacion seleccionada.'
                            )
                        ]
                    }
                )

        serializer.save()

    @action(detail=False, methods=['get'])
    def servicios_de_autoevaluacion(self, request):
        """
        Obtiene los servicios disponibles para una autoevaluacion especifica.

        Parametros de query:
        - autoevaluacion_id: ID de la autoevaluacion (requerido)

        Retorna: Lista de servicios del prestador vinculado a la autoevaluacion

        Ejemplo: GET /api/habilitacion/cumplimientos/servicios_de_autoevaluacion/?autoevaluacion_id=5
        """
        autoevaluacion_id = request.query_params.get('autoevaluacion_id')

        if not autoevaluacion_id:
            return Response(
                {
                    'error': 'Parametro requerido: autoevaluacion_id',
                    'ejemplo': '/api/habilitacion/cumplimientos/servicios_de_autoevaluacion/?autoevaluacion_id=5',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            autoevaluacion = Autoevaluacion.objects.get(pk=autoevaluacion_id)
        except Autoevaluacion.DoesNotExist:
            return Response(
                {'error': f'La autoevaluacion con ID {autoevaluacion_id} no existe.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        prestador = autoevaluacion.datos_prestador
        servicios = ServicioSede.objects.filter(prestador=prestador)

        serializer = ServicioSedeListSerializer(servicios, many=True)

        return Response(
            {
                'autoevaluacion': {
                    'id': autoevaluacion.id,
                    'numero': autoevaluacion.numero_autoevaluacion,
                    'periodo': autoevaluacion.periodo,
                },
                'prestador': {
                    'id': prestador.id,
                    'codigo_reps': prestador.codigo_reps,
                    'nombre': prestador.nombre_prestador,
                },
                'servicios': serializer.data,
                'total_servicios': servicios.count(),
            }
        )

    @action(detail=False, methods=['get'])
    def sin_cumplir(self, request):
        """Criterios no cumplidos con planes de mejora."""
        queryset = self.queryset.filter(cumple='NO_CUMPLE').order_by('fecha_compromiso')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CumplimientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CumplimientoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def con_plan_mejora(self, request):
        """Cumplimientos con plan de mejora pendiente."""
        queryset = self.queryset.filter(plan_mejora__isnull=False).exclude(plan_mejora='')

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
            cumple='NO_CUMPLE',
        ).order_by('fecha_compromiso')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CumplimientoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CumplimientoListSerializer(queryset, many=True)
        return Response(serializer.data)
