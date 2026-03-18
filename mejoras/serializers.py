"""
mejoras/serializers.py

Serializers para Planes de Mejora y Hallazgos.
Incluye serializers de listado, detalle, creación y estadísticas.
"""

from rest_framework import serializers
from .models import PlanMejora, Hallazgo, SoportePlan


# ═══════════════════════════════════════════════════════════════════
# SOPORTE DE PLAN - SERIALIZERS
# ═══════════════════════════════════════════════════════════════════

class SoportePlanSerializer(serializers.ModelSerializer):
    """Serializer para listar/detalle de soportes."""
    tipo_soporte_display = serializers.CharField(source='get_tipo_soporte_display', read_only=True)
    tamano_legible = serializers.CharField(read_only=True)
    extension = serializers.CharField(read_only=True)
    subido_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SoportePlan
        fields = [
            'id', 'plan_mejora', 'archivo', 'nombre_original',
            'tipo_soporte', 'tipo_soporte_display',
            'descripcion', 'tamano_bytes', 'tamano_legible', 'extension',
            'subido_por', 'subido_por_nombre', 'fecha_subida',
        ]

    def get_subido_por_nombre(self, obj):
        if obj.subido_por:
            nombre = f"{obj.subido_por.first_name} {obj.subido_por.last_name}".strip()
            return nombre or obj.subido_por.username
        return None


class SoportePlanUploadSerializer(serializers.ModelSerializer):
    """Serializer para subir soportes (multipart/form-data)."""

    class Meta:
        model = SoportePlan
        fields = [
            'id', 'plan_mejora', 'archivo',
            'tipo_soporte', 'descripcion',
        ]

    def validate_archivo(self, value):
        # Máximo 10 MB
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"El archivo excede el tamaño máximo de 10 MB. Tamaño: {value.size / (1024*1024):.1f} MB"
            )
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['subido_por'] = request.user
        archivo = validated_data.get('archivo')
        if archivo:
            validated_data['nombre_original'] = archivo.name
            validated_data['tamano_bytes'] = archivo.size
        return super().create(validated_data)


# ═══════════════════════════════════════════════════════════════════
# PLAN DE MEJORA - SERIALIZERS
# ═══════════════════════════════════════════════════════════════════

class PlanMejoraListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados."""
    origen_tipo_display = serializers.CharField(source='get_origen_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    criterio_codigo = serializers.CharField(source='criterio.codigo', read_only=True, default='')
    criterio_nombre = serializers.CharField(source='criterio.nombre', read_only=True, default='')
    autoevaluacion_numero = serializers.CharField(
        source='autoevaluacion.numero_autoevaluacion', read_only=True, default=''
    )
    auditoria_nombre = serializers.CharField(
        source='auditoria.auditoria_nombre', read_only=True, default=''
    )
    responsable_nombre = serializers.SerializerMethodField()
    esta_vencido = serializers.BooleanField(read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    proximo_a_vencer = serializers.BooleanField(read_only=True)
    hallazgos_count = serializers.SerializerMethodField()
    soportes_count = serializers.SerializerMethodField()

    class Meta:
        model = PlanMejora
        fields = [
            'id', 'numero_plan', 'descripcion',
            'origen_tipo', 'origen_tipo_display',
            'criterio_id', 'criterio_codigo', 'criterio_nombre',
            'autoevaluacion_id', 'autoevaluacion_numero',
            'auditoria_id', 'auditoria_nombre',
            'cumplimiento_id', 'resultado_indicador_id',
            'estado_cumplimiento_actual', 'objetivo_mejorado',
            'acciones_implementar',
            'responsable', 'responsable_nombre',
            'fecha_inicio', 'fecha_vencimiento', 'fecha_implementacion',
            'porcentaje_avance', 'estado', 'estado_display',
            'evidencia', 'observaciones',
            'esta_vencido', 'dias_restantes', 'proximo_a_vencer',
            'hallazgos_count', 'soportes_count',
            'fecha_creacion', 'fecha_actualizacion',
        ]

    def get_responsable_nombre(self, obj):
        if obj.responsable:
            nombre = f"{obj.responsable.first_name} {obj.responsable.last_name}".strip()
            return nombre or obj.responsable.username
        return None

    def get_hallazgos_count(self, obj):
        return obj.hallazgos.count()

    def get_soportes_count(self, obj):
        return obj.soportes.count()


class PlanMejoraDetailSerializer(PlanMejoraListSerializer):
    """Serializer completo para detalle, incluye hallazgos y soportes."""
    hallazgos = serializers.SerializerMethodField()
    soportes = SoportePlanSerializer(many=True, read_only=True)
    soportes_count = serializers.SerializerMethodField()
    origen_detalle = serializers.CharField(read_only=True)

    class Meta(PlanMejoraListSerializer.Meta):
        fields = PlanMejoraListSerializer.Meta.fields + [
            'hallazgos', 'soportes', 'soportes_count', 'origen_detalle',
        ]

    def get_hallazgos(self, obj):
        """Lista resumida de hallazgos asociados al plan."""
        from .serializers import HallazgoListSerializer
        return HallazgoListSerializer(obj.hallazgos.all(), many=True).data

    def get_soportes_count(self, obj):
        return obj.soportes.count()


class PlanMejoraCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar planes de mejora."""

    class Meta:
        model = PlanMejora
        fields = [
            'id',
            'numero_plan', 'descripcion',
            'origen_tipo',
            'cumplimiento', 'autoevaluacion', 'criterio',
            'auditoria', 'resultado_indicador',
            'estado_cumplimiento_actual', 'objetivo_mejorado',
            'acciones_implementar', 'responsable',
            'fecha_inicio', 'fecha_vencimiento', 'fecha_implementacion',
            'porcentaje_avance', 'estado',
            'evidencia', 'observaciones',
        ]

    def validate(self, data):
        """Validaciones de negocio."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_vencimiento = data.get('fecha_vencimiento')

        if fecha_inicio and fecha_vencimiento:
            if fecha_vencimiento <= fecha_inicio:
                raise serializers.ValidationError({
                    'fecha_vencimiento': 'La fecha de vencimiento debe ser posterior a la fecha de inicio.'
                })

        porcentaje = data.get('porcentaje_avance', 0)
        estado = data.get('estado', 'PENDIENTE')

        if estado == 'COMPLETADO' and porcentaje < 100:
            raise serializers.ValidationError({
                'porcentaje_avance': 'El porcentaje debe ser 100% para marcar como completado.'
            })

        # Validar coherencia origen_tipo ↔ FK
        origen = data.get('origen_tipo')
        if origen == 'HABILITACION' and not data.get('autoevaluacion'):
            raise serializers.ValidationError({
                'autoevaluacion': 'Se requiere autoevaluación para planes de origen HABILITACION.'
            })
        elif origen == 'AUDITORIA' and not data.get('auditoria'):
            raise serializers.ValidationError({
                'auditoria': 'Se requiere auditoría para planes de origen AUDITORIA.'
            })
        elif origen == 'INDICADOR' and not data.get('resultado_indicador'):
            raise serializers.ValidationError({
                'resultado_indicador': 'Se requiere resultado de indicador para planes de origen INDICADOR.'
            })

        return data


class PlanMejoraResumenSerializer(serializers.Serializer):
    """Serializer para el resumen/estadísticas de planes."""
    total_planes = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    en_curso = serializers.IntegerField()
    completados = serializers.IntegerField()
    vencidos = serializers.IntegerField()
    porcentaje_promedio_avance = serializers.FloatField()


# ═══════════════════════════════════════════════════════════════════
# HALLAZGO - SERIALIZERS
# ═══════════════════════════════════════════════════════════════════

class HallazgoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de hallazgos."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    severidad_display = serializers.CharField(source='get_severidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    origen_tipo_display = serializers.CharField(source='get_origen_tipo_display', read_only=True)
    criterio_codigo = serializers.CharField(source='criterio.codigo', read_only=True, default='')
    criterio_nombre = serializers.CharField(source='criterio.nombre', read_only=True, default='')
    plan_mejora_numero = serializers.CharField(
        source='plan_mejora.numero_plan', read_only=True, default=''
    )
    autoevaluacion_numero = serializers.CharField(
        source='autoevaluacion.numero_autoevaluacion', read_only=True, default=''
    )
    auditoria_nombre = serializers.CharField(
        source='auditoria.auditoria_nombre', read_only=True, default=''
    )

    class Meta:
        model = Hallazgo
        fields = [
            'id', 'numero_hallazgo', 'descripcion',
            'tipo', 'tipo_display',
            'severidad', 'severidad_display',
            'estado', 'estado_display',
            'origen_tipo', 'origen_tipo_display',
            'area_responsable',
            'autoevaluacion_id', 'autoevaluacion_numero',
            'datos_prestador_id',
            'auditoria_id', 'auditoria_nombre',
            'resultado_indicador_id',
            'criterio_id', 'criterio_codigo', 'criterio_nombre',
            'plan_mejora_id', 'plan_mejora_numero',
            'fecha_identificacion', 'fecha_cierre',
            'observaciones',
            'fecha_creacion', 'fecha_actualizacion',
        ]


class HallazgoDetailSerializer(HallazgoListSerializer):
    """Serializer completo para detalle de hallazgo."""
    origen_detalle = serializers.CharField(read_only=True)
    plan_mejora_detalle = serializers.SerializerMethodField()

    class Meta(HallazgoListSerializer.Meta):
        fields = HallazgoListSerializer.Meta.fields + [
            'origen_detalle', 'plan_mejora_detalle',
        ]

    def get_plan_mejora_detalle(self, obj):
        if obj.plan_mejora:
            return {
                'id': obj.plan_mejora.id,
                'numero_plan': obj.plan_mejora.numero_plan,
                'estado': obj.plan_mejora.estado,
                'porcentaje_avance': obj.plan_mejora.porcentaje_avance,
                'fecha_vencimiento': obj.plan_mejora.fecha_vencimiento,
            }
        return None


class HallazgoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar hallazgos."""

    class Meta:
        model = Hallazgo
        fields = [
            'id',
            'numero_hallazgo', 'descripcion',
            'tipo', 'severidad', 'estado',
            'origen_tipo',
            'area_responsable',
            'autoevaluacion', 'datos_prestador',
            'auditoria', 'resultado_indicador',
            'criterio', 'plan_mejora',
            'fecha_identificacion', 'fecha_cierre',
            'observaciones',
        ]

    def validate(self, data):
        estado = data.get('estado')
        fecha_cierre = data.get('fecha_cierre')

        if estado == 'CERRADO' and not fecha_cierre:
            raise serializers.ValidationError({
                'fecha_cierre': 'Se requiere fecha de cierre para cerrar un hallazgo.'
            })

        # Validar coherencia origen_tipo ↔ FK
        origen = data.get('origen_tipo')
        if origen == 'HABILITACION' and not data.get('autoevaluacion'):
            raise serializers.ValidationError({
                'autoevaluacion': 'Se requiere autoevaluación para hallazgos de origen HABILITACION.'
            })
        elif origen == 'AUDITORIA' and not data.get('auditoria'):
            raise serializers.ValidationError({
                'auditoria': 'Se requiere auditoría para hallazgos de origen AUDITORIA.'
            })
        elif origen == 'INDICADOR' and not data.get('resultado_indicador'):
            raise serializers.ValidationError({
                'resultado_indicador': 'Se requiere resultado de indicador para hallazgos de origen INDICADOR.'
            })

        return data


class EstadisticasHallazgosSerializer(serializers.Serializer):
    """Serializer para estadísticas de hallazgos."""
    total_hallazgos = serializers.IntegerField()
    fortalezas = serializers.IntegerField()
    oportunidades_mejora = serializers.IntegerField()
    no_conformidades = serializers.IntegerField()
    hallazgos = serializers.IntegerField()
    abiertos = serializers.IntegerField()
    en_seguimiento = serializers.IntegerField()
    cerrados = serializers.IntegerField()
    criticos = serializers.IntegerField()
