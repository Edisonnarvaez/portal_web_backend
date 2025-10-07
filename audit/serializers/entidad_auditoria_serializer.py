from rest_framework import serializers
from ..models.auditoria import EntidadAuditoria 


class EntidadAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntidadAuditoria
        fields = '__all__'
