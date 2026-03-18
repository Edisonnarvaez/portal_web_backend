"""
habilitacion/create_cumplimientos.py

Script para crear cumplimientos automáticamente para una autoevaluación.

USO:
  python manage.py shell
  exec(open('habilitacion/create_cumplimientos.py', encoding='utf-8').read())

O ejecutar directamente:
  python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings'); 
  import django; django.setup(); exec(open('habilitacion/create_cumplimientos.py', 
  encoding='utf-8').read())"
"""

import os
import sys
import django
from datetime import date

# Configurar Django si se ejecuta directamente
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

from habilitacion.models import Autoevaluacion, Cumplimiento, ServicioSede
from normativity.models import Criterio

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

print("\n" + "="*80)
print("  CREAR CUMPLIMIENTOS AUTOMÁTICAMENTE")
print("="*80)

# OPCIÓN 1: Seleccionar autoevaluación específica
print("\n1️⃣  SELECCIONAR AUTOEVALUACIÓN")
print("-" * 80)

autoevaluaciones = Autoevaluacion.objects.all()
for idx, auto in enumerate(autoevaluaciones, 1):
    cumpl_count = auto.cumplimientos.count()
    print(f"  {idx}. {auto.numero_autoevaluacion} "
          f"({auto.estado}) - {cumpl_count} cumplimientos")

if not autoevaluaciones.exists():
    print("  ❌ No hay autoevaluaciones en la BD")
    print("  Crea una primero: Ir a /admin/habilitacion/autoevaluacion/")
    sys.exit(1)

seleccion = input("\n¿Cuál autoevaluación? (número): ").strip()
try:
    auto = autoevaluaciones[int(seleccion) - 1]
except (ValueError, IndexError):
    print("❌ Selección inválida")
    sys.exit(1)

print(f"\n✓ Seleccionado: {auto.numero_autoevaluacion}")

# ============================================================================
# VERIFICAR SERVICIOS
# ============================================================================

print("\n2️⃣  SELECCIONAR SERVICIOS")
print("-" * 80)

# Obtener servicios - Si vienen de la autoevaluación o de la empresa
servicios = ServicioSede.objects.filter(
    datospreestador=auto.datos_prestador
)

if not servicios.exists():
    print("  ⚠️  No hay servicios asociados a esta institución")
    print("  Creando cumplimientos para TODOS los servicios del sistema...")
    servicios = ServicioSede.objects.all()

print(f"\n  Servicios disponibles:")
for idx, serv in enumerate(servicios, 1):
    cumpl_count = serv.cumplimientos.filter(autoevaluacion=auto).count()
    print(f"    {idx}. {serv.nombre_servicio} "
          f"({cumpl_count} cumplimientos de esta auto)")

# ============================================================================
# CREAR CUMPLIMIENTOS
# ============================================================================

print("\n3️⃣  CREAR CUMPLIMIENTOS")
print("-" * 80)

# Obtener todos los criterios
criterios = Criterio.objects.all().order_by('estandar__codigo', 'codigo')

print(f"\nCriterios a evaluar: {criterios.count()}")
print(f"Servicios: {servicios.count()}")
print(f"Total cumplimientos a crear: {criterios.count() * servicios.count()}")

# Contar cuántos ya existen
existentes = Cumplimiento.objects.filter(autoevaluacion=auto).count()
print(f"Cumplimientos existentes: {existentes}")

# Preguntar confirmación
respuesta = input("\n¿Crear cumplimientos? (s/n): ").strip().lower()
if respuesta != 's':
    print("Operación cancelada")
    sys.exit(0)

# ============================================================================
# EJECUCIÓN
# ============================================================================

print("\nCreando cumplimientos...\n")

creados = 0
duplicados = 0
errores = 0

estandar_actual = None

for criterio in criterios:
    # Mostrar progreso por estándar
    if estandar_actual != criterio.estandar.codigo:
        estandar_actual = criterio.estandar.codigo
        print(f"\n  📍 Estándar {estandar_actual}: {criterio.estandar.nombre}")
        print(f"     {'-'*70}", end='')
    
    for servicio in servicios:
        try:
            cumplimiento, created = Cumplimiento.objects.get_or_create(
                autoevaluacion=auto,
                servicio_sede=servicio,
                criterio=criterio,
                defaults={
                    'cumple': 'CUMPLE',  # Por defecto
                    'hallazgo': f"Evaluación pendiente de {criterio.nombre}",
                }
            )
            
            if created:
                creados += 1
                print(f"\n     ✓ Creado: {criterio.codigo} → {servicio.nombre_servicio[:40]}", end='')
            else:
                duplicados += 1
                print(f"\n     ⊕ Existe: {criterio.codigo} → {servicio.nombre_servicio[:40]}", end='')
        
        except Exception as e:
            errores += 1
            print(f"\n     ✗ Error en {criterio.codigo}: {str(e)}", end='')

# ============================================================================
# RESUMEN
# ============================================================================

print("\n\n" + "="*80)
print("  RESUMEN")
print("="*80)

total_ahora = auto.cumplimientos.count()
porcentaje = auto.porcentaje_cumplimiento()

print(f"\n  ✓ Creados:       {creados}")
print(f"  ⊕ Existentes:    {duplicados}")
print(f"  ✗ Errores:       {errores}")
print(f"  ─────────────────────")
print(f"  TOTAL:           {total_ahora}")

print(f"\n  📊 Estadísticas de la Autoevaluación:")
print(f"     Número: {auto.numero_autoevaluacion}")
print(f"     Estado: {auto.estado}")
print(f"     Cumplimientos: {total_ahora}")
print(f"     Porcentaje: {porcentaje:.1f}%")

# Desglose por resultado
print(f"\n  📋 Desglose por Resultado:")
for resultado in ['CUMPLE', 'NO_CUMPLE', 'PARCIALMENTE', 'NO_APLICA']:
    count = auto.cumplimientos.filter(cumple=resultado).count()
    if count > 0:
        pct = (count / total_ahora * 100) if total_ahora > 0 else 0
        print(f"     {resultado:20} {count:4} ({pct:5.1f}%)")

# ============================================================================
# PRÓXIMOS PASOS
# ============================================================================

print("\n" + "="*80)
print("  PRÓXIMOS PASOS")
print("="*80)

print(f"""
  1. VER EN ADMIN:
     http://localhost:8000/admin/habilitacion/autoevaluacion/{auto.pk}/change/
     
  2. MODIFICAR CUMPLIMIENTOS:
     http://localhost:8000/admin/habilitacion/cumplimiento/
     
     Filtrar por autoevaluación: {auto.numero_autoevaluacion}
     
     Para cada cumplimiento:
     - Cambiar resultado (CUMPLE → NO_CUMPLE)
     - Agregar hallazgo
     - Agregar documentos evidencia
     - Agregar plan de mejora (si no cumple)
     
  3. VERIFICAR CAMBIOS EN SHELL:
     auto = Autoevaluacion.objects.get(numero_autoevaluacion="{auto.numero_autoevaluacion}")
     print(f"Porcentaje: {{auto.porcentaje_cumplimiento()}}%")
     
  4. GENERAR REPORTES:
     (Ver REPORTES.md para instrucciones)

""")

print("="*80)
print("  ✓ CUMPLIMIENTOS LISTOS PARA EVALUAR")
print("="*80 + "\n")

# ============================================================================
# INFORMACIÓN ADICIONAL
# ============================================================================

if __name__ == '__main__':
    print("\n✓ Script ejecutado exitosamente")
    sys.exit(0)
