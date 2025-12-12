"""
normativity/serializers.py

Serializers para los modelos maestros de normativity.
"""

from rest_framework import serializers
from .models import Estandar, Criterio, DocumentoNormativo


class CriterioSerializer(serializers.ModelSerializer):
    """Serializer para Criterios con validaciones."""
    
    estandar_display = serializers.CharField(
        source='estandar.get_codigo_display',
        read_only=True,
        label="Estándar"
    )
    complejidad_display = serializers.CharField(
        source='get_complejidad_display',
        read_only=True
    )
    
    class Meta:
        model = Criterio
        fields = [
            'id',
            'estandar',
            'estandar_display',
            'codigo',
            'nombre',
            'descripcion',
            'complejidad',
            'complejidad_display',
            'aplica_todos',
            'es_mandatorio',
            'requiere_evidencia_documental',
            'notas_interpretacion',
            'estado',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def validate_codigo(self, value):
        """Validar que el código siga el formato esperado."""
        if not value or '.' not in value:
            raise serializers.ValidationError(
                "El código debe seguir el formato: N.N (ej: 1.1, 2.3)"
            )
        return value


class EstandarSerializer(serializers.ModelSerializer):
    """Serializer para Estándares con criterios anidados."""
    
    criterios = CriterioSerializer(many=True, read_only=True)
    codigo_display = serializers.CharField(
        source='get_codigo_display',
        read_only=True
    )
    
    class Meta:
        model = Estandar
        fields = [
            'id',
            'codigo',
            'codigo_display',
            'nombre',
            'descripcion',
            'estado',
            'version_resolucion',
            'criterios',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class EstandarListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar Estándares (sin criterios anidados)."""
    
    codigo_display = serializers.CharField(
        source='get_codigo_display',
        read_only=True
    )
    criterios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Estandar
        fields = [
            'id',
            'codigo',
            'codigo_display',
            'nombre',
            'estado',
            'criterios_count',
        ]
    
    def get_criterios_count(self, obj):
        return obj.criterios.filter(estado=True).count()


class DocumentoNormativoSerializer(serializers.ModelSerializer):
    """Serializer para Documentos Normativos."""
    
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )
    criterios_relacionados = CriterioSerializer(
        many=True,
        read_only=True
    )
    
    class Meta:
        model = DocumentoNormativo
        fields = [
            'id',
            'titulo',
            'tipo',
            'tipo_display',
            'numero_referencia',
            'fecha_publicacion',
            'url_documento',
            'descripcion',
            'criterios_relacionados',
        ]
        read_only_fields = ['id']
