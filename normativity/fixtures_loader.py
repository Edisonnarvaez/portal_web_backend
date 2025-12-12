"""
normativity/fixtures_loader.py

✓ Script COMPLETO para cargar datos iniciales de la Resolución 3100 de 2019.

✓ CARACTERÍSTICAS:
  - 7 Estándares principales (TH, INF, DOT, PO, RS, GI, SA)
  - 3 Criterios por estándar (21 criterios totales)
  - Documentos normativos de referencia
  - Idempotente (puede ejecutarse múltiples veces sin duplicar)
  - Listo para producción

✓ EJECUCIÓN:
  Opción 1 (Recomendado):
    python manage.py shell
    exec(open('normativity/fixtures_loader.py').read())

  Opción 2:
    python normativity/fixtures_loader.py

✓ DESPUÉS DE EJECUTAR:
  - Sistema tiene todos los estándares de Resolución 3100
  - Admin disponible en /admin/normativity/
  - APIs REST disponibles en /api/normativity/
  - Listo para crear autoevaluaciones

Autor: Development Team
Última actualización: 2025-12-12
"""

import os
import sys
import django

# Configurar Django si se ejecuta directamente
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

from normativity.models import Estandar, Criterio, DocumentoNormativo

# ============================================================================
# CONFIGURACIÓN Y ESTILOS
# ============================================================================

SEPARADOR = "=" * 100
SUBSEPARADOR = "-" * 100

def print_header(titulo):
    """Imprimir encabezado formateado."""
    print(f"\n{SEPARADOR}")
    print(f"  ✓ {titulo}")
    print(f"{SEPARADOR}")

def print_item(status, codigo, nombre, detalles=""):
    """Imprimir item con formato."""
    icon = "✓" if status == "CREADO" else "⊕"
    print(f"  {icon} {codigo:5} | {nombre:50} {detalles}")

# ============================================================================
# 1. ESTÁNDARES (7 Estándares de la Resolución 3100/2019)
# ============================================================================

print_header("CARGANDO ESTÁNDARES DE RESOLUCIÓN 3100/2019")

estandares_data = [
    {
        'codigo': 'TH',
        'nombre': 'Talento Humano',
        'descripcion': 'Disponibilidad, idoneidad, capacitación y entrenamiento de talento humano para garantizar la prestación de servicios de salud con calidad.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'INF',
        'nombre': 'Infraestructura Física',
        'descripcion': 'Instalaciones, equipos, servicios básicos, seguridad física y ambiental para la prestación de servicios de salud.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'DOT',
        'nombre': 'Dotación y Medicamentos',
        'descripcion': 'Disponibilidad, almacenamiento, control, uso racional y disposición final de medicamentos y dispositivos médicos.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'PO',
        'nombre': 'Procesos Organizacionales',
        'descripcion': 'Gestión administrativa, financiera, información, comunicación y atención al usuario con enfoque de calidad.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'RS',
        'nombre': 'Relacionamiento',
        'descripcion': 'Gestión de relaciones con usuarios, familiares, comunidad, referencia y contrarreferencia de servicios.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'GI',
        'nombre': 'Garantía de Calidad',
        'descripcion': 'Mejora continua, evaluación de satisfacción, seguimiento de procesos, resultados y desempeño organizacional.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'SA',
        'nombre': 'Seguridad del Paciente',
        'descripcion': 'Prevención y control de infecciones, prevención de eventos adversos, gestión del riesgo y seguridad en procedimientos.',
        'version_resolucion': '3100/2019'
    },
]

# Crear estándares
estandares_creados = {}
estandares_count = 0

print(f"\n{SUBSEPARADOR}")
for data in estandares_data:
    estandar, created = Estandar.objects.get_or_create(
        codigo=data['codigo'],
        defaults={
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'version_resolucion': data['version_resolucion'],
            'estado': True,
        }
    )
    estandares_creados[data['codigo']] = estandar
    status = 'CREADO' if created else 'EXISTE'
    estandares_count += 1
    print_item(status, data['codigo'], data['nombre'])

print(f"{SUBSEPARADOR}\n  Total estándares: {estandares_count}")

# ============================================================================
# 2. CRITERIOS POR ESTÁNDAR (3 criterios × 7 estándares = 21 criterios)
# ============================================================================

print_header("CARGANDO CRITERIOS (21 CRITERIOS TOTALES)")

criterios_por_estandar = {
    'TH': [
        {
            'codigo': '1.1',
            'nombre': 'Disponibilidad de personal médico especializado',
            'descripcion': 'La institución cuenta con médicos especialistas disponibles según la complejidad de los servicios.',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '1.2',
            'nombre': 'Capacitación y entrenamiento continuo',
            'descripcion': 'Programa formal de capacitación continua para todo el personal de salud, mínimo anual.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '1.3',
            'nombre': 'Evaluación de competencias',
            'descripcion': 'Evaluación periódica de competencias técnicas y comportamentales de todo el personal.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
    'INF': [
        {
            'codigo': '2.1',
            'nombre': 'Disponibilidad de espacios adecuados',
            'descripcion': 'Espacios físicos separados por función, adecuados para las actividades clínicas y administrativas.',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
        {
            'codigo': '2.2',
            'nombre': 'Servicios básicos operativos',
            'descripcion': 'Agua potable, electricidad, gas medicinal (si aplica) disponibles de manera segura y continua.',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
        {
            'codigo': '2.3',
            'nombre': 'Mantenimiento preventivo de instalaciones',
            'descripcion': 'Plan de mantenimiento preventivo para infraestructura, equipos y servicios.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
    'DOT': [
        {
            'codigo': '3.1',
            'nombre': 'Disponibilidad de medicamentos esenciales',
            'descripcion': 'Medicamentos disponibles según nivel de complejidad y servicios ofertados, con acceso permanente.',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '3.2',
            'nombre': 'Control y almacenamiento adecuado',
            'descripcion': 'Sistema de almacenamiento seguro, condiciones de temperatura y humedad controladas.',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
        {
            'codigo': '3.3',
            'nombre': 'Inventario y trazabilidad',
            'descripcion': 'Inventario actualizado de medicamentos y dispositivos, con registro de entrada y salida.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
    'PO': [
        {
            'codigo': '4.1',
            'nombre': 'Documentación de procesos',
            'descripcion': 'Todos los procesos clínicos y administrativos documentados, actualizados y disponibles.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '4.2',
            'nombre': 'Gestión financiera y administrativa',
            'descripcion': 'Sistema de gestión financiera transparente, presupuesto, ingresos y gastos controlados.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '4.3',
            'nombre': 'Sistema de información operativo',
            'descripcion': 'Sistema de información que registre datos clínicos y administrativos con control de acceso.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
    ],
    'RS': [
        {
            'codigo': '5.1',
            'nombre': 'Accesibilidad a servicios',
            'descripcion': 'Servicios accesibles en términos de ubicación, horarios, costo y capacidad de respuesta.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '5.2',
            'nombre': 'Satisfacción del usuario',
            'descripcion': 'Mecanismo de medición de satisfacción del usuario, realizado periódicamente.',
            'complejidad': 'BAJA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '5.3',
            'nombre': 'Sistema de referencia y contrarreferencia',
            'descripcion': 'Proceso formal de referencia y contrarreferencia con instituciones de mayor complejidad.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
    'GI': [
        {
            'codigo': '6.1',
            'nombre': 'Planes de mejora continua',
            'descripcion': 'Plan anual de mejora con indicadores, metas y seguimiento de avance.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '6.2',
            'nombre': 'Auditoría interna periódica',
            'descripcion': 'Auditoría interna realizada mínimo anualmente para evaluar cumplimiento de estándares.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '6.3',
            'nombre': 'Indicadores de desempeño',
            'descripcion': 'Indicadores de procesos, estructura y resultados monitoreados continuamente.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
    'SA': [
        {
            'codigo': '7.1',
            'nombre': 'Prevención de infecciones asociadas a la atención',
            'descripcion': 'Protocolos de prevención y control de infecciones, higiene y desinfección de áreas.',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '7.2',
            'nombre': 'Reporte y análisis de eventos adversos',
            'descripcion': 'Sistema de reporte, análisis y seguimiento de eventos adversos y near-miss.',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '7.3',
            'nombre': 'Gestión integral del riesgo',
            'descripcion': 'Identificación, evaluación, control y monitoreo de riesgos clínicos y no clínicos.',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
}

# Crear criterios
criterios_total = 0
print(f"\n{SUBSEPARADOR}")

for codigo_estandar, criterios in criterios_por_estandar.items():
    estandar = estandares_creados[codigo_estandar]
    print(f"\n  ESTÁNDAR {codigo_estandar} - {estandar.nombre}")
    print(f"  {SUBSEPARADOR}")
    
    for criterio_data in criterios:
        criterio, created = Criterio.objects.get_or_create(
            estandar=estandar,
            codigo=criterio_data['codigo'],
            defaults={
                'nombre': criterio_data['nombre'],
                'descripcion': criterio_data.get('descripcion', ''),
                'complejidad': criterio_data['complejidad'],
                'es_mandatorio': criterio_data['es_mandatorio'],
                'aplica_todos': criterio_data['aplica_todos'],
                'requiere_evidencia_documental': criterio_data['requiere_evidencia_documental'],
                'estado': True,
            }
        )
        criterios_total += 1
        status = 'CREADO' if created else 'EXISTE'
        mandatorio_icon = '✓M' if criterio_data['es_mandatorio'] else '○O'
        complejidad_short = criterio_data['complejidad'][0]
        detalles = f"[{complejidad_short}] {mandatorio_icon}"
        print_item(status, criterio_data['codigo'], criterio_data['nombre'], detalles)

print(f"\n  Total criterios cargados: {criterios_total}")

# ============================================================================
# 3. DOCUMENTOS NORMATIVOS
# ============================================================================

print_header("CARGANDO DOCUMENTOS NORMATIVOS")

documentos_data = [
    {
        'titulo': 'Resolución 3100 de 2019',
        'tipo': 'RESOLUCION',
        'numero_referencia': 'Res3100-2019',
        'descripcion': 'Por la cual se adoptan los estándares de habilitación del Ministerio de Salud y Protección Social.',
    },
    {
        'titulo': 'Resolución 1533 de 2021',
        'tipo': 'RESOLUCION',
        'numero_referencia': 'Res1533-2021',
        'descripcion': 'Por la cual se modifica la Resolución 3100 de 2019.',
    },
    {
        'titulo': 'Manual de Estándares de Habilitación',
        'tipo': 'MANUAL',
        'numero_referencia': 'Manual-Estandares-2019',
        'descripcion': 'Guía técnica para la implementación y evaluación de estándares de habilitación.',
    },
    {
        'titulo': 'Documento de Autoevaluación',
        'tipo': 'GUIA',
        'numero_referencia': 'Autoevaluacion-Estándares',
        'descripcion': 'Herramienta para la autoevaluación de instituciones prestadoras de servicios de salud.',
    },
]

print(f"\n{SUBSEPARADOR}")
documentos_count = 0

for doc_data in documentos_data:
    documento, created = DocumentoNormativo.objects.get_or_create(
        numero_referencia=doc_data['numero_referencia'],
        defaults={
            'titulo': doc_data['titulo'],
            'tipo': doc_data['tipo'],
            'descripcion': doc_data.get('descripcion', ''),
        }
    )
    documentos_count += 1
    status = 'CREADO' if created else 'EXISTE'
    print_item(status, doc_data['tipo'][:4], doc_data['titulo'])

print(f"{SUBSEPARADOR}\n  Total documentos: {documentos_count}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print_header("CARGA COMPLETADA EXITOSAMENTE")

total_registros = estandares_count + criterios_total + documentos_count

print(f"\n{SUBSEPARADOR}")
print(f"  RESUMEN DE DATOS CARGADOS:")
print(f"  {SUBSEPARADOR}")
print(f"    ✓ Estándares:      {estandares_count}/7")
print(f"    ✓ Criterios:       {criterios_total}/21")
print(f"    ✓ Documentos:      {documentos_count}")
print(f"    ✓ Total registros: {total_registros}")
print(f"\n{SUBSEPARADOR}")

print(f"""
✓ PRÓXIMOS PASOS:

  1. VERIFICAR EN ADMIN:
     http://localhost:8000/admin/normativity/

  2. PROBAR APIs REST:
     GET  /api/normativity/estandares/
     GET  /api/normativity/criterios/
     GET  /api/normativity/documentos/

  3. CREAR AUTOEVALUACIONES:
     POST /api/habilitacion/autoevaluaciones/

{SEPARADOR}
✓ SISTEMA LISTO PARA PRODUCCIÓN
{SEPARADOR}
""")

# ============================================================================
# INFORMACIÓN ADICIONAL
# ============================================================================

if __name__ == '__main__':
    print("\n✓ Script ejecutado exitosamente")
    print(f"✓ Total de {total_registros} registros cargados en la base de datos")
    sys.exit(0)
