from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ..models import EntidadAuditoria
from ..serializers import EntidadAuditoriaSerializer


class EntidadAuditoriaViewSet(viewsets.ModelViewSet):
    """ViewSet para entidades de auditoría."""
    queryset = EntidadAuditoria.objects.all()
    serializer_class = EntidadAuditoriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo_entidad', 'activo']
    search_fields = ['nombre', 'contacto', 'email']

