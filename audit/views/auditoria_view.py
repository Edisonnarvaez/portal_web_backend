"""
audit/views/auditoria_view.py

ViewSets para Auditorías, Hallazgos de Auditoría, Actas y Programas.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone

from ..models import (
    Auditoria,
    MiembroEquipoAuditor,
    HallazgoAuditoria,
    ActaReunion,
    ProgramaAuditoria,
)
from ..serializers import (
    AuditoriaListSerializer,
    AuditoriaDetailSerializer,
    AuditoriaCreateUpdateSerializer,
    MiembroEquipoSerializer,
    HallazgoAuditoriaListSerializer,
    HallazgoAuditoriaDetailSerializer,
    HallazgoAuditoriaCreateUpdateSerializer,
    ActaReunionSerializer,
    ProgramaAuditoriaListSerializer,
    ProgramaAuditoriaDetailSerializer,
    CambiarFaseSerializer,
)


class AuditoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Auditorías con ciclo de vida.

    Filtros:
        ?fase=PROGRAMADA|NOTIFICADA|EN_EJECUCION|INFORME|SEGUIMIENTO|CERRADA|CANCELADA
        ?clasificacion=INTERNA|EXTERNA
        ?auditoria_tipo=ID
        ?auditoria_entidad=ID
        ?auditoria_proceso=ID
        ?sede=ID
        ?auditoria_estado=true|false
    """
    queryset = Auditoria.objects.select_related(
        'auditoria_tipo', 'auditoria_entidad',
        'auditoria_proceso', 'sede',
        'auditor_lider', 'creado_por',
        'auditoria_relacionada',
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'fase', 'clasificacion', 'auditoria_tipo', 'auditoria_entidad',
        'auditoria_proceso', 'sede', 'auditoria_estado', 'auditor_lider',
    ]
    search_fields = ['auditoria_nombre', 'auditoria_detalle', 'norma_referencia']
    ordering_fields = ['fecha_creacion', 'fecha_programada', 'fase', 'clasificacion']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action == 'list':
            return AuditoriaListSerializer
        elif self.action == 'retrieve':
            return AuditoriaDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AuditoriaCreateUpdateSerializer
        return AuditoriaListSerializer

    # ─── Acciones de ciclo de vida ───

    @action(detail=True, methods=['post'], url_path='cambiar-fase')
    def cambiar_fase(self, request, pk=None):
        """Cambiar la fase de la auditoría con validación de transiciones."""
        auditoria = self.get_object()
        serializer = CambiarFaseSerializer(
            data=request.data,
            context={'auditoria': auditoria}
        )
        serializer.is_valid(raise_exception=True)
        nueva_fase = serializer.validated_data['nueva_fase']
        auditoria.avanzar_fase(nueva_fase)
        return Response(AuditoriaDetailSerializer(auditoria).data)

    # ─── Equipo auditor ───

    @action(detail=True, methods=['get', 'post'], url_path='equipo')
    def equipo(self, request, pk=None):
        """GET: Lista equipo auditor. POST: Agregar miembro."""
        auditoria = self.get_object()
        if request.method == 'GET':
            miembros = auditoria.equipo_auditor.select_related('usuario').all()
            serializer = MiembroEquipoSerializer(miembros, many=True)
            return Response(serializer.data)
        # POST
        data = request.data.copy()
        data['auditoria'] = auditoria.auditoria_id
        serializer = MiembroEquipoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            url_path='equipo/(?P<miembro_id>[0-9]+)')
    def eliminar_miembro(self, request, pk=None, miembro_id=None):
        """Eliminar un miembro del equipo auditor."""
        auditoria = self.get_object()
        try:
            miembro = auditoria.equipo_auditor.get(id=miembro_id)
        except MiembroEquipoAuditor.DoesNotExist:
            return Response({'detail': 'Miembro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        miembro.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ─── Actas ───

    @action(detail=True, methods=['get', 'post'], url_path='actas')
    def actas(self, request, pk=None):
        """GET: Lista actas. POST: Crear acta."""
        auditoria = self.get_object()
        if request.method == 'GET':
            actas = auditoria.actas.all()
            serializer = ActaReunionSerializer(actas, many=True)
            return Response(serializer.data)
        data = request.data.copy()
        data['auditoria'] = auditoria.auditoria_id
        serializer = ActaReunionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ─── Estadísticas ───

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """Resumen general de auditorías."""
        queryset = self.get_queryset()
        total = queryset.count()
        por_fase = {}
        for fase_code, fase_label in Auditoria.Fase.choices:
            por_fase[fase_code.lower()] = queryset.filter(fase=fase_code).count()

        data = {
            'total': total,
            'activas': queryset.filter(auditoria_estado=True).exclude(
                fase__in=['CERRADA', 'CANCELADA']
            ).count(),
            **por_fase,
            'internas': queryset.filter(clasificacion='INTERNA').count(),
            'externas': queryset.filter(clasificacion='EXTERNA').count(),
            'con_hallazgos': queryset.filter(hallazgos_auditoria__isnull=False).distinct().count(),
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='proximas')
    def proximas(self, request):
        """Auditorías próximas a ejecutarse (en los próximos N días)."""
        dias = int(request.query_params.get('dias', 30))
        from datetime import timedelta
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        queryset = self.get_queryset().filter(
            fecha_programada__lte=fecha_limite,
            fecha_programada__gte=timezone.now().date(),
            fase__in=['PROGRAMADA', 'NOTIFICADA'],
        )
        serializer = AuditoriaListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='por-fase')
    def por_fase(self, request):
        """Conteo de auditorías agrupadas por fase."""
        data = Auditoria.objects.values('fase').annotate(
            total=Count('auditoria_id')
        ).order_by('fase')
        return Response(list(data))


class HallazgoAuditoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para hallazgos de auditoría.

    Filtros:
        ?auditoria=ID
        ?tipo=NC_MAYOR|NC_MENOR|OBSERVACION|OPORTUNIDAD|FORTALEZA
        ?estado=IDENTIFICADO|PLAN_ACCION|EN_SEGUIMIENTO|VERIFICADO|CERRADO
        ?responsable_accion=ID
    """
    queryset = HallazgoAuditoria.objects.select_related(
        'auditoria', 'proceso_afectado',
        'responsable_accion', 'hallazgo_mejora', 'plan_mejora',
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['auditoria', 'tipo', 'estado', 'responsable_accion', 'proceso_afectado']
    search_fields = ['numero', 'descripcion', 'criterio_norma', 'evidencia_objetiva']
    ordering_fields = ['fecha_creacion', 'tipo', 'estado', 'fecha_limite_accion']
    ordering = ['numero']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HallazgoAuditoriaDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return HallazgoAuditoriaCreateUpdateSerializer
        return HallazgoAuditoriaListSerializer

    @action(detail=False, methods=['get'], url_path='vencidos')
    def vencidos(self, request):
        """Hallazgos con fecha límite vencida y no cerrados."""
        queryset = self.get_queryset().filter(
            fecha_limite_accion__lt=timezone.now().date()
        ).exclude(estado__in=['VERIFICADO', 'CERRADO'])
        serializer = HallazgoAuditoriaListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """Estadísticas de hallazgos de auditoría."""
        queryset = self.get_queryset()
        auditoria = request.query_params.get('auditoria')
        if auditoria:
            queryset = queryset.filter(auditoria_id=auditoria)

        data = {
            'total': queryset.count(),
            'nc_mayor': queryset.filter(tipo='NC_MAYOR').count(),
            'nc_menor': queryset.filter(tipo='NC_MENOR').count(),
            'observaciones': queryset.filter(tipo='OBSERVACION').count(),
            'oportunidades': queryset.filter(tipo='OPORTUNIDAD').count(),
            'fortalezas': queryset.filter(tipo='FORTALEZA').count(),
            'identificados': queryset.filter(estado='IDENTIFICADO').count(),
            'con_plan': queryset.filter(estado='PLAN_ACCION').count(),
            'en_seguimiento': queryset.filter(estado='EN_SEGUIMIENTO').count(),
            'verificados': queryset.filter(estado='VERIFICADO').count(),
            'cerrados': queryset.filter(estado='CERRADO').count(),
            'vencidos': queryset.filter(
                fecha_limite_accion__lt=timezone.now().date()
            ).exclude(estado__in=['VERIFICADO', 'CERRADO']).count(),
        }
        return Response(data)


class ActaReunionViewSet(viewsets.ModelViewSet):
    """ViewSet para actas de reunión de auditoría."""
    queryset = ActaReunion.objects.select_related('auditoria').all()
    serializer_class = ActaReunionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['auditoria', 'tipo_acta']
    ordering = ['-fecha']


class ProgramaAuditoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para programas de auditoría.

    Filtros:
        ?estado=BORRADOR|APROBADO|EN_EJECUCION|COMPLETADO
        ?periodo=2026
        ?responsable=ID
    """
    queryset = ProgramaAuditoria.objects.select_related('responsable').prefetch_related('auditorias').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'periodo', 'responsable']
    search_fields = ['nombre', 'periodo', 'descripcion']
    ordering = ['-periodo']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProgramaAuditoriaDetailSerializer
        return ProgramaAuditoriaListSerializer

