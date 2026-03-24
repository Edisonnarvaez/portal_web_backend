from django.core.management.base import BaseCommand

from habilitacion.models import RequisitoDocumental


REQUISITOS_BASE = [
    # Inscripción
    {'codigo': 'INS-001', 'nombre': 'Documento de identidad o existencia legal del prestador', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Documento de identificación para persona natural o certificado de existencia para persona jurídica.', 'obligatorio': True},
    {'codigo': 'INS-002', 'nombre': 'Soporte de representación legal', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Documento que acredita la representación legal vigente.', 'obligatorio': True},
    {'codigo': 'INS-003', 'nombre': 'RUT y datos tributarios vigentes', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Registro tributario actualizado del prestador.', 'obligatorio': True},
    {'codigo': 'INS-004', 'nombre': 'Soporte de sede y dirección habilitable', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Soporte de ubicación de la sede a registrar en REPS.', 'obligatorio': True},
    {'codigo': 'INS-005', 'nombre': 'Declaración de autoevaluación inicial', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Autodeclaración de cumplimiento de condiciones de habilitación.', 'obligatorio': True},
    {'codigo': 'INS-006', 'nombre': 'Soportes de talento humano', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Relación y soportes de talento humano requerido por servicios ofertados.', 'obligatorio': True},
    {'codigo': 'INS-007', 'nombre': 'Soportes de infraestructura física', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Cumplimiento de condiciones locativas e infraestructura.', 'obligatorio': True},
    {'codigo': 'INS-008', 'nombre': 'Soportes de dotación biomédica y mantenimiento', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Inventario y evidencia de mantenimiento de equipos y dotación.', 'obligatorio': True},
    {'codigo': 'INS-009', 'nombre': 'Soportes de medicamentos, dispositivos e insumos', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Evidencia documental de gestión y control de medicamentos e insumos.', 'obligatorio': False},
    {'codigo': 'INS-010', 'nombre': 'Soportes de procesos prioritarios y seguridad del paciente', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Protocolos y procedimientos institucionales exigidos.', 'obligatorio': True},
    {'codigo': 'INS-011', 'nombre': 'Soportes de historia clínica y registros', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Evidencia de gestión documental clínica y trazabilidad.', 'obligatorio': True},
    {'codigo': 'INS-012', 'nombre': 'Soportes de interdependencia y referencia/contrarreferencia', 'tipo_tramite': 'INSCRIPCION', 'descripcion': 'Acuerdos, rutas y soportes de continuidad de atención.', 'obligatorio': False},

    # Novedad - base común
    {'codigo': 'NOV-BAS-001', 'nombre': 'Solicitud formal de novedad', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Formulario oficial de novedad con descripción del cambio.', 'obligatorio': True},
    {'codigo': 'NOV-BAS-002', 'nombre': 'Soporte del acto administrativo o decisión interna', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Acta o documento que sustenta la novedad reportada.', 'obligatorio': True},
    {'codigo': 'NOV-BAS-003', 'nombre': 'Autoevaluación actualizada asociada a la novedad', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Registro de autoevaluación ajustado a las condiciones actuales.', 'obligatorio': True},
    {'codigo': 'NOV-BAS-004', 'nombre': 'Plan de transición y gestión del riesgo por cambio', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Plan para asegurar continuidad y seguridad durante la implementación.', 'obligatorio': False},

    # Novedad - cambio de contacto
    {'codigo': 'NOV-CON-001', 'nombre': 'Soporte de actualización de datos de contacto', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Documento con actualización de teléfono, correo y canales oficiales.', 'obligatorio': True},
    {'codigo': 'NOV-CON-002', 'nombre': 'Publicación o comunicación oficial del cambio de contacto', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Evidencia de comunicación a partes interesadas.', 'obligatorio': False},

    # Novedad - cierre de modalidad
    {'codigo': 'NOV-CM-001', 'nombre': 'Acta de cierre de modalidad o servicio', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Acta de decisión y cierre de la modalidad reportada.', 'obligatorio': True},
    {'codigo': 'NOV-CM-002', 'nombre': 'Plan de continuidad y remisión de usuarios', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Plan de transición para garantizar continuidad de atención.', 'obligatorio': True},
    {'codigo': 'NOV-CM-003', 'nombre': 'Soporte de cierre de agenda y recursos asociados', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Evidencia de cierre operativo de recursos y programación.', 'obligatorio': False},

    # Novedad - cambio de horario
    {'codigo': 'NOV-HOR-001', 'nombre': 'Soporte de nuevo horario de prestación', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Documento de modificación de horarios y turnos.', 'obligatorio': True},
    {'codigo': 'NOV-HOR-002', 'nombre': 'Evidencia de divulgación de horarios actualizados', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Evidencia de socialización interna y externa del cambio.', 'obligatorio': False},

    # Novedad - cambio de complejidad
    {'codigo': 'NOV-CC-001', 'nombre': 'Soporte técnico del cambio de complejidad', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Justificación técnica y operativa del cambio de complejidad.', 'obligatorio': True},
    {'codigo': 'NOV-CC-002', 'nombre': 'Matriz de talento humano ajustada a la complejidad', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Evidencia de talento humano acorde al nivel de complejidad.', 'obligatorio': True},
    {'codigo': 'NOV-CC-003', 'nombre': 'Matriz de dotación ajustada a la complejidad', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Evidencia de equipos y dotación según nueva complejidad.', 'obligatorio': True},

    # Novedad - traslado de servicio
    {'codigo': 'NOV-TS-001', 'nombre': 'Acta o soporte de traslado de servicio', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Documento que formaliza el traslado y sus condiciones.', 'obligatorio': True},
    {'codigo': 'NOV-TS-002', 'nombre': 'Soporte de habilitación del nuevo espacio o sede', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Evidencia de condiciones del nuevo lugar de prestación.', 'obligatorio': True},
    {'codigo': 'NOV-TS-003', 'nombre': 'Plan de continuidad asistencial por traslado', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Plan de operación para garantizar continuidad a usuarios.', 'obligatorio': True},

    # Novedad - capacidad instalada
    {'codigo': 'NOV-CI-001', 'nombre': 'Soporte de ajuste de capacidad instalada', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Relación actualizada de camas, salas, ambulancias u otros.', 'obligatorio': True},
    {'codigo': 'NOV-CI-002', 'nombre': 'Soporte de disponibilidad de recursos para nueva capacidad', 'tipo_tramite': 'NOVEDAD', 'descripcion': 'Evidencia de recurso humano y tecnológico asociado.', 'obligatorio': False},

    # Visita previa
    {'codigo': 'VP-001', 'nombre': 'Solicitud formal de visita previa', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Solicitud de visita previa para validar condiciones declaradas.', 'obligatorio': True},
    {'codigo': 'VP-002', 'nombre': 'Autoevaluación vigente para visita previa', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Autoverificación vigente asociada a la visita.', 'obligatorio': True},
    {'codigo': 'VP-003', 'nombre': 'Portafolio y alcance de servicios a verificar', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Detalle de servicios objeto de verificación.', 'obligatorio': True},
    {'codigo': 'VP-004', 'nombre': 'Matriz de talento humano por servicio', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Matriz de disponibilidad de talento humano por turno y servicio.', 'obligatorio': True},
    {'codigo': 'VP-005', 'nombre': 'Inventario de dotación biomédica y mantenimiento', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Inventario y hojas de vida/mantenimiento de equipos.', 'obligatorio': True},
    {'codigo': 'VP-006', 'nombre': 'Soportes de infraestructura y planos funcionales', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Planos y evidencias de adecuación de infraestructura.', 'obligatorio': True},
    {'codigo': 'VP-007', 'nombre': 'Protocolos de seguridad del paciente aplicables', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Protocolos y procedimientos críticos institucionales.', 'obligatorio': True},
    {'codigo': 'VP-008', 'nombre': 'Ruta de referencia y contrarreferencia vigente', 'tipo_tramite': 'VISITA_PREVIA', 'descripcion': 'Evidencia de red de apoyo y continuidad asistencial.', 'obligatorio': False},

    # Visita de certificación (apertura de modalidad)
    {'codigo': 'VC-001', 'nombre': 'Plan de apertura de modalidad', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Plan operativo y cronograma para apertura de modalidad.', 'obligatorio': True},
    {'codigo': 'VC-002', 'nombre': 'Matriz de talento humano certificado', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Soportes de idoneidad y disponibilidad de talento humano.', 'obligatorio': True},
    {'codigo': 'VC-003', 'nombre': 'Inventario de dotación certificable', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Listado de dotación/equipos exigidos para la modalidad.', 'obligatorio': True},
    {'codigo': 'VC-004', 'nombre': 'Protocolos y guías clínicas de la modalidad', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Protocolos clínicos y de seguridad específicos.', 'obligatorio': True},
    {'codigo': 'VC-005', 'nombre': 'Soporte de infraestructura y ambientes específicos', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Condiciones de infraestructura para la modalidad solicitada.', 'obligatorio': True},
    {'codigo': 'VC-006', 'nombre': 'Soportes de medicamentos e insumos críticos', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Disponibilidad de medicamentos y dispositivos requeridos.', 'obligatorio': False},
    {'codigo': 'VC-007', 'nombre': 'Plan de emergencias y contingencias de la modalidad', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Plan de contingencia y continuidad operacional.', 'obligatorio': True},
    {'codigo': 'VC-008', 'nombre': 'Evidencia de entrenamiento y alistamiento', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Registros de entrenamiento de personal en la modalidad.', 'obligatorio': False},
    {'codigo': 'VC-009', 'nombre': 'Mecanismos de referencia y apoyo diagnóstico', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Acuerdos de soporte clínico y referencia.', 'obligatorio': False},
    {'codigo': 'VC-010', 'nombre': 'Acta interna de alistamiento para certificación', 'tipo_tramite': 'VISITA_CERTIFICACION', 'descripcion': 'Acta de verificación interna previa a certificación.', 'obligatorio': True},

    # Visita de reactivación
    {'codigo': 'VR-001', 'nombre': 'Solicitud formal de reactivación del servicio', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Solicitud para reactivar servicio o modalidad suspendida.', 'obligatorio': True},
    {'codigo': 'VR-002', 'nombre': 'Justificación técnica de reactivación', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Documento de justificación y alcance de reactivación.', 'obligatorio': True},
    {'codigo': 'VR-003', 'nombre': 'Plan de cierre de hallazgos previos', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Plan de acciones correctivas para hallazgos históricos.', 'obligatorio': True},
    {'codigo': 'VR-004', 'nombre': 'Evidencia de cierre de hallazgos críticos', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Soportes verificables de cierre de hallazgos críticos.', 'obligatorio': True},
    {'codigo': 'VR-005', 'nombre': 'Autoevaluación de reingreso a operación', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Autoverificación de condiciones previas a reactivación.', 'obligatorio': True},
    {'codigo': 'VR-006', 'nombre': 'Matriz actualizada de talento humano', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Soporte de disponibilidad y competencias vigentes.', 'obligatorio': True},
    {'codigo': 'VR-007', 'nombre': 'Inventario actualizado de dotación y equipos', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Equipos y dotación en estado operativo con mantenimientos.', 'obligatorio': True},
    {'codigo': 'VR-008', 'nombre': 'Soportes de infraestructura apta para reactivación', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Evidencia de condiciones locativas funcionales.', 'obligatorio': True},
    {'codigo': 'VR-009', 'nombre': 'Plan de gestión del riesgo para retorno', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Plan de prevención y mitigación de riesgos en retorno.', 'obligatorio': True},
    {'codigo': 'VR-010', 'nombre': 'Acta interna de alistamiento para visita de reactivación', 'tipo_tramite': 'VISITA_REACTIVACION', 'descripcion': 'Acta de cumplimiento interno antes de visita.', 'obligatorio': True},
]


class Command(BaseCommand):
    help = 'Carga o actualiza catálogo base de requisitos documentales (Anexo 2).'

    def handle(self, *args, **options):
        creados = 0
        actualizados = 0

        for item in REQUISITOS_BASE:
            requisito, created = RequisitoDocumental.objects.update_or_create(
                codigo=item['codigo'],
                defaults={
                    'nombre': item['nombre'],
                    'tipo_tramite': item['tipo_tramite'],
                    'descripcion': item['descripcion'],
                    'obligatorio': item['obligatorio'],
                    'activo': True,
                },
            )
            if created:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Requisitos procesados: {len(REQUISITOS_BASE)} | Creados: {creados} | Actualizados: {actualizados}'
        ))
