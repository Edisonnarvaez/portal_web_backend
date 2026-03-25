from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import MedidaSeguridadServicio
from ..serializers import MedidaSeguridadServicioSerializer


class MedidaSeguridadServicioViewSet(viewsets.ModelViewSet):
    """API para medidas de seguridad por servicio."""

    queryset = MedidaSeguridadServicio.objects.select_related('servicio_sede', 'servicio_sede__prestador')
    serializer_class = MedidaSeguridadServicioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['servicio_sede', 'estado']
    ordering_fields = ['fecha_creacion', 'fecha_inicio', 'fecha_fin']
    ordering = ['-fecha_creacion']
