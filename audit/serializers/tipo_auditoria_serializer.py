from rest_framework import serializers
from ..models.tipo_auditoria import TipoAuditoria


class TipoAuditoriaSerializer(serializers.ModelSerializer):
    auditorias_count = serializers.SerializerMethodField()

    class Meta:
        model = TipoAuditoria
        fields = ['tipo_id', 'nombre', 'descripcion', 'requiere_entidad_externa', 'activo', 'auditorias_count']

    def get_auditorias_count(self, obj):
        return obj.auditorias.count() if hasattr(obj, 'auditorias') else 0
