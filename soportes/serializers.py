from rest_framework import serializers

from .models import (
    CategoriaSoporte,
    SoporteDocumental,
    SoporteRequerido,
    TipoDocumentoSoporte,
)


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
    # ✅ CAMPOS READ-ONLY PARA INFORMACIÓN RELACIONADA
    tipo_nombre = serializers.ReadOnlyField(source='tipo_documento.nombre')
    prestador_nombre = serializers.ReadOnlyField(source='prestador.nombre_prestador')
    empresa_nombre = serializers.ReadOnlyField(source='empresa.name')
    sede_nombre = serializers.ReadOnlyField(source='sede.name')
    servicio_nombre = serializers.ReadOnlyField(source='servicio.nombre')

    class Meta:
        model = SoporteDocumental
        fields = [
            'id',
            'prestador',
            'prestador_nombre',
            'nivel',
            'empresa',
            'empresa_nombre',
            'sede',
            'sede_nombre',
            'servicio',
            'servicio_nombre',
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
        read_only_fields = [
            'version',
            'fecha_carga',
            'prestador_nombre',
            'empresa_nombre',
            'sede_nombre',
            'servicio_nombre',
            'tipo_nombre',
        ]

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


class SoporteRequeridoSerializer(serializers.ModelSerializer):
    # ✅ CAMPOS READ-ONLY PARA INFORMACIÓN RELACIONADA
    prestador_nombre = serializers.ReadOnlyField(source='prestador.nombre_prestador')
    tipo_nombre = serializers.ReadOnlyField(source='tipo_documento.nombre')
    empresa_nombre = serializers.ReadOnlyField(source='empresa.name')
    sede_nombre = serializers.ReadOnlyField(source='sede.name')
    servicio_nombre = serializers.ReadOnlyField(source='servicio.nombre')
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = SoporteRequerido
        fields = [
            'id',
            'prestador',
            'prestador_nombre',
            'empresa',
            'empresa_nombre',
            'sede',
            'sede_nombre',
            'servicio',
            'servicio_nombre',
            'tipo_documento',
            'tipo_nombre',
            'estado',
            'estado_display',
        ]
        read_only_fields = [
            'prestador_nombre',
            'empresa_nombre',
            'sede_nombre',
            'servicio_nombre',
            'tipo_nombre',
            'estado_display',
        ]
