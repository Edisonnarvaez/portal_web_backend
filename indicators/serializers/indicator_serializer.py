from rest_framework import serializers
from ..models.indicator import Indicator

class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = '__all__'