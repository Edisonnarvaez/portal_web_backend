from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from ..models import EvidenciaChecklist
from ..serializers import EvidenciaChecklistSerializer


class EvidenciaChecklistViewSet(viewsets.ModelViewSet):
    """API para cargue de soportes de items de checklist."""

    queryset = EvidenciaChecklist.objects.select_related('checklist_item', 'subido_por')
    serializer_class = EvidenciaChecklistSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['checklist_item', 'tipo']
    ordering_fields = ['fecha_subida']
    ordering = ['-fecha_subida']

    def perform_create(self, serializer):
        serializer.save(subido_por=self.request.user)
