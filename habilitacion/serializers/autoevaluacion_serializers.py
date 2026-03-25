from rest_framework import serializers

from ..models import Autoevaluacion, DatosPrestador


class AutoevaluacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de Autoevaluacion."""

    prestador_codigo = serializers.CharField(
        source='datos_prestador.codigo_reps',
        read_only=True,
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True,
    )
    porcentaje_cumplimiento = serializers.SerializerMethodField()

    class Meta:
        model = Autoevaluacion
        fields = [
            'id',
            'numero_autoevaluacion',
            'prestador_codigo',
            'periodo',
            'version',
            'estado',
            'estado_display',
            'fecha_inicio',
            'fecha_completacion',
            'porcentaje_cumplimiento',
        ]
        read_only_fields = fields

    def get_porcentaje_cumplimiento(self, obj):
        return round(obj.porcentaje_cumplimiento(), 2)


class AutoevaluacionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Autoevaluacion."""

    datos_prestador_id = serializers.PrimaryKeyRelatedField(
        queryset=DatosPrestador.objects.all(),
        source='datos_prestador',
        write_only=True,
    )
    datos_prestador_detail = serializers.SerializerMethodField()
    usuario_responsable_detail = serializers.SerializerMethodField()
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True,
    )
    porcentaje_cumplimiento = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()
    total_cumplimientos = serializers.SerializerMethodField()
    cumplimientos_data = serializers.SerializerMethodField()

    planes_mejora_count = serializers.SerializerMethodField()
    hallazgos_count = serializers.SerializerMethodField()
    mejoras_resumen = serializers.SerializerMethodField()

    class Meta:
        model = Autoevaluacion
        fields = [
            'id',
            'numero_autoevaluacion',
            'datos_prestador_id',
            'datos_prestador_detail',
            'periodo',
            'version',
            'estado',
            'estado_display',
            'fecha_inicio',
            'fecha_completacion',
            'fecha_vencimiento',
            'vigente',
            'usuario_responsable_detail',
            'observaciones',
            'porcentaje_cumplimiento',
            'total_cumplimientos',
            'cumplimientos_data',
            'planes_mejora_count',
            'hallazgos_count',
            'mejoras_resumen',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'fecha_creacion',
            'fecha_actualizacion',
            'numero_autoevaluacion',
            'datos_prestador_detail',
            'usuario_responsable_detail',
            'porcentaje_cumplimiento',
            'vigente',
            'total_cumplimientos',
            'cumplimientos_data',
            'planes_mejora_count',
            'hallazgos_count',
            'mejoras_resumen',
        ]

    def get_datos_prestador_detail(self, obj):
        return {
            'id': obj.datos_prestador.id,
            'nombre_prestador': obj.datos_prestador.nombre_prestador,
            'codigo_reps': obj.datos_prestador.codigo_reps,
            'company_name': obj.datos_prestador.headquarters.company.name,
        }

    def get_usuario_responsable_detail(self, obj):
        if not obj.usuario_responsable:
            return None
        return {
            'id': obj.usuario_responsable.id,
            'username': obj.usuario_responsable.username,
            'email': obj.usuario_responsable.email,
        }

    def get_porcentaje_cumplimiento(self, obj):
        return round(obj.porcentaje_cumplimiento(), 2)

    def get_vigente(self, obj):
        return obj.esta_vigente()

    def get_total_cumplimientos(self, obj):
        return obj.cumplimientos.count()

    def get_cumplimientos_data(self, obj):
        cumplimientos = obj.cumplimientos.all()
        return {
            'total': cumplimientos.count(),
            'cumple': cumplimientos.filter(cumple='CUMPLE').count(),
            'no_cumple': cumplimientos.filter(cumple='NO_CUMPLE').count(),
            'parcialmente': cumplimientos.filter(cumple='PARCIALMENTE').count(),
            'no_aplica': cumplimientos.filter(cumple='NO_APLICA').count(),
        }

    def get_planes_mejora_count(self, obj):
        from mejoras.models import PlanMejora

        return PlanMejora.objects.filter(autoevaluacion=obj).count()

    def get_hallazgos_count(self, obj):
        from mejoras.models import Hallazgo

        return Hallazgo.objects.filter(autoevaluacion=obj).count()

    def get_mejoras_resumen(self, obj):
        from mejoras.models import Hallazgo, PlanMejora

        planes = PlanMejora.objects.filter(autoevaluacion=obj)
        hallazgos = Hallazgo.objects.filter(autoevaluacion=obj)
        return {
            'total_planes': planes.count(),
            'planes_pendientes': planes.filter(estado='PENDIENTE').count(),
            'planes_en_curso': planes.filter(estado='EN_CURSO').count(),
            'planes_completados': planes.filter(estado='COMPLETADO').count(),
            'total_hallazgos': hallazgos.count(),
            'hallazgos_abiertos': hallazgos.filter(estado='ABIERTO').count(),
            'hallazgos_cerrados': hallazgos.filter(estado='CERRADO').count(),
        }
