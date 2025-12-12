"""
habilitacion/serializers.py

Serializers para la API de habilitación de servicios de salud.
Incluye validaciones complejas y campos calculados.
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento
from companies.models import Company, Headquarters
from normativity.models import Criterio
from processes.models import Documento
from users.models import User


class DatosPrestadorListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de DatosPrestador."""
    
    company_name = serializers.CharField(
        source='company.name',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True
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
        """¿Está próxima a vencer?"""
        return obj.esta_proxima_a_vencer(dias=90)
    
    def get_dias_vencimiento(self, obj):
        """Días restantes para vencimiento."""
        return obj.dias_para_vencimiento()


class DatosPrestadorDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para DatosPrestador con validaciones."""
    
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        write_only=True
    )
    company_detail = serializers.SerializerMethodField()
    clase_prestador_display = serializers.CharField(
        source='get_clase_prestador_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True
    )
    
    # Información calculada
    dias_vencimiento = serializers.SerializerMethodField()
    proxima_vencer = serializers.SerializerMethodField()
    vencida = serializers.SerializerMethodField()
    autoevaluaciones_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DatosPrestador
        fields = [
            'id',
            'codigo_reps',
            'company_id',
            'company_detail',
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
            'dias_vencimiento',
            'proxima_vencer',
            'vencida',
            'autoevaluaciones_count',
        ]
    
    def get_company_detail(self, obj):
        """Detalle de la company vinculada."""
        return {
            'id': obj.company.id,
            'name': obj.company.name,
            'nit': getattr(obj.company, 'nit', None),
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
        """Validar formato del código REPS."""
        if not value or len(value) < 5:
            raise serializers.ValidationError(
                "El código REPS debe tener al menos 5 caracteres."
            )
        return value


class ServicioSedeListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de ServicioSede."""
    
    sede_nombre = serializers.CharField(
        source='sede.name',
        read_only=True
    )
    modalidad_display = serializers.CharField(
        source='get_modalidad_display',
        read_only=True
    )
    complejidad_display = serializers.CharField(
        source='get_complejidad_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True
    )
    vencido = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicioSede
        fields = [
            'id',
            'codigo_servicio',
            'nombre_servicio',
            'sede_nombre',
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
    
    sede_id = serializers.PrimaryKeyRelatedField(
        queryset=Headquarters.objects.all(),
        write_only=True
    )
    sede_detail = serializers.SerializerMethodField()
    modalidad_display = serializers.CharField(
        source='get_modalidad_display',
        read_only=True
    )
    complejidad_display = serializers.CharField(
        source='get_complejidad_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_habilitacion_display',
        read_only=True
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
            'sede_id',
            'sede_detail',
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
            'sede_detail',
            'vencido',
            'dias_vencimiento',
        ]
    
    def get_sede_detail(self, obj):
        return {
            'id': obj.sede.id,
            'name': obj.sede.name,
            'address': obj.sede.address,
        }
    
    def get_vencido(self, obj):
        return obj.esta_vencido()
    
    def get_dias_vencimiento(self, obj):
        return obj.dias_para_vencimiento()


class AutoevaluacionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de Autoevaluacion."""
    
    prestador_codigo = serializers.CharField(
        source='datos_prestador.codigo_reps',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
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
        write_only=True
    )
    datos_prestador_detail = serializers.SerializerMethodField()
    usuario_responsable_detail = serializers.SerializerMethodField()
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    porcentaje_cumplimiento = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()
    total_cumplimientos = serializers.SerializerMethodField()
    cumplimientos_data = serializers.SerializerMethodField()
    
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
        ]
    
    def get_datos_prestador_detail(self, obj):
        return {
            'id': obj.datos_prestador.id,
            'codigo_reps': obj.datos_prestador.codigo_reps,
            'company_name': obj.datos_prestador.company.name,
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
        """Resumen de cumplimientos por estado."""
        cumplimientos = obj.cumplimientos.all()
        return {
            'total': cumplimientos.count(),
            'cumple': cumplimientos.filter(cumple='CUMPLE').count(),
            'no_cumple': cumplimientos.filter(cumple='NO_CUMPLE').count(),
            'parcialmente': cumplimientos.filter(cumple='PARCIALMENTE').count(),
            'no_aplica': cumplimientos.filter(cumple='NO_APLICA').count(),
        }


class CumplimientoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de Cumplimiento."""
    
    criterio_codigo = serializers.CharField(
        source='criterio.codigo',
        read_only=True
    )
    criterio_nombre = serializers.CharField(
        source='criterio.nombre',
        read_only=True
    )
    servicio_nombre = serializers.CharField(
        source='servicio_sede.nombre_servicio',
        read_only=True
    )
    cumple_display = serializers.CharField(
        source='get_cumple_display',
        read_only=True
    )
    tiene_plan_mejora = serializers.SerializerMethodField()
    
    class Meta:
        model = Cumplimiento
        fields = [
            'id',
            'criterio_codigo',
            'criterio_nombre',
            'servicio_nombre',
            'cumple',
            'cumple_display',
            'tiene_plan_mejora',
            'fecha_compromiso',
        ]
        read_only_fields = fields
    
    def get_tiene_plan_mejora(self, obj):
        return obj.tiene_plan_mejora()


class CumplimientoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Cumplimiento."""
    
    autoevaluacion_id = serializers.PrimaryKeyRelatedField(
        queryset=Autoevaluacion.objects.all(),
        write_only=True
    )
    servicio_sede_id = serializers.PrimaryKeyRelatedField(
        queryset=ServicioSede.objects.all(),
        write_only=True
    )
    criterio_id = serializers.PrimaryKeyRelatedField(
        queryset=Criterio.objects.all(),
        write_only=True
    )
    
    # Details (lectura)
    autoevaluacion_detail = serializers.SerializerMethodField()
    servicio_sede_detail = serializers.SerializerMethodField()
    criterio_detail = serializers.SerializerMethodField()
    documentos_evidencia_list = serializers.SerializerMethodField()
    responsable_mejora_detail = serializers.SerializerMethodField()
    
    cumple_display = serializers.CharField(
        source='get_cumple_display',
        read_only=True
    )
    tiene_plan_mejora = serializers.SerializerMethodField()
    mejora_vencida = serializers.SerializerMethodField()
    
    class Meta:
        model = Cumplimiento
        fields = [
            'id',
            'autoevaluacion_id',
            'autoevaluacion_detail',
            'servicio_sede_id',
            'servicio_sede_detail',
            'criterio_id',
            'criterio_detail',
            'cumple',
            'cumple_display',
            'hallazgo',
            'plan_mejora',
            'responsable_mejora_detail',
            'fecha_compromiso',
            'tiene_plan_mejora',
            'mejora_vencida',
            'documentos_evidencia_list',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'fecha_creacion',
            'fecha_actualizacion',
            'autoevaluacion_detail',
            'servicio_sede_detail',
            'criterio_detail',
            'documentos_evidencia_list',
            'responsable_mejora_detail',
            'tiene_plan_mejora',
            'mejora_vencida',
        ]
    
    def get_autoevaluacion_detail(self, obj):
        return {
            'id': obj.autoevaluacion.id,
            'numero': obj.autoevaluacion.numero_autoevaluacion,
            'periodo': obj.autoevaluacion.periodo,
        }
    
    def get_servicio_sede_detail(self, obj):
        return {
            'id': obj.servicio_sede.id,
            'codigo': obj.servicio_sede.codigo_servicio,
            'nombre': obj.servicio_sede.nombre_servicio,
        }
    
    def get_criterio_detail(self, obj):
        return {
            'id': obj.criterio.id,
            'codigo': obj.criterio.codigo,
            'nombre': obj.criterio.nombre,
            'complejidad': obj.criterio.complejidad,
        }
    
    def get_documentos_evidencia_list(self, obj):
        documentos = obj.documentos_evidencia.all()
        return [
            {
                'id': doc.id,
                'titulo': doc.titulo,
                'tipo': doc.tipo,
                'archivo': str(doc.archivo) if doc.archivo else None,
            }
            for doc in documentos
        ]
    
    def get_responsable_mejora_detail(self, obj):
        if not obj.responsable_mejora:
            return None
        return {
            'id': obj.responsable_mejora.id,
            'username': obj.responsable_mejora.username,
            'email': obj.responsable_mejora.email,
        }
    
    def get_tiene_plan_mejora(self, obj):
        return obj.tiene_plan_mejora()
    
    def get_mejora_vencida(self, obj):
        return obj.mejora_vencida()
