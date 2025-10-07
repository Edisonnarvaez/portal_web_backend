from rest_framework import serializers
from ..models.terceros_municipios import Municipio  

class MunicipioSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Municipio
        fields = '__all__'
