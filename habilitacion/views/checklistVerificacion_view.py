from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ChecklistVerificacion
from ..serializers import ChecklistVerificacionSerializer


class ChecklistVerificacionViewSet(viewsets.ModelViewSet):
    """API de checklists documentales por tramite REPS."""

    queryset = ChecklistVerificacion.objects.select_related(
        'novedad', 'servicio_sede', 'responsable'
    ).prefetch_related('items')
    serializer_class = ChecklistVerificacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'novedad', 'servicio_sede']
    search_fields = ['codigo_checklist', 'observaciones']
    ordering_fields = ['fecha_creacion', 'fecha_cierre']
    ordering = ['-fecha_creacion']

    def perform_create(self, serializer):
        serializer.save(responsable=self.request.user)

    @action(detail=True, methods=['get'])
    def avance(self, request, pk=None):
        """Resumen de avance del checklist por items cumplidos."""
        checklist = self.get_object()
        total = checklist.items.count()
        cumplidos = checklist.items.filter(cumple=True).count()
        pendientes = checklist.items.filter(cumple__isnull=True).count()
        no_cumplen = checklist.items.filter(cumple=False).count()
        porcentaje = round((cumplidos / total) * 100, 2) if total else 0
        return Response(
            {
                'checklist_id': checklist.id,
                'codigo_checklist': checklist.codigo_checklist,
                'total_items': total,
                'cumplidos': cumplidos,
                'no_cumplen': no_cumplen,
                'pendientes': pendientes,
                'porcentaje_avance': porcentaje,
            }
        )
