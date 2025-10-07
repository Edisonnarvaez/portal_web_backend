from rest_framework import serializers
from gestionProveedores.models.centro_operaciones import CentroOperaciones

class CentroOperacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentroOperaciones
        fields = '__all__'
