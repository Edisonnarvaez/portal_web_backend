from rest_framework import serializers
from ..models.terceros_paises import Pais

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = '__all__'
