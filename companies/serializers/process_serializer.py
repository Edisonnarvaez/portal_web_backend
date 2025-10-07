from rest_framework import serializers
from ..models.process import Process

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = '__all__'