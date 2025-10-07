from rest_framework import serializers
from gestionProveedores.models.etapa5_revision_contraloria import RevisionContraloria

class RevisionContraloriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionContraloria
        fields = '__all__'

