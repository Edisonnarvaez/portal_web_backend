from rest_framework import viewsets
from ..models.terceros_paises import Pais
from ..serializers.tercero_paises_serializer import PaisSerializer

class PaisViewSet(viewsets.ModelViewSet):
    serializer_class = PaisSerializer

    def get_queryset(self):
        return Pais.objects.filter(pais_nombre='Colombia')



