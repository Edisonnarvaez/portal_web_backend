from rest_framework import serializers

from ..models import ChecklistItem, ChecklistVerificacion, EvidenciaChecklist
from .catalogo_serializers import RequisitoDocumentalSerializer


class EvidenciaChecklistSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = EvidenciaChecklist
        fields = [
            'id',
            'checklist_item',
            'tipo',
            'tipo_display',
            'nombre',
            'archivo',
            'hash_integridad',
            'subido_por',
            'fecha_subida',
        ]
        read_only_fields = ['id', 'fecha_subida', 'subido_por']


class ChecklistItemSerializer(serializers.ModelSerializer):
    requisito_detail = RequisitoDocumentalSerializer(source='requisito', read_only=True)
    evidencias = EvidenciaChecklistSerializer(many=True, read_only=True)

    class Meta:
        model = ChecklistItem
        fields = [
            'id',
            'checklist',
            'requisito',
            'requisito_detail',
            'obligatorio',
            'cumple',
            'observaciones',
            'verificado_por',
            'fecha_verificacion',
            'evidencias',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'verificado_por']


class ChecklistVerificacionSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    items = ChecklistItemSerializer(many=True, read_only=True)

    class Meta:
        model = ChecklistVerificacion
        fields = [
            'id',
            'codigo_checklist',
            'estado',
            'estado_display',
            'novedad',
            'servicio_sede',
            'responsable',
            'fecha_cierre',
            'observaciones',
            'items',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'responsable']
