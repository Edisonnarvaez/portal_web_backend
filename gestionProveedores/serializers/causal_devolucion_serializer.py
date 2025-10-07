from rest_framework import serializers
from gestionProveedores.models.causal_devolucion import CausalDevolucion

class CausalDevolucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CausalDevolucion
        fields = '__all__'
