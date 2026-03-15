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
        source='headquarters.company.name',
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
    
    headquarters_id = serializers.PrimaryKeyRelatedField(
        queryset=Headquarters.objects.all(),
        source='headquarters',
        write_only=True
    )
    company_detail = serializers.SerializerMethodField()
    headquarters_detail = serializers.SerializerMethodField()
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
        """Detalle de la company vinculada a través de headquarters."""
        company = obj.headquarters.company
        return {
            'id': company.id,
            'name': company.name,
            'nit': getattr(company, 'nit', None),
        }

    def get_headquarters_detail(self, obj):
        """Detalle de la sede (headquarters) vinculada al prestador."""
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
        """Validar formato del código REPS."""
        if not value or len(value) < 5:
            raise serializers.ValidationError(
                "El código REPS debe tener al menos 5 caracteres."
            )
        return value


class ServicioSedeListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de ServicioSede."""
    
    prestador_codigo = serializers.CharField(
        source='prestador.codigo_reps',
        read_only=True
    )
    prestador_headquarters = serializers.CharField(
        source='prestador.headquarters.name',
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
        write_only=True
    )
    prestador_detail = serializers.SerializerMethodField()
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
        source='datos_prestador',
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

    # ─── Integración con app mejoras ───
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
        """Resumen de cumplimientos por estado."""
        cumplimientos = obj.cumplimientos.all()
        return {
            'total': cumplimientos.count(),
            'cumple': cumplimientos.filter(cumple='CUMPLE').count(),
            'no_cumple': cumplimientos.filter(cumple='NO_CUMPLE').count(),
            'parcialmente': cumplimientos.filter(cumple='PARCIALMENTE').count(),
            'no_aplica': cumplimientos.filter(cumple='NO_APLICA').count(),
        }

    def get_planes_mejora_count(self, obj):
        """Total de planes de mejora vinculados a esta autoevaluación."""
        from mejoras.models import PlanMejora
        return PlanMejora.objects.filter(autoevaluacion=obj).count()

    def get_hallazgos_count(self, obj):
        """Total de hallazgos vinculados a esta autoevaluación."""
        from mejoras.models import Hallazgo
        return Hallazgo.objects.filter(autoevaluacion=obj).count()

    def get_mejoras_resumen(self, obj):
        """Resumen de planes de mejora y hallazgos para esta autoevaluación."""
        from mejoras.models import PlanMejora, Hallazgo
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
    documentos_evidencia = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Documento.objects.filter(estado='VIGENTE'),
        required=False
    )
    documentos_evidencia_list = serializers.SerializerMethodField(read_only=True)
    tiene_plan_mejora = serializers.SerializerMethodField()
    planes_mejora_count = serializers.SerializerMethodField()
    hallazgos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cumplimiento
        fields = [
            'id',
            'criterio_codigo',
            'criterio_nombre',
            'servicio_nombre',
            "autoevaluacion_id",  
            "servicio_sede_id",
            "criterio_id",
            'cumple',
            'cumple_display',
            "documentos_evidencia",      # writable (entrada)
            "documentos_evidencia_list", # read-only (salida)
            'tiene_plan_mejora',
            'planes_mejora_count',
            'hallazgos_count',
            'fecha_compromiso',
        ]
        read_only_fields = fields
    
    def get_tiene_plan_mejora(self, obj):
        """Verifica si tiene planes de mejora en la app mejoras."""
        if hasattr(obj, 'planes_mejora') and obj.planes_mejora.exists():
            return True
        # Fallback al campo TextField antiguo
        return bool(obj.plan_mejora)

    def get_planes_mejora_count(self, obj):
        """Cantidad de planes de mejora vinculados (app mejoras)."""
        if hasattr(obj, 'planes_mejora'):
            return obj.planes_mejora.count()
        return 0

    def get_hallazgos_count(self, obj):
        """Cantidad de hallazgos vinculados a la autoevaluación + criterio."""
        from mejoras.models import Hallazgo
        return Hallazgo.objects.filter(
            autoevaluacion=obj.autoevaluacion,
            criterio=obj.criterio
        ).count()
    
    def get_documentos_evidencia_list(self, obj):
        """Lista de documentos de evidencia con detalles."""
        documentos = obj.documentos_evidencia.all()
        return [
            {
                'id': doc.id,
                'titulo': doc.nombre_documento,
                'tipo': doc.tipo_documento,
                'archivo': str(doc.archivo_oficial) if doc.archivo_oficial else None,
            }
            for doc in documentos
        ]


class CumplimientoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Cumplimiento."""
    
    autoevaluacion_id = serializers.PrimaryKeyRelatedField(
        queryset=Autoevaluacion.objects.all(),
        source='autoevaluacion',
        write_only=True
    )
    servicio_sede_id = serializers.PrimaryKeyRelatedField(
        queryset=ServicioSede.objects.all(),
        source='servicio_sede',
        write_only=True
    )
    criterio_id = serializers.PrimaryKeyRelatedField(
        queryset=Criterio.objects.all(),
        source='criterio',
        write_only=True
    )
    
    # Servicios disponibles para la autoevaluación seleccionada (lectura)
    servicios_disponibles = serializers.SerializerMethodField()
    
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

    # ─── Integración con app mejoras ───
    planes_mejora_vinculados = serializers.SerializerMethodField()
    hallazgos_vinculados = serializers.SerializerMethodField()
    
    class Meta:
        model = Cumplimiento
        fields = [
            'id',
            'autoevaluacion_id',
            'autoevaluacion_detail',
            'servicio_sede_id',
            'servicio_sede_detail',
            'servicios_disponibles',
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
            'planes_mejora_vinculados',
            'hallazgos_vinculados',
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
            'planes_mejora_vinculados',
            'hallazgos_vinculados',
            'servicios_disponibles',
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
                'titulo': doc.nombre_documento,
                'tipo': doc.tipo_documento,
                'archivo': str(doc.archivo_oficial) if doc.archivo_oficial else None,
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
        """Verifica si tiene planes de mejora vinculados (app mejoras o campo legacy)."""
        if hasattr(obj, 'planes_mejora') and obj.planes_mejora.exists():
            return True
        return bool(obj.plan_mejora)
    
    def get_mejora_vencida(self, obj):
        return obj.mejora_vencida()

    def get_planes_mejora_vinculados(self, obj):
        """Lista de planes de mejora vinculados (app mejoras)."""
        if hasattr(obj, 'planes_mejora'):
            planes = obj.planes_mejora.all()
            return [
                {
                    'id': p.id,
                    'numero_plan': p.numero_plan,
                    'estado': p.estado,
                    'porcentaje_avance': p.porcentaje_avance,
                    'fecha_vencimiento': p.fecha_vencimiento,
                    'esta_vencido': p.esta_vencido,
                }
                for p in planes
            ]
        return []

    def get_servicios_disponibles(self, obj):
        """
        Retorna los servicios disponibles para la autoevaluación.
        Útil para que el frontend sepa qué servicios puede seleccionar.
        Robustez: Soporta tanto updates (obj existe) como context del request.
        """
        # Opción 1: Si el objeto existe, usar sus datos
        if obj and obj.autoevaluacion:
            prestador = obj.autoevaluacion.datos_prestador
        # Opción 2: Desde el contexto (durante POST/PUT)
        elif 'autoevaluacion_id' in self.initial_data:
            try:
                autoevaluacion_id = self.initial_data.get('autoevaluacion_id')
                autoevaluacion = Autoevaluacion.objects.get(pk=autoevaluacion_id)
                prestador = autoevaluacion.datos_prestador
            except (Autoevaluacion.DoesNotExist, ValueError):
                return []
        else:
            return []
        
        servicios = ServicioSede.objects.filter(
            prestador=prestador
        ).select_related('prestador')
        
        return [
            {
                'id': s.id,
                'codigo': s.codigo_servicio,
                'nombre': s.nombre_servicio,
                'modalidad': s.get_modalidad_display(),
                'complejidad': s.get_complejidad_display(),
                'estado': s.get_estado_habilitacion_display(),
            }
            for s in servicios
        ]
    
    def validate_servicio_sede_id(self, value):
        """
        Validar que el servicio pertenezca al prestador de la autoevaluación.
        Se ejecuta cuando se actualiza/crea un cumplimiento.
        Con mensajes de error descriptivos.
        """
        # Solo validar si estamos en create/update
        if self.instance is None or self.partial:
            # Obtener la autoevaluación del contexto
            autoevaluacion_id = self.initial_data.get('autoevaluacion_id')
            
            if autoevaluacion_id:
                try:
                    autoevaluacion_obj = Autoevaluacion.objects.get(pk=autoevaluacion_id)
                    prestador = autoevaluacion_obj.datos_prestador
                    
                    # Verificar que el servicio pertenezca a este prestador
                    if value.prestador != prestador:
                        # Obtener servicios disponibles para sugerir
                        servicios_disponibles = ServicioSede.objects.filter(
                            prestador=prestador
                        ).values_list('nombre_servicio', flat=True)
                        
                        msg = (
                            f"El servicio '{value.nombre_servicio}' pertenece al prestador "
                            f"'{value.prestador.nombre_prestador}', pero la autoevaluación "
                            f"es del prestador '{prestador.nombre_prestador}'. "
                        )
                        
                        if servicios_disponibles:
                            msg += f"Servicios disponibles: {', '.join(servicios_disponibles)}"
                        else:
                            msg += (
                                f"⚠️ No hay servicios registrados para '{prestador.nombre_prestador}'. "
                                f"Registre servicios antes de crear cumplimientos."
                            )
                        
                        raise serializers.ValidationError(msg)
                        
                except Autoevaluacion.DoesNotExist:
                    raise serializers.ValidationError(
                        "La autoevaluación especificada no existe."
                    )
        
        return value

    def get_hallazgos_vinculados(self, obj):
        """Lista de hallazgos vinculados (app mejoras) por autoevaluacion + criterio."""
        from mejoras.models import Hallazgo
        hallazgos = Hallazgo.objects.filter(
            autoevaluacion=obj.autoevaluacion,
            criterio=obj.criterio
        )
        return [
            {
                'id': h.id,
                'numero_hallazgo': h.numero_hallazgo,
                'tipo': h.tipo,
                'severidad': h.severidad,
                'estado': h.estado,
                'tiene_plan': h.plan_mejora_id is not None,
            }
            for h in hallazgos
        ]
