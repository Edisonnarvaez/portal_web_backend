#!/usr/bin/env python
"""
Script para crear datos de prueba del módulo de habilitación.
Crea: Estándares, Criterios, DatosPrestador, ServiciosSede, Autoevaluaciones, Cumplimientos.

Ejecutar con:
  cd D:\\portal_web_backend
  .\\venv\\Scripts\\python.exe manage.py shell < create_habilitacion_data.py

Es idempotente: si los registros ya existen, los reutiliza sin duplicar.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from datetime import date, timedelta
from django.contrib.auth import get_user_model
from companies.models import Company, Headquarters
from normativity.models import Estandar, Criterio
from habilitacion.models import DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento

User = get_user_model()

print("\n" + "=" * 80)
print("  CREAR DATOS DE PRUEBA - MÓDULO DE HABILITACIÓN")
print("=" * 80 + "\n")

# ─────────────────────────────────────────────
#  1. OBTENER DATOS BASE
# ─────────────────────────────────────────────
print("── 1. OBTENER DATOS BASE ──")

# Obtener Company
company = Company.objects.filter(nit="900123456-1").first()
if not company:
    print("  ⚠️  No se encontró la Company. Ejecuta primero: create_sample_data.py")
    exit(1)
print(f"  ✅ Company: {company.name}")

# Obtener Sedes
sedes = Headquarters.objects.filter(company=company)
if not sedes.exists():
    print("  ⚠️  No se encontraron Sedes. Ejecuta primero: create_sample_data.py")
    exit(1)
print(f"  ✅ Sedes encontradas: {sedes.count()}")

# Obtener Usuario Admin
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    print("  ⚠️  No se encontró un superusuario.")
    admin_user = User.objects.create_superuser(
        username="admin_habilitacion",
        email="admin.habilitacion@redmedicronips.com.co",
        password="admin123"
    )
    print(f"  ✅ Superusuario creado: {admin_user.username}")
else:
    print(f"  ✅ Usuario Admin: {admin_user.username}")

# ─────────────────────────────────────────────
#  2. CREAR ESTÁNDARES (Resolución 3100/2019)
# ─────────────────────────────────────────────
print("\n── 2. ESTÁNDARES DE HABILITACIÓN ──")

estandares_data = [
    {
        "codigo": "TH",
        "nombre": "Talento Humano",
        "descripcion": "Garantizar disponibilidad de personal competente, capacitado y suficiente para prestar servicios de calidad."
    },
    {
        "codigo": "INF",
        "nombre": "Infraestructura Física",
        "descripcion": "Asegurar que la infraestructura física sea segura, adecuada y accesible para la prestación de servicios."
    },
    {
        "codigo": "DOT",
        "nombre": "Dotación, Medicamentos e Insumos",
        "descripcion": "Garantizar disponibilidad de equipos, medicamentos e insumos necesarios y de calidad."
    },
    {
        "codigo": "PO",
        "nombre": "Procesos Organizacionales",
        "descripcion": "Contar con procesos documentados, implementados y controlados para la prestación de servicios."
    },
    {
        "codigo": "RS",
        "nombre": "Relacionamiento y Sostenibilidad",
        "descripcion": "Mantener relaciones efectivas con usuarios, entidades y la comunidad, asegurando sostenibilidad."
    },
    {
        "codigo": "GI",
        "nombre": "Garantía de Calidad e Información",
        "descripcion": "Implementar sistemas de garantía de calidad y gestión de información para mejora continua."
    },
    {
        "codigo": "SA",
        "nombre": "Seguridad del Paciente y Ambiente",
        "descripcion": "Proteger la seguridad del paciente, personal e instalaciones, previniendo accidentes y eventos adversos."
    },
]

estandares_created = {}
for est_info in estandares_data:
    estandar, created = Estandar.objects.get_or_create(
        codigo=est_info["codigo"],
        defaults={
            "nombre": est_info["nombre"],
            "descripcion": est_info["descripcion"],
            "estado": True,
            "version_resolucion": "3100/2019"
        }
    )
    estandares_created[est_info["codigo"]] = estandar
    tag = "CREADO" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} [{estandar.codigo}] {estandar.nombre} ({tag})")

# ─────────────────────────────────────────────
#  3. CREAR CRITERIOS POR ESTÁNDAR
# ─────────────────────────────────────────────
print("\n── 3. CRITERIOS DE EVALUACIÓN ──")

criterios_data = [
    # Talento Humano (TH)
    {
        "estandar": "TH",
        "codigo": "TH-1.1",
        "nombre": "Disponibilidad de Médicos Especialistas",
        "descripcion": "La IPS cuenta con médicos especialistas en las modalidades y complejidad de sus servicios.",
        "complejidad": "ALTA"
    },
    {
        "estandar": "TH",
        "codigo": "TH-1.2",
        "nombre": "Perfiles y Competencias del Personal",
        "descripcion": "El personal tiene perfiles y competencias acordes con las funciones asignadas.",
        "complejidad": "MEDIA"
    },
    {
        "estandar": "TH",
        "codigo": "TH-1.3",
        "nombre": "Programa de Educación Continua",
        "descripcion": "Existe un programa documentado de educación continua para todo el personal.",
        "complejidad": "MEDIA"
    },
    # Infraestructura Física (INF)
    {
        "estandar": "INF",
        "codigo": "INF-2.1",
        "nombre": "Condiciones de Infraestructura",
        "descripcion": "Las áreas de la IPS cumplen con condiciones de seguridad, higiene y accesibilidad.",
        "complejidad": "ALTA"
    },
    {
        "estandar": "INF",
        "codigo": "INF-2.2",
        "nombre": "Mantenimiento Preventivo",
        "descripcion": "Se realiza mantenimiento preventivo de infraestructura y equipos.",
        "complejidad": "MEDIA"
    },
    # Dotación (DOT)
    {
        "estandar": "DOT",
        "codigo": "DOT-3.1",
        "nombre": "Disponibilidad de Equipos Básicos",
        "descripcion": "La IPS cuenta con equipos mínimos necesarios para sus servicios.",
        "complejidad": "ALTA"
    },
    {
        "estandar": "DOT",
        "codigo": "DOT-3.2",
        "nombre": "Control de Medicamentos e Insumos",
        "descripcion": "Exists control sobre medicamentos, insumos y dispositivos médicos.",
        "complejidad": "MEDIA"
    },
    # Procesos Organizacionales (PO)
    {
        "estandar": "PO",
        "codigo": "PO-4.1",
        "nombre": "Documentación de Procesos",
        "descripcion": "Los procesos están documentados, actualizados y disponibles.",
        "complejidad": "MEDIA"
    },
    {
        "estandar": "PO",
        "codigo": "PO-4.2",
        "nombre": "Protocolos Clínicos",
        "descripcion": "Existen protocolos clínicos basados en evidencia para los servicios.",
        "complejidad": "ALTA"
    },
    # Seguridad del Paciente (SA)
    {
        "estandar": "SA",
        "codigo": "SA-7.1",
        "nombre": "Programa de Seguridad del Paciente",
        "descripcion": "Existe un programa integral de seguridad del paciente implementado.",
        "complejidad": "ALTA"
    },
    {
        "estandar": "SA",
        "codigo": "SA-7.2",
        "nombre": "Reporte de Eventos Adversos",
        "descripcion": "Se reportan y analizan eventos adversos para la mejora continua.",
        "complejidad": "MEDIA"
    },
]

criterios_created = {}
for crit_info in criterios_data:
    criterio, created = Criterio.objects.get_or_create(
        codigo=crit_info["codigo"],
        defaults={
            "estandar": estandares_created[crit_info["estandar"]],
            "nombre": crit_info["nombre"],
            "descripcion": crit_info["descripcion"],
            "complejidad": crit_info["complejidad"]
        }
    )
    criterios_created[crit_info["codigo"]] = criterio
    tag = "CREADO" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} [{criterio.codigo}] {criterio.nombre[:40]}... ({tag})")

print(f"\n  Total criterios: {len(criterios_created)}")

# ─────────────────────────────────────────────
#  4. CREAR DATOS DE PRESTADOR (Por Sede)
# ─────────────────────────────────────────────
print("\n── 4. DATOS DE PRESTADOR (DatosPrestador) ──")

datos_prestador_created = {}
for i, sede in enumerate(sedes, 1):
    # Usar get_or_create con headquarters (OneToOne)
    # Si ya existe, se reutiliza; si no, se crea
    codigo_reps = f"52001-IPS-000{i}"
    
    datos, created = DatosPrestador.objects.get_or_create(
        headquarters=sede,
        defaults={
            "codigo_reps": codigo_reps,
            "clase_prestador": "IPS",
            "estado_habilitacion": "EN_PROCESO",
            "fecha_inscripcion": date(2023, 1, 15),
            "fecha_renovacion": date(2024, 1, 15),
            "fecha_vencimiento_habilitacion": date(2025, 1, 14),
            "aseguradora_pep": "AXA Seguros Colombia",
            "numero_poliza": f"POL-2024-{i:05d}",
            "vigencia_poliza": date(2025, 12, 31),
            "usuario_responsable": admin_user,
        }
    )
    datos_prestador_created[sede.id] = datos
    tag = "CREADO" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} [{datos.codigo_reps}] {sede.name} ({tag})")

# ─────────────────────────────────────────────
#  5. CREAR SERVICIOS DE SEDE
# ─────────────────────────────────────────────
print("\n── 5. SERVICIOS DE SEDE (ServicioSede) ──")

servicios_data = [
    # Modalidades de servicio
    {
        "codigo": "URG-001",
        "nombre": "Urgencias - Nivel I",
        "modalidad": "URGENCIAS",
        "complejidad": "BAJA",
    },
    {
        "codigo": "CNS-001",
        "nombre": "Consulta Externa - Medicina General",
        "modalidad": "AMBULATORIA",
        "complejidad": "BAJA",
    },
    {
        "codigo": "INT-001",
        "nombre": "Hospitalización - Medicina Interna",
        "modalidad": "INTRAMURAL",
        "complejidad": "MEDIA",
    },
    {
        "codigo": "TEL-001",
        "nombre": "Telemedicina - Teleconsulta",
        "modalidad": "TELEMEDICINA",
        "complejidad": "BAJA",
    },
    {
        "codigo": "AMB-001",
        "nombre": "Servicio de Ambulancia",
        "modalidad": "AMBULANCIA",
        "complejidad": "MEDIA",
    },
]

servicios_creados = {}
servicios_count = 0
for datos_id, datos in datos_prestador_created.items():
    for srv_info in servicios_data:
        codigo_unico = f"{srv_info['codigo']}-{datos.codigo_reps}"
        
        servicio, created = ServicioSede.objects.get_or_create(
            codigo_servicio=codigo_unico,
            defaults={
                "prestador": datos,
                "nombre_servicio": srv_info["nombre"],
                "descripcion": f"Servicio {srv_info['nombre']} habilitado en {datos.headquarters.name}",
                "modalidad": srv_info["modalidad"],
                "complejidad": srv_info["complejidad"],
                "estado_habilitacion": "EN_PROCESO",
                "fecha_habilitacion": date(2023, 6, 1),
                "fecha_vencimiento": date(2025, 5, 31),
            }
        )
        if created:
            servicios_creados[codigo_unico] = servicio
            servicios_count += 1
        tag = "CREADO" if created else "ya existe"
        print(f"  {'✅' if created else '⏭️ '} [{servicio.codigo_servicio}] {servicio.nombre_servicio[:35]}... [{servicio.modalidad}] ({tag})")

print(f"\n  Total servicios: {servicios_count}")

# ─────────────────────────────────────────────
#  6. CREAR AUTOEVALUACIONES
# ─────────────────────────────────────────────
print("\n── 6. AUTOEVALUACIONES ──")

periodos = [2024, 2025]
autoevaluaciones_created = {}

for periodo in periodos:
    for datos_id, datos in datos_prestador_created.items():
        numero_auto = f"AUT-{datos.codigo_reps}-{periodo}"
        
        # Calcular fecha de vencimiento (1 año después del inicio)
        fecha_inicio = date(periodo, 1, 1)
        fecha_vencimiento = date(periodo + 1, 12, 31)
        
        # Determinar estado según el período
        if periodo == 2024:
            estado = "VALIDADA"
            fecha_completacion = date(2024, 12, 31)
        else:
            estado = "EN_CURSO"
            fecha_completacion = None
        
        autoevaluacion, created = Autoevaluacion.objects.get_or_create(
            numero_autoevaluacion=numero_auto,
            defaults={
                "datos_prestador": datos,
                "periodo": periodo,
                "version": 1,
                "fecha_inicio": fecha_inicio,
                "fecha_completacion": fecha_completacion,
                "fecha_vencimiento": fecha_vencimiento,
                "estado": estado,
                "usuario_responsable": admin_user,
                "observaciones": f"Autoevaluación {periodo} de {datos.headquarters.name}",
            }
        )
        autoevaluaciones_created[numero_auto] = autoevaluacion
        tag = "CREADA" if created else "ya existe"
        print(f"  {'✅' if created else '⏭️ '} {autoevaluacion.numero_autoevaluacion} [{autoevaluacion.estado}] ({tag})")

# ─────────────────────────────────────────────
#  7. CREAR CUMPLIMIENTOS
# ─────────────────────────────────────────────
print("\n── 7. CUMPLIMIENTOS DE CRITERIOS ──")

resultados_distribucion = [
    ("CUMPLE", 0.6),           # 60% cumple
    ("PARCIALMENTE", 0.25),    # 25% parcialmente
    ("NO_CUMPLE", 0.10),       # 10% no cumple
    ("NO_APLICA", 0.05),       # 5% no aplica
]

cumplimientos_count = 0
for numero_auto, autoevaluacion in autoevaluaciones_created.items():
    # Obtener servicios del prestador
    servicios = autoevaluacion.datos_prestador.servicios_salud.all()
    
    # Para cada servicio, crear cumplimiento por criterio
    for idx_srv, servicio in enumerate(servicios):
        for idx_crit, criterio in enumerate(criterios_created.values()):
            
            # Variar resultado según criterio para simular realidad
            resultado = "CUMPLE"
            if idx_crit % 7 == 0:
                resultado = "NO_CUMPLE"
            elif idx_crit % 5 == 0:
                resultado = "PARCIALMENTE"
            elif idx_crit % 11 == 0:
                resultado = "NO_APLICA"
            
            key_unico = f"{numero_auto}_{servicio.id}_{criterio.id}"
            
            cumplimiento, created = Cumplimiento.objects.get_or_create(
                autoevaluacion=autoevaluacion,
                servicio_prestador=servicio,
                criterio=criterio,
                defaults={
                    "cumple": resultado,
                    "hallazgo": f"Hallazgo para {criterio.nombre} en {servicio.nombre_servicio}" if resultado != "CUMPLE" else None,
                    "plan_mejora": f"Plan de mejora: Implementar {criterio.nombre.lower()}" if resultado != "CUMPLE" else None,
                    "responsable_mejora": admin_user if resultado != "CUMPLE" else None,
                    "fecha_compromiso": date.today() + timedelta(days=90) if resultado != "CUMPLE" else None,
                }
            )
            
            if created:
                cumplimientos_count += 1
            
            if created:
                status_icon = "✅"
            else:
                status_icon = "⏭️ "
            
            if created and cumplimientos_count <= 5:  # Mostrar solo los primeros 5
                print(f"  {status_icon} {autoevaluacion.numero_autoevaluacion} -> "
                      f"{servicio.nombre_servicio[:20]}... -> {criterio.codigo} [{resultado}]")
            elif created and cumplimientos_count == 6:
                print(f"  ... (mostrando primeros 5 cumplimientos creados)")

print(f"\n  Total cumplimientos: {cumplimientos_count}")

# ─────────────────────────────────────────────
#  8. ESTADÍSTICAS Y RESUMEN
# ─────────────────────────────────────────────
print("\n" + "=" * 80)
print("  RESUMEN DE DATOS CREADOS")
print("=" * 80)
print(f"  Estándares:                {Estandar.objects.count()}")
print(f"  Criterios:                 {Criterio.objects.count()}")
print(f"  Datos de Prestador:        {DatosPrestador.objects.count()}")
print(f"  Servicios de Sede:         {ServicioSede.objects.count()}")
print(f"  Autoevaluaciones:          {Autoevaluacion.objects.count()}")
print(f"  Cumplimientos:             {Cumplimiento.objects.count()}")

# Estadísticas por resultado
print("\n  Distribución de Cumplimientos:")
for resultado in ["CUMPLE", "PARCIALMENTE", "NO_CUMPLE", "NO_APLICA"]:
    count = Cumplimiento.objects.filter(cumple=resultado).count()
    porcentaje = (count / Cumplimiento.objects.count() * 100) if Cumplimiento.objects.count() > 0 else 0
    print(f"    • {resultado:15} {count:4} ({porcentaje:5.1f}%)")

# Verificar autoevaluaciones más recientes
print("\n  Autoevaluaciones Activas (2025):")
auto_2025 = Autoevaluacion.objects.filter(periodo=2025)
for auto in auto_2025[:3]:
    porcentaje = auto.porcentaje_cumplimiento()
    print(f"    • {auto.numero_autoevaluacion} - {auto.datos_prestador.headquarters.name}")
    print(f"      Estado: {auto.estado} | Cumplimiento: {porcentaje}%")

print("=" * 80)
print("  ✅ Datos de habilitación listos para pruebas.")
print("=" * 80 + "\n")
