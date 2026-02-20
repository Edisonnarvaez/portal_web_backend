from rest_framework import serializers
from ..models.entidad_auditoria import EntidadAuditoria


class EntidadAuditoriaSerializer(serializers.ModelSerializer):
    tipo_entidad_display = serializers.CharField(source='get_tipo_entidad_display', read_only=True)
    auditorias_count = serializers.SerializerMethodField()

    class Meta:
        model = EntidadAuditoria
        fields = [
            'entidad_id', 'nombre', 'tipo_entidad', 'tipo_entidad_display',
            'contacto', 'telefono', 'email', 'activo', 'auditorias_count',
        ]

    def get_auditorias_count(self, obj):
        return obj.auditorias.count() if hasattr(obj, 'auditorias') else 0
