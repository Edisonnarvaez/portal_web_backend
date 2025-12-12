"""
habilitacion/sample_data.py

Script para crear datos de ejemplo de autoevaluaciones y cumplimientos.

USO:
  python manage.py shell
  exec(open('habilitacion/sample_data.py', encoding='utf-8').read())
"""

import os
import sys
import django
from datetime import date, timedelta
from random import choice, randint

if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

from habilitacion.models import (
    DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento
)
from normativity.models import Criterio
from companies.models import Company

print("\n" + "="*80)
print("  CREAR DATOS DE EJEMPLO")
print("="*80)

# ============================================================================
# 1. CREAR COMPANY EJEMPLO
# ============================================================================

print("\n1️⃣  CREAR EMPRESA DE EJEMPLO")
print("-" * 80)

company, created = Company.objects.get_or_create(
    nombre="Clínica Integral de Salud",
    defaults={
        'razon_social': "Clínica Integral de Salud S.A.S.",
        'nit': "9009876543",
        'email': "info@clinica.com",
        'telefono': "312 555 1234",
        'estado': True,
    }
)

if created:
    print(f"✓ Empresa creada: {company.nombre}")
else:
    print(f"⊕ Empresa existente: {company.nombre}")

# ============================================================================
# 2. CREAR DATOS PRESTADOR
# ============================================================================

print("\n2️⃣  CREAR DATOS DE PRESTADOR")
print("-" * 80)

datos_prestador, created = DatosPrestador.objects.get_or_create(
    codigo_reps="9009876543",
    defaults={
        'company': company,
        'clase_prestador': 'IPS',
        'estado_habilitacion': 'EN_PROCESO',
        'fecha_inscripcion': date(2020, 1, 15),
        'aseguradora_pep': "Seguros La Confianza",
        'numero_poliza': "POL-2024-001234",
        'vigencia_poliza': date(2025, 12, 31),
    }
)

if created:
    print(f"✓ Datos prestador creados: {datos_prestador.codigo_reps}")
else:
    print(f"⊕ Datos prestador existentes: {datos_prestador.codigo_reps}")

# ============================================================================
# 3. CREAR SERVICIOS DE SEDE
# ============================================================================

print("\n3️⃣  CREAR SERVICIOS DE SEDE")
print("-" * 80)

servicios_data = [
    {
        'codigo_servicio': 'EMERG',
        'nombre_servicio': 'Servicio de Emergencias',
        'modalidad': 'PRESENCIAL',
        'complejidad': 'ALTA',
    },
    {
        'codigo_servicio': 'LAB',
        'nombre_servicio': 'Laboratorio Clínico',
        'modalidad': 'PRESENCIAL',
        'complejidad': 'MEDIA',
    },
    {
        'codigo_servicio': 'IMAG',
        'nombre_servicio': 'Imagenología',
        'modalidad': 'PRESENCIAL',
        'complejidad': 'ALTA',
    },
]

servicios = []
for serv_data in servicios_data:
    serv, created = ServicioSede.objects.get_or_create(
        codigo_servicio=serv_data['codigo_servicio'],
        datos_prestador=datos_prestador,
        defaults={
            'nombre_servicio': serv_data['nombre_servicio'],
            'modalidad': serv_data['modalidad'],
            'complejidad': serv_data['complejidad'],
            'estado_habilitacion': 'EN_PROCESO',
        }
    )
    servicios.append(serv)
    
    if created:
        print(f"  ✓ Servicio creado: {serv.nombre_servicio}")
    else:
        print(f"  ⊕ Servicio existente: {serv.nombre_servicio}")

# ============================================================================
# 4. CREAR AUTOEVALUACIÓN
# ============================================================================

print("\n4️⃣  CREAR AUTOEVALUACIÓN")
print("-" * 80)

auto, created = Autoevaluacion.objects.get_or_create(
    datos_prestador=datos_prestador,
    periodo=2024,
    version=1,
    defaults={
        'numero_autoevaluacion': f"AUT-{datos_prestador.codigo_reps}-2024",
        'fecha_vencimiento': date(2025, 12, 31),
        'estado': 'EN_PROCESO',
        'observaciones': 'Evaluación inicial del sistema de habilitación',
    }
)

if created:
    print(f"✓ Autoevaluación creada: {auto.numero_autoevaluacion}")
else:
    print(f"⊕ Autoevaluación existente: {auto.numero_autoevaluacion}")

# ============================================================================
# 5. CREAR CUMPLIMIENTOS
# ============================================================================

print("\n5️⃣  CREAR CUMPLIMIENTOS")
print("-" * 80)

criterios = Criterio.objects.all().order_by('estandar__codigo', 'codigo')

if not criterios.exists():
    print("❌ No hay criterios en la BD")
    print("Ejecuta primero: normativity/fixtures_loader.py")
    sys.exit(1)

print(f"\nCreando {len(servicios)} servicios × {criterios.count()} criterios = "
      f"{len(servicios) * criterios.count()} cumplimientos\n")

resultados_posibles = ['CUMPLE', 'NO_CUMPLE', 'PARCIALMENTE', 'NO_APLICA']
creados = 0
duplicados = 0
estandar_actual = None

for criterio in criterios:
    # Mostrar progreso
    if estandar_actual != criterio.estandar.codigo:
        estandar_actual = criterio.estandar.codigo
        print(f"  📍 Estándar {estandar_actual}: {criterio.estandar.nombre}")
    
    for servicio in servicios:
        # Resultado aleatorio pero más tendiente a CUMPLE
        resultado_aleatorio = choice([
            'CUMPLE',           # 60%
            'CUMPLE',
            'CUMPLE',
            'NO_CUMPLE',       # 20%
            'NO_CUMPLE',
            'PARCIALMENTE',    # 15%
            'PARCIALMENTE',
            'NO_APLICA',       # 5%
        ])
        
        cumplimiento, created = Cumplimiento.objects.get_or_create(
            autoevaluacion=auto,
            servicio_sede=servicio,
            criterio=criterio,
            defaults={
                'cumple': resultado_aleatorio,
                'hallazgo': f"Evaluación del criterio {criterio.codigo}: {criterio.nombre}",
                'plan_mejora': (
                    f"Plan de mejora para {criterio.nombre}" 
                    if resultado_aleatorio in ['NO_CUMPLE', 'PARCIALMENTE'] 
                    else None
                ),
            }
        )
        
        if created:
            creados += 1
            print(f"    ✓ {criterio.codigo} → {servicio.nombre_servicio[:30]:30} "
                  f"{resultado_aleatorio:15}", end='\n')
        else:
            duplicados += 1

# ============================================================================
# RESUMEN Y ESTADÍSTICAS
# ============================================================================

print("\n" + "="*80)
print("  RESUMEN DE DATOS CREADOS")
print("="*80)

total_cumplimientos = auto.cumplimientos.count()
porcentaje = auto.porcentaje_cumplimiento()

print(f"\n  AUTOEVALUACIÓN")
print(f"  ├─ Número: {auto.numero_autoevaluacion}")
print(f"  ├─ Período: {auto.periodo}")
print(f"  ├─ Versión: {auto.version}")
print(f"  ├─ Estado: {auto.estado}")
print(f"  └─ Vencimiento: {auto.fecha_vencimiento}")

print(f"\n  DATOS PRESTADOR")
print(f"  ├─ Empresa: {company.nombre}")
print(f"  ├─ Código REPS: {datos_prestador.codigo_reps}")
print(f"  ├─ Clase: {datos_prestador.clase_prestador}")
print(f"  └─ Estado Habilitación: {datos_prestador.estado_habilitacion}")

print(f"\n  SERVICIOS")
print(f"  └─ Total: {len(servicios)}")
for serv in servicios:
    print(f"      • {serv.nombre_servicio} ({serv.complejidad})")

print(f"\n  CUMPLIMIENTOS")
print(f"  ├─ Creados: {creados}")
print(f"  ├─ Duplicados: {duplicados}")
print(f"  ├─ Total: {total_cumplimientos}")
print(f"  └─ Porcentaje: {porcentaje:.1f}%")

# Desglose
print(f"\n  DESGLOSE POR RESULTADO")
for resultado in ['CUMPLE', 'NO_CUMPLE', 'PARCIALMENTE', 'NO_APLICA']:
    count = auto.cumplimientos.filter(cumple=resultado).count()
    if count > 0:
        pct = (count / total_cumplimientos * 100) if total_cumplimientos > 0 else 0
        print(f"  ├─ {resultado:20} {count:4} ({pct:5.1f}%)")

# Desglose por estándar
print(f"\n  CUMPLIMIENTO POR ESTÁNDAR")
from normativity.models import Estandar
for estandar in Estandar.objects.all():
    criterios_std = estandar.criterios.all()
    cumpl_std = auto.cumplimientos.filter(criterio__in=criterios_std)
    cumple_std = cumpl_std.filter(cumple='CUMPLE').count()
    total_std = cumpl_std.count()
    pct_std = (cumple_std / total_std * 100) if total_std > 0 else 0
    print(f"  ├─ {estandar.codigo:3} {estandar.nombre:35} {cumple_std:3}/{total_std:3} ({pct_std:5.1f}%)")

# ============================================================================
# ACCIONES SIGUIENTES
# ============================================================================

print("\n" + "="*80)
print("  PRÓXIMOS PASOS")
print("="*80)

print(f"""
  1. VER LA AUTOEVALUACIÓN EN ADMIN:
     http://localhost:8000/admin/habilitacion/autoevaluacion/{auto.pk}/change/
     
  2. VER CUMPLIMIENTOS EN ADMIN:
     http://localhost:8000/admin/habilitacion/cumplimiento/
     ?autoevaluacion__numero_autoevaluacion={auto.numero_autoevaluacion}
     
  3. VER EN DJANGO SHELL:
     from habilitacion.models import Autoevaluacion
     auto = Autoevaluacion.objects.get(pk={auto.pk})
     print(f"Cumplimientos: {{auto.cumplimientos.count()}}")
     print(f"Porcentaje: {{auto.porcentaje_cumplimiento()}}%")
     
  4. MODIFICAR DATOS:
     - Cambiar resultados de cumplimientos
     - Agregar documentos de evidencia
     - Agregar planes de mejora
     - Cambiar estado de autoevaluación

""")

print("="*80)
print("  ✓ DATOS DE EJEMPLO CREADOS EXITOSAMENTE")
print("="*80 + "\n")
