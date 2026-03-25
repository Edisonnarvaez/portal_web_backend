from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import RequisitoDocumental
from ..serializers import RequisitoDocumentalSerializer


class RequisitoDocumentalViewSet(viewsets.ModelViewSet):
    """API catalogo de requisitos documentales (Anexo 2)."""

    queryset = RequisitoDocumental.objects.all()
    serializer_class = RequisitoDocumentalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_tramite', 'obligatorio', 'activo']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering_fields = ['codigo', 'fecha_creacion']
    ordering = ['codigo']
