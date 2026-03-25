from rest_framework import serializers

from ..models import DatosPrestador, ServicioSede


class ServicioSedeListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de ServicioSede."""

    prestador_codigo = serializers.CharField(
        source='prestador.codigo_reps',
        read_only=True,
    )
    prestador_headquarters = serializers.CharField(
        source='prestador.headquarters.name',
        read_only=True,
    )
    modalidad_display = serializers.CharField(
        source='get_modalidad_display',
        read_only=True,
    )
    complejidad_display = serializers.CharField(
        source='get_complejidad_display',
        read_only=True,
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True,
    )
    vencido = serializers.SerializerMethodField()

    class Meta:
        model = ServicioSede
        fields = [
            'id',
            'codigo_servicio',
            'nombre_servicio',
            'prestador_codigo',
            'prestador_headquarters',
            'modalidad',
            'modalidad_display',
            'complejidad',
            'complejidad_display',
            'estado_habilitacion',
            'estado_display',
            'fecha_vencimiento',
            'vencido',
        ]
        read_only_fields = fields

    def get_vencido(self, obj):
        return obj.esta_vencido()


class ServicioSedeDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para ServicioSede."""

    prestador_id = serializers.PrimaryKeyRelatedField(
        queryset=DatosPrestador.objects.all(),
        source='prestador',
        write_only=True,
    )
    prestador_detail = serializers.SerializerMethodField()
    modalidad_display = serializers.CharField(
        source='get_modalidad_display',
        read_only=True,
    )
    complejidad_display = serializers.CharField(
        source='get_complejidad_display',
        read_only=True,
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True,
    )
    vencido = serializers.SerializerMethodField()
    dias_vencimiento = serializers.SerializerMethodField()

    class Meta:
        model = ServicioSede
        fields = [
            'id',
            'codigo_servicio',
            'nombre_servicio',
            'descripcion',
            'prestador_id',
            'prestador_detail',
            'modalidad',
            'modalidad_display',
            'complejidad',
            'complejidad_display',
            'estado_habilitacion',
            'estado_display',
            'fecha_habilitacion',
            'fecha_vencimiento',
            'vencido',
            'dias_vencimiento',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'fecha_creacion',
            'fecha_actualizacion',
            'prestador_detail',
            'vencido',
            'dias_vencimiento',
        ]

    def get_prestador_detail(self, obj):
        return {
            'id': obj.prestador.id,
            'codigo_reps': obj.prestador.codigo_reps,
            'nombre_prestador': obj.prestador.nombre_prestador,
            'headquarters': obj.prestador.headquarters.name,
            'estado_habilitacion': obj.prestador.get_estado_habilitacion_display(),
        }

    def get_vencido(self, obj):
        return obj.esta_vencido()

    def get_dias_vencimiento(self, obj):
        return obj.dias_para_vencimiento()
