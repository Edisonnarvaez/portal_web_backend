from companies.serializers.company_serializer import CompanySerializer
from rest_framework import serializers
from companies.models.headquarters import Headquarters

class HeadquartersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Headquarters
        #fields = ['id', 'habilitationCode','name', 'company', 'departament', 'city', 'address', 'habilitationDate', 'closingDate', 'status']
        fields = '__all__'

