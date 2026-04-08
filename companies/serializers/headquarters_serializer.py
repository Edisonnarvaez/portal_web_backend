from companies.serializers.company_serializer import CompanySerializer
from rest_framework import serializers
from companies.models.headquarters import Headquarters


class HeadquartersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Headquarters
        #fields = ['id', 'habilitationCode','name', 'company', 'departament', 'city', 'address', 'habilitationDate', 'closingDate', 'status']
        fields = '__all__'

    def validate(self, attrs):
        region = attrs.get('region', getattr(self.instance, 'region', None))
        municipality = attrs.get('municipality', getattr(self.instance, 'municipality', None))

        if region and municipality and municipality.region_id != region.id:
            raise serializers.ValidationError(
                {'municipality': 'El municipio seleccionado no pertenece a la region elegida.'}
            )

        return attrs

