from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from companies.models.parameters import Municipality
from companies.serializers.municipality_serializer import MunicipalitySerializer


class MunicipalityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Municipality.objects.select_related('region').all()
    serializer_class = MunicipalitySerializer

    def get_queryset(self):
        queryset = Municipality.objects.select_related('region').all()
        region_id = self.request.query_params.get('region') or self.request.query_params.get('region_id')
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        return queryset
