from rest_framework import serializers
from .models import SedeAuditada
from django.contrib.auth import get_user_model

User = get_user_model()

class SedeAuditadaSerializer(serializers.ModelSerializer):
    auditor = serializers.StringRelatedField(read_only=True)
    auditor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='auditor',
        write_only=True
    )

    class Meta:
        model = SedeAuditada
        fields = ['id', 'nombre', 'direccion', 'ciudad', 'pais', 'fecha_auditoria', 'auditor', 'auditor_id', 'observaciones']
