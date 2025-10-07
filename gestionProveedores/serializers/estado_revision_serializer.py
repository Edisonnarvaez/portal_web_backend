from rest_framework import serializers
from gestionProveedores.models.estado_revision import EstadoRevision

class EstadoRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoRevision
        fields = '__all__'
