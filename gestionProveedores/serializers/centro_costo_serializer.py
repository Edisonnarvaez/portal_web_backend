from rest_framework import serializers
from gestionProveedores.models.centro_costo import CentroCostos

class CentroCostosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentroCostos
        fields = '__all__'
