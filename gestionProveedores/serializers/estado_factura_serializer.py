from rest_framework import serializers
from ..models import Factura, EstadoFactura 

class EstadoFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoFactura
        fields = ['estado_id', 'nombre']  
