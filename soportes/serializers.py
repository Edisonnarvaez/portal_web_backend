from rest_framework import serializers

from .models import CategoriaSoporte, SoporteDocumental, TipoDocumentoSoporte


class CategoriaSoporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaSoporte
        fields = '__all__'


class TipoDocumentoSoporteSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = TipoDocumentoSoporte
        fields = '__all__'


class SoporteDocumentalSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.ReadOnlyField(source='tipo_documento.nombre')

    class Meta:
        model = SoporteDocumental
        fields = [
            'id',
            'nivel',
            'empresa',
            'sede',
            'servicio',
            'tipo_documento',
            'tipo_nombre',
            'archivo',
            'fecha_emision',
            'fecha_vencimiento',
            'version',
            'es_vigente',
            'fecha_carga',
            'observaciones',
        ]
        read_only_fields = ['version', 'fecha_carga']

    def validate(self, data):
        tipo = data.get('tipo_documento')
        nivel = data.get('nivel')

        if tipo and nivel:
            if tipo.nivel_aplica != nivel:
                raise serializers.ValidationError(
                    f'Este documento aplica a nivel {tipo.nivel_aplica}'
                )

            if tipo.requiere_vencimiento and not data.get('fecha_vencimiento'):
                raise serializers.ValidationError(
                    {'fecha_vencimiento': 'Este documento requiere fecha de vencimiento'}
                )

        return data
