from rest_framework import viewsets
from ..models.terceros import Terceros
from ..serializers.tercero_serializers import TerceroSerializer

class TerceroViewSet(viewsets.ModelViewSet):
    queryset = Terceros.objects.all()
    serializer_class = TerceroSerializer




