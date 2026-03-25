from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import NovedadREPS
from ..serializers import NovedadREPSSerializer


class NovedadREPSViewSet(viewsets.ModelViewSet):
    """API para registrar y gestionar novedades REPS."""

    queryset = NovedadREPS.objects.select_related(
        'datos_prestador', 'sede', 'servicio_sede', 'creado_por'
    )
    serializer_class = NovedadREPSSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_novedad', 'subtipo_novedad', 'estado', 'datos_prestador', 'sede', 'servicio_sede']
    search_fields = ['codigo_novedad', 'descripcion', 'datos_prestador__codigo_reps', 'datos_prestador__nombre_prestador']
    ordering_fields = ['fecha_creacion', 'fecha_radicacion']
    ordering = ['-fecha_creacion']

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
