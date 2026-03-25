from rest_framework import serializers

from ..models import (
    CapacidadInstalada,
    MedidaSeguridadServicio,
    NovedadREPS,
    RequisitoDocumental,
    SancionServicio,
)


class CapacidadInstaladaSerializer(serializers.ModelSerializer):
    tipo_capacidad_display = serializers.CharField(
        source='get_tipo_capacidad_display',
        read_only=True,
    )

    class Meta:
        model = CapacidadInstalada
        fields = [
            'id',
            'servicio_sede',
            'tipo_capacidad',
            'tipo_capacidad_display',
            'subtipo',
            'cantidad',
            'unidad',
            'observaciones',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class MedidaSeguridadServicioSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = MedidaSeguridadServicio
        fields = [
            'id',
            'servicio_sede',
            'norma_referencia',
            'descripcion',
            'estado',
            'estado_display',
            'fecha_inicio',
            'fecha_fin',
            'autoridad',
            'observaciones',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class SancionServicioSerializer(serializers.ModelSerializer):
    tipo_sancion_display = serializers.CharField(source='get_tipo_sancion_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = SancionServicio
        fields = [
            'id',
            'servicio_sede',
            'norma_referencia',
            'tipo_sancion',
            'tipo_sancion_display',
            'estado',
            'estado_display',
            'acto_administrativo',
            'autoridad',
            'fecha_inicio',
            'fecha_fin',
            'descripcion',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class NovedadREPSSerializer(serializers.ModelSerializer):
    tipo_novedad_display = serializers.CharField(source='get_tipo_novedad_display', read_only=True)
    subtipo_novedad_display = serializers.CharField(source='get_subtipo_novedad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = NovedadREPS
        fields = [
            'id',
            'codigo_novedad',
            'tipo_novedad',
            'tipo_novedad_display',
            'subtipo_novedad',
            'subtipo_novedad_display',
            'estado',
            'estado_display',
            'datos_prestador',
            'sede',
            'servicio_sede',
            'requiere_visita_previa',
            'fecha_radicacion',
            'descripcion',
            'observaciones',
            'creado_por',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'creado_por']


class RequisitoDocumentalSerializer(serializers.ModelSerializer):
    tipo_tramite_display = serializers.CharField(source='get_tipo_tramite_display', read_only=True)

    class Meta:
        model = RequisitoDocumental
        fields = [
            'id',
            'codigo',
            'nombre',
            'tipo_tramite',
            'tipo_tramite_display',
            'descripcion',
            'obligatorio',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
