from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Autoevaluacion
from ..serializers import AutoevaluacionDetailSerializer, AutoevaluacionListSerializer


class AutoevaluacionViewSet(viewsets.ModelViewSet):
	"""
	API para gestionar autoevaluaciones anuales.

	Acciones personalizadas:
	- GET /api/habilitacion/autoevaluaciones/por_completar/ -> Pendientes de completar
	- GET /api/habilitacion/autoevaluaciones/{id}/resumen/ -> Resumen estadistico
	- POST /api/habilitacion/autoevaluaciones/{id}/validar/ -> Validar autoevaluacion
	- POST /api/habilitacion/autoevaluaciones/{id}/duplicar/ -> Crear nueva version (copiar)
	"""

	queryset = Autoevaluacion.objects.select_related(
		'datos_prestador',
		'datos_prestador__headquarters',
		'datos_prestador__headquarters__company',
		'usuario_responsable',
	).prefetch_related('cumplimientos')
	permission_classes = [IsAuthenticated]
	filter_backends = [
		DjangoFilterBackend,
		filters.SearchFilter,
		filters.OrderingFilter,
	]
	filterset_fields = [
		'datos_prestador',
		'periodo',
		'estado',
	]
	search_fields = [
		'numero_autoevaluacion',
		'datos_prestador__codigo_reps',
	]
	ordering_fields = [
		'periodo',
		'estado',
		'fecha_vencimiento',
	]
	ordering = ['-periodo', '-version']

	def get_serializer_class(self):
		if self.action == 'list':
			return AutoevaluacionListSerializer
		return AutoevaluacionDetailSerializer

	def perform_create(self, serializer):
		"""Asignar usuario responsable y generar numero."""
		autoevaluacion = serializer.save(usuario_responsable=self.request.user)
		autoevaluacion.numero_autoevaluacion = (
			f"AUT-{autoevaluacion.datos_prestador.codigo_reps}"
			f"-{autoevaluacion.periodo}-v{autoevaluacion.version}"
		)
		autoevaluacion.save()

	@action(detail=False, methods=['get'])
	def por_completar(self, request):
		"""Autoevaluaciones no completadas."""
		queryset = self.queryset.filter(estado__in=['BORRADOR', 'EN_CURSO'])

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = AutoevaluacionListSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = AutoevaluacionListSerializer(queryset, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['get'])
	def resumen(self, request, pk=None):
		"""Resumen estadistico de la autoevaluacion."""
		autoevaluacion = self.get_object()

		cumplimientos = autoevaluacion.cumplimientos.all()

		stats = {
			'numero_autoevaluacion': autoevaluacion.numero_autoevaluacion,
			'periodo': autoevaluacion.periodo,
			'estado': autoevaluacion.get_estado_display(),
			'total_cumplimientos': cumplimientos.count(),
			'resumen_por_resultado': {
				'cumple': cumplimientos.filter(cumple='CUMPLE').count(),
				'no_cumple': cumplimientos.filter(cumple='NO_CUMPLE').count(),
				'parcialmente': cumplimientos.filter(cumple='PARCIALMENTE').count(),
				'no_aplica': cumplimientos.filter(cumple='NO_APLICA').count(),
			},
			'porcentaje_cumplimiento': round(autoevaluacion.porcentaje_cumplimiento(), 2),
			'pendientes_mejora': cumplimientos.filter(plan_mejora__isnull=False).count(),
			'mejoras_vencidas': cumplimientos.filter(
				fecha_compromiso__lt=timezone.now().date(),
				cumple='NO_CUMPLE',
			).count(),
		}

		return Response(stats)

	@action(detail=True, methods=['post'])
	def validar(self, request, pk=None):
		"""Cambiar estado a VALIDADA."""
		autoevaluacion = self.get_object()

		if autoevaluacion.estado == 'VALIDADA':
			return Response(
				{'error': 'La autoevaluacion ya fue validada.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		autoevaluacion.estado = 'VALIDADA'
		autoevaluacion.fecha_completacion = timezone.now().date()
		autoevaluacion.save()

		serializer = self.get_serializer(autoevaluacion)
		return Response(serializer.data)

	@action(detail=True, methods=['post'])
	def duplicar(self, request, pk=None):
		"""
		Crear nueva version copiando datos de esta autoevaluacion.
		Util para renovacion anual.
		"""
		autoevaluacion = self.get_object()

		siguiente_periodo = autoevaluacion.periodo + 1
		siguiente_version = 1

		nueva_autoevaluacion = Autoevaluacion.objects.create(
			datos_prestador=autoevaluacion.datos_prestador,
			periodo=siguiente_periodo,
			version=siguiente_version,
			fecha_vencimiento=(timezone.now().date() + timedelta(days=365)),
			estado='BORRADOR',
			usuario_responsable=request.user,
			observaciones=f"Copia del periodo {autoevaluacion.periodo}",
		)

		nueva_autoevaluacion.numero_autoevaluacion = (
			f"AUT-{nueva_autoevaluacion.datos_prestador.codigo_reps}"
			f"-{siguiente_periodo}-v1"
		)
		nueva_autoevaluacion.save()

		serializer = self.get_serializer(nueva_autoevaluacion)
		return Response(serializer.data, status=status.HTTP_201_CREATED)

