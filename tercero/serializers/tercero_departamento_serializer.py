from rest_framework import serializers
from ..models.terceros_departamentos import Departamento  


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'
