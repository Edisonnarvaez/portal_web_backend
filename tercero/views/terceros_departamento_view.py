from rest_framework import viewsets
from ..models.terceros_departamentos import Departamento
from ..serializers.tercero_departamento_serializer import DepartamentoSerializer  


class DepartamentoViewSet(viewsets.ModelViewSet):
    serializer_class = DepartamentoSerializer

    def get_queryset(self):
        return Departamento.objects.filter(departamento_pais__pais_nombre='Colombia')





