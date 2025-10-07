from rest_framework import serializers
from gestionProveedores.models.etapa3_pendiente_reconocimiento_contable import PendienteReconocimientoContable

class PendienteReconocimientoContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendienteReconocimientoContable
        fields = '__all__'

