#!/usr/bin/env python
"""
Script para crear datos iniciales de prueba.
Crea: Apps, Roles, Company, Headquarters, Departments, ProcessTypes, Processes.

Ejecutar con:
  cd D:\\portal_web_backend
  .\\venv\\Scripts\\python.exe manage.py shell < create_sample_data.py

Es idempotente: si los registros ya existen, los reutiliza sin duplicar.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from datetime import date
from django.contrib.auth import get_user_model
from users.models import App, Role
from companies.models import Company, Headquarters, Department, ProcessType, Process

User = get_user_model()

print("\n" + "=" * 80)
print("  CREAR DATOS INICIALES DE PRUEBA")
print("=" * 80 + "\n")

# ─────────────────────────────────────────────
#  1. APPS
# ─────────────────────────────────────────────
print("── 1. APPS ──")

apps_data = [
    "habilitacion",
    "indicadores",
    "procesos",
    "auditorias",
    "mejoras",
    "normatividad",
    "administracion",
]

apps_created = {}
for app_name in apps_data:
    app_obj, created = App.objects.get_or_create(name=app_name)
    apps_created[app_name] = app_obj
    tag = "CREADA" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} App: {app_name} ({tag})")

# ─────────────────────────────────────────────
#  2. ROLES (vinculados a Apps)
# ─────────────────────────────────────────────
print("\n── 2. ROLES ──")

roles_data = [
    # (nombre_rol, app_name)
    ("admin",     "administracion"),
    ("Coordinador",       "habilitacion"),
    ("Auditor",           "auditorias"),
    ("Auditor Lider",     "auditorias"),
    ("Gestor Calidad",    "procesos"),
    ("Analista",          "indicadores"),
    ("Consultor",         "normatividad"),
    ("Coordinador Mejora","mejoras"),
    ("Visualizador",      "administracion"),
]

roles_created = {}
for role_name, app_name in roles_data:
    app_obj = apps_created[app_name]
    role_obj, created = Role.objects.get_or_create(name=role_name, app=app_obj)
    roles_created[role_name] = role_obj
    tag = "CREADO" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} Rol: {role_name} -> {app_name} ({tag})")

# ─────────────────────────────────────────────
#  3. COMPANY
# ─────────────────────────────────────────────
print("\n── 3. COMPANY ──")

company, created = Company.objects.get_or_create(
    nit="900123456-1",
    defaults={
        "name": "Red Medicron IPS S.A.S.",
        "legalRepresentative": "Dr. Carlos Andrés Martínez",
        "phone": "+57 602 7301234",
        "address": "Calle 15 # 8-42, Pasto, Nariño",
        "contactEmail": "gerencia@redmedicronips.com.co",
        "foundationDate": date(2012, 6, 10),
        "status": True,
    }
)
tag = "CREADA" if created else "ya existe"
print(f"  {'✅' if created else '⏭️ '} Company: {company.name} (NIT: {company.nit}) ({tag})")

# ─────────────────────────────────────────────
#  4. HEADQUARTERS (Sedes)
# ─────────────────────────────────────────────
print("\n── 4. SEDES (Headquarters) ──")

sedes_data = [
    {
        "habilitationCode": "52001-MED001",
        "name": "Sede Principal - Pasto",
        "departament": "Nariño",
        "city": "Pasto",
        "address": "Calle 15 # 8-42",
        "habilitationDate": date(2013, 1, 15),
    },
    {
        "habilitationCode": "52110-MED002",
        "name": "Sede Buesaco",
        "departament": "Nariño",
        "city": "Buesaco",
        "address": "Carrera 4 # 5-30",
        "habilitationDate": date(2015, 3, 20),
    },
    {
        "habilitationCode": "52356-MED003",
        "name": "Sede Ipiales",
        "departament": "Nariño",
        "city": "Ipiales",
        "address": "Avenida Panamericana Km 2",
        "habilitationDate": date(2018, 7, 1),
    },
    {
        "habilitationCode": "52835-MED004",
        "name": "Sede Tumaco",
        "departament": "Nariño",
        "city": "Tumaco",
        "address": "Calle del Comercio # 12-08",
        "habilitationDate": date(2020, 2, 10),
    },
]

sedes_created = {}
for sede_info in sedes_data:
    hq, created = Headquarters.objects.get_or_create(
        habilitationCode=sede_info["habilitationCode"],
        defaults={
            "company": company,
            "name": sede_info["name"],
            "departament": sede_info["departament"],
            "city": sede_info["city"],
            "address": sede_info["address"],
            "habilitationDate": sede_info["habilitationDate"],
            "status": True,
        }
    )
    sedes_created[sede_info["habilitationCode"]] = hq
    tag = "CREADA" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} Sede: {hq.name} ({hq.habilitationCode}) ({tag})")

sede_principal = sedes_created["52001-MED001"]

# ─────────────────────────────────────────────
#  5. DEPARTMENTS (Áreas)
# ─────────────────────────────────────────────
print("\n── 5. DEPARTAMENTOS / ÁREAS ──")

departamentos_data = [
    {
        "name": "Gerencia General",
        "departmentCode": "GER-001",
        "description": "Dirección general y toma de decisiones estratégicas de la organización.",
    },
    {
        "name": "Dirección Médica",
        "departmentCode": "MED-001",
        "description": "Coordinación de servicios asistenciales y gestión clínica.",
    },
    {
        "name": "Calidad y Habilitación",
        "departmentCode": "CAL-001",
        "description": "Gestión de la calidad, autoevaluación y cumplimiento de estándares de habilitación.",
    },
    {
        "name": "Talento Humano",
        "departmentCode": "THU-001",
        "description": "Gestión del recurso humano, contratación, capacitación y bienestar.",
    },
    {
        "name": "Financiera y Contable",
        "departmentCode": "FIN-001",
        "description": "Gestión financiera, presupuesto, facturación y contabilidad.",
    },
    {
        "name": "Tecnología e Información",
        "departmentCode": "TIC-001",
        "description": "Soporte tecnológico, sistemas de información y comunicaciones.",
    },
    {
        "name": "Enfermería",
        "departmentCode": "ENF-001",
        "description": "Coordinación de servicios de enfermería y cuidado del paciente.",
    },
    {
        "name": "Farmacia",
        "departmentCode": "FAR-001",
        "description": "Gestión de medicamentos, dispositivos médicos e insumos.",
    },
]

departamentos_created = {}
for dept_info in departamentos_data:
    dept, created = Department.objects.get_or_create(
        departmentCode=dept_info["departmentCode"],
        company=company,
        defaults={
            "name": dept_info["name"],
            "description": dept_info["description"],
            "status": True,
        }
    )
    departamentos_created[dept_info["departmentCode"]] = dept
    tag = "CREADO" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} Área: {dept.name} ({dept.departmentCode}) ({tag})")

# ─────────────────────────────────────────────
#  6. PROCESS TYPES (Tipos de Proceso)
# ─────────────────────────────────────────────
print("\n── 6. TIPOS DE PROCESO ──")

# Necesitamos un usuario para el FK user de ProcessType y Process
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    print("  ⚠️  No se encontró un superusuario. Creando uno por defecto...")
    admin_user = User.objects.create_superuser(
        username="admin",
        email="admin@redmedicronips.com.co",
        password="admin"
    )
    print(f"  ✅ Superusuario creado: {admin_user.username}")

tipos_proceso_data = [
    {
        "name":        "Estratégico",
        "description": "Procesos de planeación, dirección y mejora continua.",
    },
    {
        "name":        "Misional",
        "description": "Procesos core del negocio: atención al paciente, prestación de servicios.",
    },
    {
        "name":        "Apoyo",
        "description": "Procesos de soporte: talento humano, financiero, tecnología.",
    },
    {
        "name":        "Evaluación",
        "description": "Procesos de auditoría, medición y control de la calidad.",
    },
]

tipos_created = {}
for tipo_info in tipos_proceso_data:
    tipo, created = ProcessType.objects.get_or_create(
        name=tipo_info["name"],
        company=company,
        defaults={
            "description": tipo_info["description"],
            "status": True,
            "user": admin_user,
        }
    )
    tipos_created[tipo_info["name"]] = tipo
    tag = "CREADO" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} Tipo: {tipo.name} ({tag})")

# ─────────────────────────────────────────────
#  7. PROCESSES (Procesos)
# ─────────────────────────────────────────────
print("\n── 7. PROCESOS ──")

procesos_data = [
    # Estratégicos
    {
        "name":        "Planeación Estratégica",
        "code":        "PE-001",
        "version":     "1.0",
        "description": "Definición de metas, indicadores y planes institucionales.",
        "tipo":        "Estratégico",
        "depto":       "GER-001",
    },
    {
        "name":        "Gestión de Calidad",
        "code":        "GC-001",
        "version":     "1.0",
        "description": "Implementación del sistema de gestión de calidad y mejora continua.",
        "tipo":        "Estratégico",
        "depto":       "CAL-001",
    },
    # Misionales
    {
        "name":        "Atención de Urgencias",
        "code":        "AU-001",
        "version":     "1.0",
        "description": "Proceso de atención de pacientes en el servicio de urgencias.",
        "tipo":        "Misional",
        "depto":       "MED-001",
    },
    {
        "name":        "Consulta Externa",
        "code":        "CE-001",
        "version":     "1.0",
        "description": "Gestión de citas, valoración y seguimiento en consulta externa.",
        "tipo":        "Misional",
        "depto":       "MED-001",
    },
    {
        "name":        "Gestión de Enfermería",
        "code":        "GE-001",
        "version":     "1.0",
        "description": "Coordinación del cuidado de enfermería y protocolos asistenciales.",
        "tipo":        "Misional",
        "depto":       "ENF-001",
    },
    {
        "name":        "Gestión Farmacéutica",
        "code":        "GF-001",
        "version":     "1.0",
        "description": "Dispensación de medicamentos, farmacovigilancia y control de inventarios.",
        "tipo":        "Misional",
        "depto":       "FAR-001",
    },
    # Apoyo
    {
        "name":        "Gestión de Talento Humano",
        "code":        "TH-001",
        "version":     "1.0",
        "description": "Selección, vinculación, capacitación y evaluación del personal.",
        "tipo":        "Apoyo",
        "depto":       "THU-001",
    },
    {
        "name":        "Gestión Financiera",
        "code":        "FI-001",
        "version":     "1.0",
        "description": "Presupuesto, facturación, cartera y estados financieros.",
        "tipo":        "Apoyo",
        "depto":       "FIN-001",
    },
    {
        "name":        "Gestión de TIC",
        "code":        "TI-001",
        "version":     "1.0",
        "description": "Soporte de infraestructura tecnológica y sistemas de información.",
        "tipo":        "Apoyo",
        "depto":       "TIC-001",
    },
    # Evaluación
    {
        "name":        "Auditoría Interna",
        "code":        "AI-001",
        "version":     "1.0",
        "description": "Planificación y ejecución de auditorías internas de calidad.",
        "tipo":        "Evaluación",
        "depto":       "CAL-001",
    },
    {
        "name":        "Gestión de Indicadores",
        "code":        "GI-001",
        "version":     "1.0",
        "description": "Medición, análisis y seguimiento de indicadores de gestión.",
        "tipo":        "Evaluación",
        "depto":       "CAL-001",
    },
]

procesos_created = 0
for proc_info in procesos_data:
    proc, created = Process.objects.get_or_create(
        code=proc_info["code"],
        defaults={
            "name": proc_info["name"],
            "description": proc_info["description"],
            "version": proc_info["version"],
            "processType": tipos_created[proc_info["tipo"]],
            "department": departamentos_created[proc_info["depto"]],
            "status": True,
            "user": admin_user,
        }
    )
    if created:
        procesos_created += 1
    tag = "CREADO" if created else "ya existe"
    print(f"  {'✅' if created else '⏭️ '} [{proc_info['tipo'][:3].upper()}] {proc.name} ({proc.code}) ({tag})")

# ─────────────────────────────────────────────
#  8. ASIGNAR ROLES AL ADMIN
# ─────────────────────────────────────────────
print("\n── 8. ASIGNAR ROLES AL ADMIN ──")

admin_role = roles_created.get("Administrador")
if admin_role and admin_role not in admin_user.roles.all():
    admin_user.roles.add(admin_role)
    print(f"  ✅ Rol '{admin_role.name}' asignado a '{admin_user.username}'")
else:
    print(f"  ⏭️  Rol 'Administrador' ya asignado a '{admin_user.username}'")

# ═════════════════════════════════════════════
#  RESUMEN FINAL
# ═════════════════════════════════════════════
print("\n" + "=" * 80)
print("  RESUMEN DE DATOS CREADOS")
print("=" * 80)
print(f"  Apps:             {App.objects.count()}")
print(f"  Roles:            {Role.objects.count()}")
print(f"  Companies:        {Company.objects.count()}")
print(f"  Sedes (HQ):       {Headquarters.objects.filter(company=company).count()}")
print(f"  Departamentos:    {Department.objects.filter(company=company).count()}")
print(f"  Tipos de Proceso: {ProcessType.objects.filter(company=company).count()}")
print(f"  Procesos:         {Process.objects.count()}")
print(f"  Superusuario:     {admin_user.username} (roles: {', '.join(r.name for r in admin_user.roles.all())})")
print("=" * 80)
print("  Datos listos para pruebas.")
print("=" * 80 + "\n")
