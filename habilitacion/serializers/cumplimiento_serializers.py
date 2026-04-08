from rest_framework import serializers

from normativity.models import Criterio
from processes.models import Documento
from soportes.models import SoporteDocumental

from ..models import Autoevaluacion, Cumplimiento, ServicioSede


class CumplimientoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de Cumplimiento."""

    criterio_codigo = serializers.CharField(
        source='criterio.codigo',
        read_only=True,
    )
    criterio_nombre = serializers.CharField(
        source='criterio.nombre',
        read_only=True,
    )
    servicio_nombre = serializers.CharField(
        source='servicio_sede.nombre_servicio',
        read_only=True,
    )
    cumple_display = serializers.CharField(
        source='get_cumple_display',
        read_only=True,
    )
    documentos = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    soportes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    documentos_evidencia = serializers.PrimaryKeyRelatedField(source='documentos', many=True, read_only=True)
    documentos_evidencia_list = serializers.SerializerMethodField(read_only=True)
    soportes_list = serializers.SerializerMethodField(read_only=True)
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
            'autoevaluacion_id',
            'servicio_sede_id',
            'criterio_id',
            'cumple',
            'cumple_display',
            'documentos',
            'soportes',
            'documentos_evidencia',
            'documentos_evidencia_list',
            'soportes_list',
            'tiene_plan_mejora',
            'planes_mejora_count',
            'hallazgos_count',
            'fecha_compromiso',
        ]
        read_only_fields = fields

    def get_tiene_plan_mejora(self, obj):
        if hasattr(obj, 'planes_mejora') and obj.planes_mejora.exists():
            return True
        return bool(obj.plan_mejora)

    def get_planes_mejora_count(self, obj):
        if hasattr(obj, 'planes_mejora'):
            return obj.planes_mejora.count()
        return 0

    def get_hallazgos_count(self, obj):
        from mejoras.models import Hallazgo

        return Hallazgo.objects.filter(
            autoevaluacion=obj.autoevaluacion,
            criterio=obj.criterio,
        ).count()

    def get_documentos_evidencia_list(self, obj):
        documentos = obj.documentos.all()
        return [
            {
                'id': doc.id,
                'titulo': doc.nombre_documento,
                'tipo': doc.tipo_documento,
                'archivo': str(doc.archivo_oficial) if doc.archivo_oficial else None,
            }
            for doc in documentos
        ]

    def get_soportes_list(self, obj):
        soportes = obj.soportes.select_related('tipo_documento').all()
        return [
            {
                'id': soporte.id,
                'tipo_documento': soporte.tipo_documento.nombre,
                'nivel': soporte.nivel,
                'es_vigente': soporte.es_vigente,
                'archivo': str(soporte.archivo) if soporte.archivo else None,
            }
            for soporte in soportes
        ]


class CumplimientoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Cumplimiento."""

    autoevaluacion_id = serializers.PrimaryKeyRelatedField(
        queryset=Autoevaluacion.objects.all(),
        source='autoevaluacion',
        write_only=True,
    )
    servicio_sede_id = serializers.PrimaryKeyRelatedField(
        queryset=ServicioSede.objects.all(),
        source='servicio_sede',
        write_only=True,
    )
    criterio_id = serializers.PrimaryKeyRelatedField(
        queryset=Criterio.objects.all(),
        source='criterio',
        write_only=True,
    )
    documentos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Documento.objects.filter(estado='VIG', activo=True),
        required=False,
    )
    soportes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SoporteDocumental.objects.filter(es_vigente=True),
        required=False,
    )
    documentos_evidencia = serializers.PrimaryKeyRelatedField(
        source='documentos',
        many=True,
        queryset=Documento.objects.filter(estado='VIG', activo=True),
        required=False,
    )

    servicios_disponibles = serializers.SerializerMethodField()

    autoevaluacion_detail = serializers.SerializerMethodField()
    servicio_sede_detail = serializers.SerializerMethodField()
    criterio_detail = serializers.SerializerMethodField()
    documentos_list = serializers.SerializerMethodField()
    soportes_list = serializers.SerializerMethodField()
    documentos_evidencia_list = serializers.SerializerMethodField()
    responsable_mejora_detail = serializers.SerializerMethodField()

    cumple_display = serializers.CharField(
        source='get_cumple_display',
        read_only=True,
    )
    tiene_plan_mejora = serializers.SerializerMethodField()
    mejora_vencida = serializers.SerializerMethodField()

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
            'documentos',
            'documentos_list',
            'soportes',
            'soportes_list',
            'documentos_evidencia',
            'documentos_evidencia_list',
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
        documentos = obj.documentos.all()
        return [
            {
                'id': doc.id,
                'titulo': doc.nombre_documento,
                'tipo': doc.tipo_documento,
                'archivo': str(doc.archivo_oficial) if doc.archivo_oficial else None,
            }
            for doc in documentos
        ]

    def get_documentos_list(self, obj):
        return self.get_documentos_evidencia_list(obj)

    def get_soportes_list(self, obj):
        soportes = obj.soportes.select_related('tipo_documento').all()
        return [
            {
                'id': soporte.id,
                'tipo_documento': soporte.tipo_documento.nombre,
                'nivel': soporte.nivel,
                'es_vigente': soporte.es_vigente,
                'archivo': str(soporte.archivo) if soporte.archivo else None,
            }
            for soporte in soportes
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
        if hasattr(obj, 'planes_mejora') and obj.planes_mejora.exists():
            return True
        return bool(obj.plan_mejora)

    def get_mejora_vencida(self, obj):
        return obj.mejora_vencida()

    def get_planes_mejora_vinculados(self, obj):
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
        if obj and obj.autoevaluacion:
            prestador = obj.autoevaluacion.datos_prestador
        elif 'autoevaluacion_id' in self.initial_data:
            try:
                autoevaluacion_id = self.initial_data.get('autoevaluacion_id')
                autoevaluacion = Autoevaluacion.objects.get(pk=autoevaluacion_id)
                prestador = autoevaluacion.datos_prestador
            except (Autoevaluacion.DoesNotExist, ValueError):
                return []
        else:
            return []

        servicios = ServicioSede.objects.filter(prestador=prestador).select_related('prestador')

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
        if self.instance is None or self.partial:
            autoevaluacion_id = self.initial_data.get('autoevaluacion_id')

            if autoevaluacion_id:
                try:
                    autoevaluacion_obj = Autoevaluacion.objects.get(pk=autoevaluacion_id)
                    prestador = autoevaluacion_obj.datos_prestador

                    if value.prestador != prestador:
                        servicios_disponibles = ServicioSede.objects.filter(
                            prestador=prestador
                        ).values_list('nombre_servicio', flat=True)

                        msg = (
                            f"El servicio '{value.nombre_servicio}' pertenece al prestador "
                            f"'{value.prestador.nombre_prestador}', pero la autoevaluacion "
                            f"es del prestador '{prestador.nombre_prestador}'. "
                        )

                        if servicios_disponibles:
                            msg += f"Servicios disponibles: {', '.join(servicios_disponibles)}"
                        else:
                            msg += (
                                f"No hay servicios registrados para '{prestador.nombre_prestador}'. "
                                'Registre servicios antes de crear cumplimientos.'
                            )

                        raise serializers.ValidationError(msg)

                except Autoevaluacion.DoesNotExist:
                    raise serializers.ValidationError(
                        'La autoevaluacion especificada no existe.'
                    )

        return value

    def get_hallazgos_vinculados(self, obj):
        from mejoras.models import Hallazgo

        hallazgos = Hallazgo.objects.filter(
            autoevaluacion=obj.autoevaluacion,
            criterio=obj.criterio,
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

    def validate(self, attrs):
        attrs = super().validate(attrs)

        criterio = attrs.get('criterio') or getattr(self.instance, 'criterio', None)
        cumple = attrs.get('cumple') or getattr(self.instance, 'cumple', None)

        if not criterio or not cumple or cumple == 'NO_APLICA':
            return attrs

        documentos = attrs.get('documentos', None)
        soportes = attrs.get('soportes', None)

        if documentos is None and self.instance is not None:
            documentos = list(self.instance.documentos.all())
        if soportes is None and self.instance is not None:
            soportes = list(self.instance.soportes.all())

        if getattr(criterio, 'requiere_documento', False) and not documentos:
            raise serializers.ValidationError(
                {'documentos': 'Este criterio requiere al menos un documento de calidad.'}
            )

        if getattr(criterio, 'requiere_soporte', False) and not soportes:
            raise serializers.ValidationError(
                {'soportes': 'Este criterio requiere al menos un soporte documental vigente.'}
            )

        return attrs
