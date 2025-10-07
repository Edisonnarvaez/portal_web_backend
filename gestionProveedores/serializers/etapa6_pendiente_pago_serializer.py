from rest_framework import serializers
from gestionProveedores.models.etapa6_pendiente_pago import PendientePago

class PendientePagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendientePago
        fields = '__all__'

