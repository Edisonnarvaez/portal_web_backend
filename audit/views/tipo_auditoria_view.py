from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ..models import TipoAuditoria
from ..serializers import TipoAuditoriaSerializer


class TipoAuditoriaViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de auditoría."""
    queryset = TipoAuditoria.objects.all()
    serializer_class = TipoAuditoriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'descripcion']

