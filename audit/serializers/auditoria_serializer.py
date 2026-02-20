"""
audit/serializers/auditoria_serializer.py

Serializers completos para el ciclo de vida de auditorías.
"""
from rest_framework import serializers
from ..models import (
    Auditoria,
    MiembroEquipoAuditor,
    HallazgoAuditoria,
    ActaReunion,
    ProgramaAuditoria,
)


# ═══════════════════════════════════════════════════════════════════
# EQUIPO AUDITOR
# ═══════════════════════════════════════════════════════════════════

class MiembroEquipoSerializer(serializers.ModelSerializer):
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = MiembroEquipoAuditor
        fields = [
            'id', 'auditoria', 'usuario', 'usuario_nombre',
            'rol', 'rol_display', 'area_responsable',
        ]

    def get_usuario_nombre(self, obj):
        nombre = f"{obj.usuario.first_name} {obj.usuario.last_name}".strip()
        return nombre or obj.usuario.username


# ═══════════════════════════════════════════════════════════════════
# HALLAZGO DE AUDITORÍA
# ═══════════════════════════════════════════════════════════════════

class HallazgoAuditoriaListSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    auditoria_nombre = serializers.CharField(source='auditoria.auditoria_nombre', read_only=True)
    responsable_nombre = serializers.SerializerMethodField()
    esta_vencido = serializers.BooleanField(read_only=True)

    class Meta:
        model = HallazgoAuditoria
        fields = [
            'id', 'auditoria', 'auditoria_nombre',
            'numero', 'tipo', 'tipo_display',
            'criterio_norma', 'descripcion',
            'estado', 'estado_display',
            'responsable_accion', 'responsable_nombre',
            'fecha_limite_accion', 'esta_vencido',
            'hallazgo_mejora', 'plan_mejora',
            'fecha_creacion',
        ]

    def get_responsable_nombre(self, obj):
        if obj.responsable_accion:
            nombre = f"{obj.responsable_accion.first_name} {obj.responsable_accion.last_name}".strip()
            return nombre or obj.responsable_accion.username
        return None


class HallazgoAuditoriaDetailSerializer(HallazgoAuditoriaListSerializer):
    proceso_nombre = serializers.CharField(
        source='proceso_afectado.name', read_only=True, default=''
    )

    class Meta(HallazgoAuditoriaListSerializer.Meta):
        fields = HallazgoAuditoriaListSerializer.Meta.fields + [
            'evidencia_objetiva', 'proceso_afectado', 'proceso_nombre',
            'fecha_verificacion', 'fecha_actualizacion',
        ]


class HallazgoAuditoriaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HallazgoAuditoria
        fields = [
            'id', 'auditoria', 'numero', 'tipo',
            'criterio_norma', 'descripcion', 'evidencia_objetiva',
            'proceso_afectado', 'responsable_accion',
            'estado', 'fecha_limite_accion', 'fecha_verificacion',
            'hallazgo_mejora', 'plan_mejora',
        ]


# ═══════════════════════════════════════════════════════════════════
# ACTA DE REUNIÓN
# ═══════════════════════════════════════════════════════════════════

class ActaReunionSerializer(serializers.ModelSerializer):
    tipo_acta_display = serializers.CharField(source='get_tipo_acta_display', read_only=True)

    class Meta:
        model = ActaReunion
        fields = [
            'id', 'auditoria', 'tipo_acta', 'tipo_acta_display',
            'fecha', 'lugar', 'asistentes',
            'temas_tratados', 'compromisos', 'observaciones',
            'fecha_creacion',
        ]


# ═══════════════════════════════════════════════════════════════════
# AUDITORÍA
# ═══════════════════════════════════════════════════════════════════

class AuditoriaListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados."""
    fase_display = serializers.CharField(source='get_fase_display', read_only=True)
    clasificacion_display = serializers.CharField(source='get_clasificacion_display', read_only=True)
    tipo_nombre = serializers.CharField(source='auditoria_tipo.nombre', read_only=True, default='')
    entidad_nombre = serializers.CharField(source='auditoria_entidad.nombre', read_only=True, default='')
    proceso_nombre = serializers.CharField(source='auditoria_proceso.name', read_only=True, default='')
    sede_nombre = serializers.CharField(source='sede.name', read_only=True, default='')
    auditor_lider_nombre = serializers.SerializerMethodField()
    esta_activa = serializers.BooleanField(read_only=True)
    total_hallazgos = serializers.IntegerField(read_only=True)
    dias_para_ejecucion = serializers.IntegerField(read_only=True)

    class Meta:
        model = Auditoria
        fields = [
            'auditoria_id', 'auditoria_nombre',
            'clasificacion', 'clasificacion_display',
            'auditoria_tipo', 'tipo_nombre',
            'auditoria_entidad', 'entidad_nombre',
            'auditoria_proceso', 'proceso_nombre',
            'sede', 'sede_nombre',
            'fase', 'fase_display',
            'auditoria_estado',
            'fecha_programada',
            'auditoria_fecha_notificacion',
            'fecha_inicio_ejecucion',
            'auditoria_fecha_auditoria',
            'auditor_lider', 'auditor_lider_nombre',
            'auditoria_responsable',
            'esta_activa', 'total_hallazgos',
            'dias_para_ejecucion',
            'fecha_creacion',
        ]

    def get_auditor_lider_nombre(self, obj):
        if obj.auditor_lider:
            nombre = f"{obj.auditor_lider.first_name} {obj.auditor_lider.last_name}".strip()
            return nombre or obj.auditor_lider.username
        return None


class AuditoriaDetailSerializer(AuditoriaListSerializer):
    """Serializer completo con relaciones anidadas."""
    equipo_auditor = MiembroEquipoSerializer(many=True, read_only=True)
    hallazgos_auditoria = HallazgoAuditoriaListSerializer(many=True, read_only=True)
    actas = ActaReunionSerializer(many=True, read_only=True)
    duracion_dias = serializers.IntegerField(read_only=True)
    total_no_conformidades = serializers.IntegerField(read_only=True)
    transiciones_permitidas = serializers.SerializerMethodField()
    auditoria_relacionada_nombre = serializers.CharField(
        source='auditoria_relacionada.auditoria_nombre', read_only=True, default=''
    )

    class Meta(AuditoriaListSerializer.Meta):
        fields = AuditoriaListSerializer.Meta.fields + [
            'auditoria_detalle', 'norma_referencia',
            'fecha_informe', 'fecha_cierre',
            'conclusion', 'recomendaciones',
            'auditoria_relacionada', 'auditoria_relacionada_nombre',
            'creado_por',
            'equipo_auditor',
            'hallazgos_auditoria',
            'actas',
            'duracion_dias', 'total_no_conformidades',
            'transiciones_permitidas',
            'fecha_actualizacion',
        ]

    def get_transiciones_permitidas(self, obj):
        return obj._transiciones_permitidas()


class AuditoriaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar auditorías."""

    class Meta:
        model = Auditoria
        fields = [
            'auditoria_id',
            'auditoria_nombre', 'auditoria_detalle',
            'clasificacion',
            'auditoria_tipo', 'auditoria_entidad',
            'auditoria_proceso', 'sede',
            'norma_referencia',
            'fase', 'auditoria_estado',
            'fecha_programada', 'auditoria_fecha_notificacion',
            'fecha_inicio_ejecucion', 'auditoria_fecha_auditoria',
            'fecha_informe', 'fecha_cierre',
            'auditor_lider', 'auditoria_responsable',
            'conclusion', 'recomendaciones',
            'auditoria_relacionada',
        ]

    def validate(self, data):
        clasificacion = data.get('clasificacion', 'INTERNA')
        if clasificacion == 'EXTERNA' and not data.get('auditoria_entidad'):
            tipo = data.get('auditoria_tipo')
            if tipo and tipo.requiere_entidad_externa:
                raise serializers.ValidationError({
                    'auditoria_entidad': 'Se requiere entidad auditora para auditorías externas de este tipo.'
                })
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['creado_por'] = request.user
        return super().create(validated_data)


class CambiarFaseSerializer(serializers.Serializer):
    """Serializer para cambiar la fase de una auditoría."""
    nueva_fase = serializers.ChoiceField(choices=Auditoria.Fase.choices)

    def validate_nueva_fase(self, value):
        auditoria = self.context.get('auditoria')
        if auditoria and not auditoria.puede_avanzar_a(value):
            raise serializers.ValidationError(
                f"No se puede avanzar de '{auditoria.get_fase_display()}' a '{value}'. "
                f"Transiciones permitidas: {auditoria._transiciones_permitidas()}"
            )
        return value


# ═══════════════════════════════════════════════════════════════════
# PROGRAMA DE AUDITORÍA
# ═══════════════════════════════════════════════════════════════════

class ProgramaAuditoriaListSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    total_auditorias = serializers.IntegerField(read_only=True)
    avance_porcentaje = serializers.FloatField(read_only=True)
    responsable_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ProgramaAuditoria
        fields = [
            'id', 'nombre', 'periodo', 'descripcion',
            'estado', 'estado_display',
            'responsable', 'responsable_nombre',
            'fecha_aprobacion',
            'total_auditorias', 'avance_porcentaje',
            'fecha_creacion',
        ]

    def get_responsable_nombre(self, obj):
        if obj.responsable:
            nombre = f"{obj.responsable.first_name} {obj.responsable.last_name}".strip()
            return nombre or obj.responsable.username
        return None


class ProgramaAuditoriaDetailSerializer(ProgramaAuditoriaListSerializer):
    auditorias_detalle = serializers.SerializerMethodField()

    class Meta(ProgramaAuditoriaListSerializer.Meta):
        fields = ProgramaAuditoriaListSerializer.Meta.fields + [
            'auditorias', 'auditorias_detalle', 'fecha_actualizacion',
        ]

    def get_auditorias_detalle(self, obj):
        return AuditoriaListSerializer(obj.auditorias.all(), many=True).data
