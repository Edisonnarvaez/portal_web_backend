from rest_framework import serializers

from companies.models import Headquarters

from ..models import DatosPrestador


class DatosPrestadorListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de DatosPrestador."""

    company_name = serializers.CharField(
        source='headquarters.company.name',
        read_only=True,
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True,
    )
    proxima_vencer = serializers.SerializerMethodField()
    dias_vencimiento = serializers.SerializerMethodField()

    class Meta:
        model = DatosPrestador
        fields = [
            'id',
            'codigo_reps',
            'company_name',
            'clase_prestador',
            'estado_habilitacion',
            'estado_display',
            'fecha_vencimiento_habilitacion',
            'proxima_vencer',
            'dias_vencimiento',
        ]
        read_only_fields = fields

    def get_proxima_vencer(self, obj):
        """Esta proxima a vencer?"""
        return obj.esta_proxima_a_vencer(dias=90)

    def get_dias_vencimiento(self, obj):
        """Dias restantes para vencimiento."""
        return obj.dias_para_vencimiento()


class DatosPrestadorDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para DatosPrestador con validaciones."""

    headquarters_id = serializers.PrimaryKeyRelatedField(
        queryset=Headquarters.objects.all(),
        source='headquarters',
        write_only=True,
    )
    company_detail = serializers.SerializerMethodField()
    headquarters_detail = serializers.SerializerMethodField()
    clase_prestador_display = serializers.CharField(
        source='get_clase_prestador_display',
        read_only=True,
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True,
    )

    dias_vencimiento = serializers.SerializerMethodField()
    proxima_vencer = serializers.SerializerMethodField()
    vencida = serializers.SerializerMethodField()
    autoevaluaciones_count = serializers.SerializerMethodField()

    class Meta:
        model = DatosPrestador
        fields = [
            'id',
            'codigo_reps',
            'headquarters_id',
            'company_detail',
            'headquarters_detail',
            'nombre_prestador',
            'sede_principal',
            'clase_prestador',
            'clase_prestador_display',
            'estado_habilitacion',
            'estado_display',
            'fecha_inscripcion',
            'fecha_renovacion',
            'fecha_vencimiento_habilitacion',
            'dias_vencimiento',
            'proxima_vencer',
            'vencida',
            'aseguradora_pep',
            'numero_poliza',
            'vigencia_poliza',
            'autoevaluaciones_count',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'fecha_creacion',
            'fecha_actualizacion',
            'company_detail',
            'headquarters_detail',
            'dias_vencimiento',
            'proxima_vencer',
            'vencida',
            'autoevaluaciones_count',
        ]

    def get_company_detail(self, obj):
        company = obj.headquarters.company
        return {
            'id': company.id,
            'name': company.name,
            'nit': getattr(company, 'nit', None),
        }

    def get_headquarters_detail(self, obj):
        hq = obj.headquarters
        return {
            'id': hq.id,
            'name': hq.name,
            'habilitationCode': hq.habilitationCode,
        }

    def get_dias_vencimiento(self, obj):
        return obj.dias_para_vencimiento()

    def get_proxima_vencer(self, obj):
        return obj.esta_proxima_a_vencer(dias=90)

    def get_vencida(self, obj):
        return obj.esta_vencida()

    def get_autoevaluaciones_count(self, obj):
        return obj.autoevaluaciones.count()

    def validate_codigo_reps(self, value):
        if not value or len(value) < 5:
            raise serializers.ValidationError(
                'El codigo REPS debe tener al menos 5 caracteres.'
            )
        return value
