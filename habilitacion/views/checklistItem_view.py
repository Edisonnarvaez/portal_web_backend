from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import ChecklistItem
from ..serializers import ChecklistItemSerializer


class ChecklistItemViewSet(viewsets.ModelViewSet):
	"""API para gestionar items del checklist y su resultado de verificacion."""

	queryset = ChecklistItem.objects.select_related(
		'checklist', 'requisito', 'verificado_por'
	).prefetch_related('evidencias')
	serializer_class = ChecklistItemSerializer
	permission_classes = [IsAuthenticated]
	filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
	filterset_fields = ['checklist', 'cumple', 'obligatorio']
	ordering_fields = ['fecha_creacion', 'fecha_verificacion']
	ordering = ['-fecha_creacion']

	def perform_update(self, serializer):
		serializer.save(verificado_por=self.request.user)

