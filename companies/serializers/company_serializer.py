from rest_framework import serializers
from companies.models.company import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'nit', 'legalRepresentative', 'phone', 'address', 'contactEmail', 'foundationDate', 'status']

    def validate_nit(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("El NIT debe contener solo números.")
        return value
