from rest_framework import serializers
from gestionProveedores.models.etapa1_gestion_FE import GestionarFactura

class GestionarFESerializer(serializers.ModelSerializer):
    class Meta:
        model = GestionarFactura
        fields = '__all__'
