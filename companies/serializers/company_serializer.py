from rest_framework import serializers
from companies.models.company import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

    def validate(self, attrs):
        region = attrs.get('region', getattr(self.instance, 'region', None))
        municipality = attrs.get('municipality', getattr(self.instance, 'municipality', None))

        # Ensure municipality always belongs to the selected region.
        if region and municipality and municipality.region_id != region.id:
            raise serializers.ValidationError(
                {'municipality': 'El municipio seleccionado no pertenece a la region elegida.'}
            )

        type_document = attrs.get('type_document', getattr(self.instance, 'type_document', None))
        number_document = attrs.get('number_document', getattr(self.instance, 'number_document', None))
        if type_document == 'NIT' and number_document and not number_document.isdigit():
            raise serializers.ValidationError(
                {'number_document': 'El NIT debe contener solo numeros.'}
            )

        return attrs
