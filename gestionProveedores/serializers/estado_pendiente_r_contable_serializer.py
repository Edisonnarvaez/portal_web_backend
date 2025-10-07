from rest_framework import serializers
from gestionProveedores.models.estado_pendiente_r_contable import EstadoPendienteRContable

class EstadoPendienteRContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoPendienteRContable
        fields = '__all__'
