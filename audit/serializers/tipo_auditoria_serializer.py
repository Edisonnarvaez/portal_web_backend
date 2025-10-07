from rest_framework import serializers
from ..models.auditoria import TipoAuditoria 


class TipoAuditoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAuditoria
        fields = '__all__'
