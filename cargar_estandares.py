#!/usr/bin/env python
"""
Script para cargar los 7 estándares de Resolución 3100.
Se ejecuta con: python cargar_estandares.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from normativity.models import Estandar, Criterio, DocumentoNormativo

print("=" * 80)
print("CARGANDO ESTÁNDARES DE RESOLUCIÓN 3100")
print("=" * 80)

# Datos de estándares
estandares_data = [
    ('TH', 'Talento Humano', 'Recursos humanos: disponibilidad, competencia, capacitación'),
    ('INF', 'Infraestructura Física', 'Instalaciones, equipos, servicios básicos, seguridad'),
    ('DOT', 'Dotación y Medicamentos', 'Disponibilidad, almacenamiento, control de medicamentos'),
    ('PO', 'Procesos Organizacionales', 'Gestión administrativo-financiera e información'),
    ('RS', 'Relacionamiento', 'Gestión de relaciones con usuarios y referencia'),
    ('GI', 'Garantía de Calidad', 'Mejora continua, satisfacción del usuario'),
    ('SA', 'Seguridad del Paciente', 'Prevención de eventos adversos e infecciones'),
]

estandares_creados = {}

for codigo, nombre, descripcion in estandares_data:
    estandar, created = Estandar.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'descripcion': descripcion,
            'version_resolucion': '3100/2019',
            'estado': True,
        }
    )
    estandares_creados[codigo] = estandar
    status = 'CREADO' if created else 'EXISTE'
    print(f"[{status}] {codigo}: {nombre}")

print("\n" + "=" * 80)
print("CARGANDO CRITERIOS")
print("=" * 80)

# Datos de criterios
criterios_data = {
    'TH': [
        ('1.1', 'Personal médico especializado', 'ALTA', True, True, True),
        ('1.2', 'Capacitación continua', 'MEDIA', True, True, True),
        ('1.3', 'Evaluación de competencias', 'MEDIA', True, False, True),
    ],
    'INF': [
        ('2.1', 'Espacios adecuados', 'ALTA', True, True, False),
        ('2.2', 'Servicios básicos', 'ALTA', True, True, False),
        ('2.3', 'Mantenimiento preventivo', 'MEDIA', False, True, True),
    ],
    'DOT': [
        ('3.1', 'Medicamentos esenciales', 'ALTA', True, True, True),
        ('3.2', 'Control y almacenamiento', 'ALTA', True, True, False),
        ('3.3', 'Inventario actualizado', 'MEDIA', True, True, True),
    ],
    'PO': [
        ('4.1', 'Documentacion de procesos', 'MEDIA', True, True, True),
        ('4.2', 'Gestion financiera', 'MEDIA', True, True, True),
        ('4.3', 'Sistemas de informacion', 'MEDIA', False, True, False),
    ],
    'RS': [
        ('5.1', 'Accesibilidad a servicios', 'MEDIA', True, True, False),
        ('5.2', 'Satisfaccion del usuario', 'BAJA', False, True, True),
        ('5.3', 'Referencia y contrarreferencia', 'MEDIA', True, True, True),
    ],
    'GI': [
        ('6.1', 'Planes de mejora continua', 'MEDIA', True, True, True),
        ('6.2', 'Auditoria interna', 'MEDIA', True, True, True),
        ('6.3', 'Indicadores de desempeño', 'MEDIA', False, True, True),
    ],
    'SA': [
        ('7.1', 'Prevencion de infecciones', 'ALTA', True, True, True),
        ('7.2', 'Reporte de eventos adversos', 'ALTA', True, True, True),
        ('7.3', 'Identificacion de riesgos', 'MEDIA', True, True, True),
    ],
}

criterios_total = 0

for codigo_est, criterios in criterios_data.items():
    estandar = estandares_creados[codigo_est]
    print(f"\n{codigo_est} - {estandar.nombre}:")
    
    for codigo, nombre, complejidad, mandatorio, aplica, evidencia in criterios:
        criterio, created = Criterio.objects.get_or_create(
            estandar=estandar,
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'complejidad': complejidad,
                'es_mandatorio': mandatorio,
                'aplica_todos': aplica,
                'requiere_evidencia_documental': evidencia,
                'estado': True,
            }
        )
        criterios_total += 1
        status = 'OK' if created else 'YA'
        print(f"  [{status}] {codigo}: {nombre}")

print("\n" + "=" * 80)
print(f"RESUMEN: {len(estandares_creados)} Estandares + {criterios_total} Criterios")
print("=" * 80)
