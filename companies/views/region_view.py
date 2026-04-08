from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from companies.models.parameters import Region
from companies.serializers.region_serializer import RegionSerializer


class RegionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
