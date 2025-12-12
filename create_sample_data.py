#!/usr/bin/env python
"""
Script para crear datos de ejemplo de autoevaluaciones y cumplimientos.
Ejecutar con: python manage.py shell < create_sample_data.py
"""

from datetime import date, timedelta
from random import choice, randint
from habilitacion.models import (
    DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento
)
from normativity.models import Criterio
from companies.models import Company, Headquarters

print("\n" + "="*80)
print("  CREAR DATOS DE EJEMPLO")
print("="*80 + "\n")

# 1. Crear Company
try:
    company = Company.objects.create(
        name="Clínica Integral de Salud",
        nit="9009876543",
        legalRepresentative="Dr. Carlos González",
        phone="+57 1 5551234",
        address="Cra 5 # 32-45, Bogotá",
        contactEmail="info@clinicaintegral.com",
        foundationDate=date(2010, 3, 15),
        status=True
    )
    print(f"✅ Company creada: {company.name}")
except Exception as e:
    company = Company.objects.get(nit="9009876543")
    print(f"⚠️  Company ya existe: {company.name}")

# 2. Crear Headquarters
try:
    headquarters = Headquarters.objects.create(
        company=company,
        habilitationCode="SEDE-PRINCIPAL-001",
        name="Sede Principal",
        departament="Bogotá",
        city="Bogotá",
        address="Cra 5 # 32-45",
        habilitationDate=date(2020, 1, 15),
        status=True
    )
    print(f"✅ Headquarters creada: {headquarters.name}")
except Exception as e:
    headquarters = Headquarters.objects.get(habilitationCode="SEDE-PRINCIPAL-001")
    print(f"⚠️  Headquarters ya existe: {headquarters.name}")

# 3. Crear DatosPrestador
try:
    datos_prestador = DatosPrestador.objects.create(
        headquarters=headquarters,
        codigo_reps="9009876543-001",
        clase_prestador="IPS",
        estado_habilitacion="HABILITADA",
        fecha_inscripcion_reps=date(2020, 1, 15),
        fecha_renovacion=date(2024, 1, 15),
        fecha_vencimiento=date(2025, 12, 31),
        aseguradora="Seguros La Confianza",
        numero_poliza="POL-2024-001234",
        vigencia_responsabilidad_civil=date(2025, 12, 31),
        entidad_verificadora="SUPERSALUD"
    )
    print(f"✅ DatosPrestador creado: {datos_prestador.codigo_reps}")
except Exception as e:
    datos_prestador = DatosPrestador.objects.get(codigo_reps="9009876543-001")
    print(f"⚠️  DatosPrestador ya existe: {datos_prestador.codigo_reps}")

# 4. Crear ServicioSede
servicios_lista = [
    ("Urgencias", "Servicio de emergencias 24/7"),
    ("Laboratorio", "Análisis clínicos y diagnóstico"),
    ("Imagenología", "Radiología, ecografía, tomografía")
]

servicios_creados = []
for codigo, nombre in servicios_lista:
    try:
        servicio = ServicioSede.objects.create(
            datos_prestador=datos_prestador,
            codigo=codigo,
            nombre=nombre,
            descripcion=f"Servicio de {nombre.lower()}",
            estado=True
        )
        servicios_creados.append(servicio)
        print(f"  ✅ Servicio: {servicio.nombre}")
    except Exception as e:
        servicio = ServicioSede.objects.get(codigo=codigo, datos_prestador=datos_prestador)
        servicios_creados.append(servicio)
        print(f"  ⚠️  Servicio ya existe: {servicio.nombre}")

print(f"\nTotal servicios: {len(servicios_creados)}")

# 5. Crear Autoevaluación
try:
    autoevaluacion = Autoevaluacion.objects.create(
        datos_prestador=datos_prestador,
        periodo=2024,
        version=1,
        fecha_inicio=date(2024, 1, 15),
        fecha_limite=date(2024, 3, 31),
        responsable=None
    )
    print(f"\n✅ Autoevaluación creada: {autoevaluacion.numero_autoevaluacion}")
except Exception as e:
    autoevaluaciones = Autoevaluacion.objects.filter(
        datos_prestador=datos_prestador,
        periodo=2024,
        version=1
    )
    if autoevaluaciones.exists():
        autoevaluacion = autoevaluaciones.first()
        print(f"\n⚠️  Autoevaluación ya existe: {autoevaluacion.numero_autoevaluacion}")
    else:
        print(f"\n❌ Error creando autoevaluación: {e}")
        raise

# 6. Crear Cumplimientos
criterios = Criterio.objects.all()
if not criterios.exists():
    print("\n⚠️  No hay criterios en la base de datos.")
    print("   Ejecuta primero: python manage.py shell < normativity/fixtures_loader.py")
else:
    cumplimientos_creados = 0
    resultados = ['CUMPLE', 'NO_CUMPLE', 'PARCIALMENTE', 'NO_APLICA']
    
    for servicio in servicios_creados:
        for criterio in criterios[:7]:  # Crear algunos cumplimientos
            try:
                cumplimiento, created = Cumplimiento.objects.get_or_create(
                    autoevaluacion=autoevaluacion,
                    servicio_sede=servicio,
                    criterio=criterio,
                    defaults={
                        'cumple': choice(resultados),
                        'responsable': "Dr. Carlos González",
                        'fecha_compromiso': date.today() + timedelta(days=30)
                    }
                )
                if created:
                    cumplimientos_creados += 1
            except Exception as e:
                print(f"  Error en cumplimiento {criterio.codigo}: {e}")

    print(f"\n✅ Cumplimientos creados: {cumplimientos_creados}")

# 7. Resumen final
print("\n" + "="*80)
print("  RESUMEN DE DATOS CREADOS")
print("="*80)
print(f"Company: {company.name} (NIT: {company.nit})")
print(f"Headquarters: {headquarters.name} ({headquarters.departament})")
print(f"DatosPrestador: {datos_prestador.codigo_reps} ({datos_prestador.estado_habilitacion})")
print(f"Servicios: {len(servicios_creados)}")
print(f"Autoevaluación: {autoevaluacion.numero_autoevaluacion}")
print(f"Cumplimientos: {Cumplimiento.objects.filter(autoevaluacion=autoevaluacion).count()}")
print("="*80 + "\n")
