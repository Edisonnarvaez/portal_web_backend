from rest_framework import serializers
from ..models import Result

class ResultSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = Result
    #     fields = '__all__'
    class Meta:
        model = Result
        fields = [
            'id',
            'indicator',
            'indicator_id',
            'headquarters',
            'headquarters_id',
            'user',
            'numerator',
            'denominator',
            'calculatedValue',
            'creationDate',
            'updateDate',
            'year',
            'month',
            'quarter',
            'semester',
        ]
        read_only_fields = ['id', 'calculatedValue', 'creationDate', 'updateDate']