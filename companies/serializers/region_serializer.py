from rest_framework import serializers

from companies.models.parameters import Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'
