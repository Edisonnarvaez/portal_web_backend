from rest_framework import viewsets
from companies.models.headquarters import Headquarters
from companies.serializers.headquarters_serializer import HeadquartersSerializer
from rest_framework.permissions import IsAuthenticated


class HeadquartersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Headquarters.objects.select_related('company').all()
    serializer_class = HeadquartersSerializer