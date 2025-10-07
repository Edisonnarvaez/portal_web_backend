from rest_framework import serializers
from gestionProveedores.models.estado_impuestos import EstadoImpuestos

class EstadoImpuestosSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoImpuestos
        fields = '__all__'
