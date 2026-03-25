from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import CapacidadInstalada
from ..serializers import CapacidadInstaladaSerializer


class CapacidadInstaladaViewSet(viewsets.ModelViewSet):
	"""API para capacidad instalada de servicios (camas, ambulancias, salas, etc.)."""

	queryset = CapacidadInstalada.objects.select_related('servicio_sede', 'servicio_sede__prestador')
	serializer_class = CapacidadInstaladaSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
	filterset_fields = ['servicio_sede', 'tipo_capacidad', 'activo']
	ordering_fields = ['fecha_creacion', 'cantidad']
	ordering = ['-fecha_creacion']

