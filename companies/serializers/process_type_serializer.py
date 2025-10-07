from rest_framework import serializers
from ..models.process_type import ProcessType

class ProcessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessType
        fields = '__all__'