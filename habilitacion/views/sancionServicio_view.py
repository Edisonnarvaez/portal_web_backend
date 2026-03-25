from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import SancionServicio
from ..serializers import SancionServicioSerializer


class SancionServicioViewSet(viewsets.ModelViewSet):
    """API para sanciones por servicio."""

    queryset = SancionServicio.objects.select_related('servicio_sede', 'servicio_sede__prestador')
    serializer_class = SancionServicioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['servicio_sede', 'tipo_sancion', 'estado']
    ordering_fields = ['fecha_creacion', 'fecha_inicio', 'fecha_fin']
    ordering = ['-fecha_creacion']
