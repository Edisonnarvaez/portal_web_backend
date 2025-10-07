from rest_framework import serializers
from gestionProveedores.models.factura_detalle import FacturaElectronicaDetalle

class FacturaElectronicaDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaElectronicaDetalle
        fields = '__all__'
