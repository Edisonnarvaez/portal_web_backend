"""
normativity/fixtures/datos_resolucion_3100.py

Script para cargar datos iniciales de la Resolución 3100 de 2019.
Crea los 7 estándares y algunos criterios de ejemplo.

Ejecutar: python manage.py shell < normativity/fixtures/datos_resolucion_3100.py
"""

from normativity.models import Estandar, Criterio, DocumentoNormativo

# Limpiar datos previos (opcional)
# Estandar.objects.all().delete()
# Criterio.objects.all().delete()

print("=" * 80)
print("CARGANDO DATOS DE RESOLUCIÓN 3100 DE 2019")
print("=" * 80)

# ============================================================================
# 1. ESTÁNDARES (7 Estándares de la Resolución 3100)
# ============================================================================

estandares_data = [
    {
        'codigo': 'TH',
        'nombre': 'Talento Humano',
        'descripcion': 'Recursos humanos: disponibilidad, competencia, capacitación y entrenamiento.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'INF',
        'nombre': 'Infraestructura Física',
        'descripcion': 'Instalaciones, equipos, servicios básicos, seguridad y ambientes.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'DOT',
        'nombre': 'Dotación y Medicamentos',
        'descripcion': 'Disponibilidad, almacenamiento, control y uso de medicamentos y equipos.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'PO',
        'nombre': 'Procesos Organizacionales',
        'descripcion': 'Gestión administrativo-financiera, información y comunicación.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'RS',
        'nombre': 'Relacionamiento',
        'descripcion': 'Gestión de relaciones con usuarios, referencia y contrarreferencia.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'GI',
        'nombre': 'Garantía de Calidad',
        'descripcion': 'Mejora continua, satisfacción del usuario y seguimiento de procesos.',
        'version_resolucion': '3100/2019'
    },
    {
        'codigo': 'SA',
        'nombre': 'Seguridad del Paciente',
        'descripcion': 'Prevención de eventos adversos, infecciones y gestión del riesgo.',
        'version_resolucion': '3100/2019'
    },
]

# Crear estándares
estandares_creados = {}
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
    status = '✓ CREADO' if created else '⊕ YA EXISTE'
    print(f"{status}: {data['codigo']} - {data['nombre']}")

print("\n" + "=" * 80)
print("CARGANDO CRITERIOS POR ESTÁNDAR")
print("=" * 80)

# ============================================================================
# 2. CRITERIOS POR ESTÁNDAR (Ejemplos - Resolución 3100)
# ============================================================================

criterios_por_estandar = {
    'TH': [
        {
            'codigo': '1.1',
            'nombre': 'Disponibilidad de personal médico especializado',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '1.2',
            'nombre': 'Capacitación y entrenamiento continuo',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '1.3',
            'nombre': 'Evaluación de competencias',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': False,
            'requiere_evidencia_documental': True,
        },
    ],
    'INF': [
        {
            'codigo': '2.1',
            'nombre': 'Disponibilidad de espacios adecuados',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
        {
            'codigo': '2.2',
            'nombre': 'Servicios básicos (agua, electricidad, gas)',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
        {
            'codigo': '2.3',
            'nombre': 'Mantenimiento preventivo de instalaciones',
            'complejidad': 'MEDIA',
            'es_mandatorio': False,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
    'DOT': [
        {
            'codigo': '3.1',
            'nombre': 'Disponibilidad de medicamentos esenciales',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '3.2',
            'nombre': 'Control y almacenamiento adecuado',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
        {
            'codigo': '3.3',
            'nombre': 'Inventario actualizado',
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
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '4.2',
            'nombre': 'Gestión financiera transparente',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '4.3',
            'nombre': 'Sistemas de información operativos',
            'complejidad': 'MEDIA',
            'es_mandatorio': False,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
    ],
    'RS': [
        {
            'codigo': '5.1',
            'nombre': 'Accesibilidad a servicios',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': False,
        },
        {
            'codigo': '5.2',
            'nombre': 'Satisfacción del usuario',
            'complejidad': 'BAJA',
            'es_mandatorio': False,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '5.3',
            'nombre': 'Sistema de referencia y contrarreferencia',
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
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '6.2',
            'nombre': 'Auditoría interna periódica',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '6.3',
            'nombre': 'Indicadores de desempeño',
            'complejidad': 'MEDIA',
            'es_mandatorio': False,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
    'SA': [
        {
            'codigo': '7.1',
            'nombre': 'Protocolos de prevención de infecciones',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '7.2',
            'nombre': 'Reporte y análisis de eventos adversos',
            'complejidad': 'ALTA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
        {
            'codigo': '7.3',
            'nombre': 'Identificación y manejo de riesgos',
            'complejidad': 'MEDIA',
            'es_mandatorio': True,
            'aplica_todos': True,
            'requiere_evidencia_documental': True,
        },
    ],
}

# Crear criterios
criterios_total = 0
for codigo_estandar, criterios in criterios_por_estandar.items():
    estandar = estandares_creados[codigo_estandar]
    print(f"\n  ESTÁNDAR {codigo_estandar} - {estandar.nombre}:")
    
    for criterio_data in criterios:
        criterio, created = Criterio.objects.get_or_create(
            estandar=estandar,
            codigo=criterio_data['codigo'],
            defaults={
                'nombre': criterio_data['nombre'],
                'complejidad': criterio_data['complejidad'],
                'es_mandatorio': criterio_data['es_mandatorio'],
                'aplica_todos': criterio_data['aplica_todos'],
                'requiere_evidencia_documental': criterio_data['requiere_evidencia_documental'],
                'estado': True,
            }
        )
        criterios_total += 1
        status = '  ✓' if created else '  ⊕'
        mandatorio_icon = '✓' if criterio_data['es_mandatorio'] else '○'
        print(f"    {status} {criterio_data['codigo']}: {criterio_data['nombre']} "
              f"[{criterio_data['complejidad']}] M:{mandatorio_icon}")

print("\n" + "=" * 80)
print(f"RESUMEN FINAL")
print("=" * 80)
print(f"✓ Estándares cargados: {len(estandares_creados)}")
print(f"✓ Criterios cargados: {criterios_total}")
print(f"✓ Total de registros: {len(estandares_creados) + criterios_total}")
print("\n" + "=" * 80)
print("DATOS CARGADOS EXITOSAMENTE")
print("=" * 80)

# ============================================================================
# 3. DOCUMENTOS NORMATIVOS (Referencias - Opcionales)
# ============================================================================

print("\n" + "=" * 80)
print("CARGANDO DOCUMENTOS NORMATIVOS")
print("=" * 80)

documentos_data = [
    {
        'titulo': 'Resolución 3100 de 2019 - Modificada por la Resolución 1533 de 2021',
        'tipo': 'RESOLUCION',
        'numero_referencia': '3100/2019',
        'descripcion': 'Estándares para acreditación de instituciones prestadoras de servicios de salud',
    },
    {
        'titulo': 'Manual de Estándares de Habilitación - Ministerio de Salud',
        'tipo': 'MANUAL',
        'numero_referencia': 'MINSALUD-2019',
        'descripcion': 'Guía técnica para implementación de estándares',
    },
]

for doc_data in documentos_data:
    documento, created = DocumentoNormativo.objects.get_or_create(
        numero_referencia=doc_data['numero_referencia'],
        defaults={
            'titulo': doc_data['titulo'],
            'tipo': doc_data['tipo'],
            'descripcion': doc_data.get('descripcion', ''),
        }
    )
    status = '✓ CREADO' if created else '⊕ YA EXISTE'
    print(f"{status}: {doc_data['numero_referencia']} - {doc_data['titulo']}")

print("\n¡CARGA COMPLETADA! Los datos están listos para usar.")
