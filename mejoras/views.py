"""
mejoras/views.py

ViewSets para Planes de Mejora y Hallazgos.
Endpoints transversales con filtrado por origen (habilitacion, audit, indicators).
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import PlanMejora, Hallazgo, SoportePlan
from .serializers import (
    PlanMejoraListSerializer,
    PlanMejoraDetailSerializer,
    PlanMejoraCreateUpdateSerializer,
    PlanMejoraResumenSerializer,
    HallazgoListSerializer,
    HallazgoDetailSerializer,
    HallazgoCreateUpdateSerializer,
    EstadisticasHallazgosSerializer,
    SoportePlanSerializer,
    SoportePlanUploadSerializer,
)


# ═══════════════════════════════════════════════════════════════════
# PLAN DE MEJORA VIEWSET
# ═══════════════════════════════════════════════════════════════════

class PlanMejoraViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Planes de Mejora.

    Filtros disponibles:
        ?origen_tipo=HABILITACION|AUDITORIA|INDICADOR
        ?estado=PENDIENTE|EN_CURSO|COMPLETADO|VENCIDO
        ?autoevaluacion=ID
        ?auditoria=ID
        ?criterio=ID
        ?responsable=ID
        ?search=texto
        ?ordering=-fecha_vencimiento
    """

    queryset = PlanMejora.objects.select_related(
        'criterio', 'criterio__estandar',
        'autoevaluacion', 'cumplimiento',
        'auditoria', 'resultado_indicador',
        'responsable',
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'origen_tipo', 'estado', 'autoevaluacion', 'auditoria',
        'criterio', 'responsable', 'cumplimiento', 'resultado_indicador',
    ]
    search_fields = ['numero_plan', 'descripcion', 'acciones_implementar']
    ordering_fields = [
        'fecha_creacion', 'fecha_vencimiento', 'porcentaje_avance',
        'estado', 'origen_tipo',
    ]
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action == 'list':
            return PlanMejoraListSerializer
        elif self.action == 'retrieve':
            return PlanMejoraDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PlanMejoraCreateUpdateSerializer
        return PlanMejoraListSerializer

    # ─── Actions personalizadas ───

    @action(detail=False, methods=['get'], url_path='vencidos')
    def vencidos(self, request):
        """Planes de mejora con fecha de vencimiento pasada y no completados."""
        queryset = self.get_queryset().filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).exclude(estado='COMPLETADO')

        # Filtros opcionales
        origen = request.query_params.get('origen_tipo')
        if origen:
            queryset = queryset.filter(origen_tipo=origen)

        autoevaluacion = request.query_params.get('autoevaluacion')
        if autoevaluacion:
            queryset = queryset.filter(autoevaluacion_id=autoevaluacion)

        auditoria = request.query_params.get('auditoria')
        if auditoria:
            queryset = queryset.filter(auditoria_id=auditoria)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlanMejoraListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PlanMejoraListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='proximos-vencer')
    def proximos_vencer(self, request):
        """Planes que vencen en los próximos N días (default: 30)."""
        dias = int(request.query_params.get('dias', 30))
        from datetime import timedelta
        fecha_limite = timezone.now().date() + timedelta(days=dias)

        queryset = self.get_queryset().filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date()
        ).exclude(estado__in=['COMPLETADO', 'VENCIDO'])

        origen = request.query_params.get('origen_tipo')
        if origen:
            queryset = queryset.filter(origen_tipo=origen)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlanMejoraListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PlanMejoraListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """
        Estadísticas resumidas de planes de mejora.
        Filtros opcionales: ?origen_tipo=X&autoevaluacion=ID&auditoria=ID
        """
        queryset = self.get_queryset()

        origen = request.query_params.get('origen_tipo')
        if origen:
            queryset = queryset.filter(origen_tipo=origen)

        autoevaluacion = request.query_params.get('autoevaluacion')
        if autoevaluacion:
            queryset = queryset.filter(autoevaluacion_id=autoevaluacion)

        auditoria = request.query_params.get('auditoria')
        if auditoria:
            queryset = queryset.filter(auditoria_id=auditoria)

        data = {
            'total_planes': queryset.count(),
            'pendientes': queryset.filter(estado='PENDIENTE').count(),
            'en_curso': queryset.filter(estado='EN_CURSO').count(),
            'completados': queryset.filter(estado='COMPLETADO').count(),
            'vencidos': queryset.filter(
                fecha_vencimiento__lt=timezone.now().date()
            ).exclude(estado='COMPLETADO').count(),
            'porcentaje_promedio_avance': queryset.aggregate(
                avg=Avg('porcentaje_avance')
            )['avg'] or 0.0,
        }

        serializer = PlanMejoraResumenSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='por-origen')
    def por_origen(self, request):
        """
        Resumen agrupado por tipo de origen.
        Retorna conteos por cada origen_tipo.
        """
        data = PlanMejora.objects.values('origen_tipo').annotate(
            total=Count('id'),
            pendientes=Count('id', filter=Q(estado='PENDIENTE')),
            en_curso=Count('id', filter=Q(estado='EN_CURSO')),
            completados=Count('id', filter=Q(estado='COMPLETADO')),
            vencidos=Count('id', filter=Q(
                fecha_vencimiento__lt=timezone.now().date()
            ) & ~Q(estado='COMPLETADO')),
        ).order_by('origen_tipo')

        return Response(list(data))

    # ─── Soporte / Archivos adjuntos ───

    @action(detail=True, methods=['get', 'post'], url_path='soportes',
            parser_classes=[MultiPartParser, FormParser, JSONParser])
    def soportes(self, request, pk=None):
        """
        GET: Lista soportes del plan.
        POST: Sube un nuevo soporte (multipart/form-data).
        """
        plan = self.get_object()

        if request.method == 'GET':
            soportes = plan.soportes.all()
            serializer = SoportePlanSerializer(soportes, many=True)
            return Response(serializer.data)

        # POST
        data = request.data.copy()
        data['plan_mejora'] = plan.id
        serializer = SoportePlanUploadSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        soporte = serializer.save()
        return Response(
            SoportePlanSerializer(soporte).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], url_path='soportes/(?P<soporte_id>[0-9]+)')
    def eliminar_soporte(self, request, pk=None, soporte_id=None):
        """Elimina un soporte específico del plan."""
        plan = self.get_object()
        try:
            soporte = plan.soportes.get(id=soporte_id)
        except SoportePlan.DoesNotExist:
            return Response(
                {'detail': 'Soporte no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Eliminar archivo físico
        if soporte.archivo:
            soporte.archivo.delete(save=False)
        soporte.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════
# HALLAZGO VIEWSET
# ═══════════════════════════════════════════════════════════════════

class HallazgoViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Hallazgos.

    Filtros disponibles:
        ?origen_tipo=HABILITACION|AUDITORIA|INDICADOR
        ?tipo=FORTALEZA|OPORTUNIDAD_MEJORA|NO_CONFORMIDAD|HALLAZGO
        ?severidad=BAJA|MEDIA|ALTA|CRÍTICA
        ?estado=ABIERTO|EN_SEGUIMIENTO|CERRADO
        ?autoevaluacion=ID
        ?auditoria=ID
        ?criterio=ID
        ?plan_mejora=ID
    """

    queryset = Hallazgo.objects.select_related(
        'autoevaluacion', 'datos_prestador',
        'criterio', 'criterio__estandar',
        'auditoria', 'resultado_indicador',
        'plan_mejora',
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'origen_tipo', 'tipo', 'severidad', 'estado',
        'autoevaluacion', 'datos_prestador', 'auditoria',
        'criterio', 'plan_mejora', 'resultado_indicador',
    ]
    search_fields = ['numero_hallazgo', 'descripcion', 'area_responsable']
    ordering_fields = [
        'fecha_creacion', 'fecha_identificacion', 'severidad',
        'estado', 'tipo', 'origen_tipo',
    ]
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HallazgoDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return HallazgoCreateUpdateSerializer
        return HallazgoListSerializer

    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """
        Estadísticas de hallazgos.
        Filtros opcionales: ?origen_tipo=X&autoevaluacion=ID&auditoria=ID
        """
        queryset = self.get_queryset()

        origen = request.query_params.get('origen_tipo')
        if origen:
            queryset = queryset.filter(origen_tipo=origen)

        autoevaluacion = request.query_params.get('autoevaluacion')
        if autoevaluacion:
            queryset = queryset.filter(autoevaluacion_id=autoevaluacion)

        auditoria = request.query_params.get('auditoria')
        if auditoria:
            queryset = queryset.filter(auditoria_id=auditoria)

        data = {
            'total_hallazgos': queryset.count(),
            'fortalezas': queryset.filter(tipo='FORTALEZA').count(),
            'oportunidades_mejora': queryset.filter(tipo='OPORTUNIDAD_MEJORA').count(),
            'no_conformidades': queryset.filter(tipo='NO_CONFORMIDAD').count(),
            'hallazgos': queryset.filter(tipo='HALLAZGO').count(),
            'abiertos': queryset.filter(estado='ABIERTO').count(),
            'en_seguimiento': queryset.filter(estado='EN_SEGUIMIENTO').count(),
            'cerrados': queryset.filter(estado='CERRADO').count(),
            'criticos': queryset.filter(severidad='CRÍTICA').count(),
        }

        serializer = EstadisticasHallazgosSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='por-origen')
    def por_origen(self, request):
        """
        Resumen agrupado por tipo de origen.
        """
        data = Hallazgo.objects.values('origen_tipo').annotate(
            total=Count('id'),
            abiertos=Count('id', filter=Q(estado='ABIERTO')),
            en_seguimiento=Count('id', filter=Q(estado='EN_SEGUIMIENTO')),
            cerrados=Count('id', filter=Q(estado='CERRADO')),
            criticos=Count('id', filter=Q(severidad='CRÍTICA')),
        ).order_by('origen_tipo')

        return Response(list(data))

    @action(detail=False, methods=['get'], url_path='sin-plan')
    def sin_plan(self, request):
        """Hallazgos que no tienen plan de mejora asociado."""
        queryset = self.get_queryset().filter(plan_mejora__isnull=True)

        origen = request.query_params.get('origen_tipo')
        if origen:
            queryset = queryset.filter(origen_tipo=origen)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HallazgoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HallazgoListSerializer(queryset, many=True)
        return Response(serializer.data)
