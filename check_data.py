#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from habilitacion.models import DatosPrestador
from companies.models import Headquarters

print("=== DIAGNÓSTICO ===\n")

# Revisar DatosPrestador
all_prestadores = DatosPrestador.objects.all()
print(f"Total DatosPrestador: {all_prestadores.count()}")

problematicos = []
for p in all_prestadores:
    try:
        hq = p.headquarters
        print(f"✅ {p.codigo_reps} → {hq.nombre}")
    except Exception as e:
        print(f"❌ {p.codigo_reps} → ERROR: {type(e).__name__}: {e}")
        problematicos.append(p.id)

if problematicos:
    print(f"\n⚠️  {len(problematicos)} DatosPrestador sin Headquarters válido")
    print(f"IDs problemáticos: {problematicos}")
    
    # Eliminar en cascada: Cumplimiento → Autoevaluacion → DatosPrestador
    from habilitacion.models import Autoevaluacion, Cumplimiento
    
    # 1. Eliminar Cumplimientos
    autoevals_to_delete = Autoevaluacion.objects.filter(datos_prestador_id__in=problematicos)
    cumplimientos = Cumplimiento.objects.filter(autoevaluacion__in=autoevals_to_delete)
    print(f"\n1. Eliminando {cumplimientos.count()} Cumplimientos...")
    cumplimientos.delete()
    
    # 2. Eliminar Autoevaluaciones
    print(f"2. Eliminando {autoevals_to_delete.count()} Autoevaluaciones...")
    autoevals_to_delete.delete()
    
    # 3. Eliminar DatosPrestador
    print("3. Eliminando DatosPrestador orfanos...")
    deleted_count, _ = DatosPrestador.objects.filter(id__in=problematicos).delete()
    print(f"\n✅ LIMPIEZA COMPLETADA - Eliminados {deleted_count} registros orfanos")
else:
    print("\n✅ Todos los DatosPrestador están bien vinculados")

# Revisar Headquarters
print(f"\nTotal Headquarters: {Headquarters.objects.count()}")
huerfanas = Headquarters.objects.filter(datos_habilitacion__isnull=True)
print(f"Headquarters sin habilitación: {huerfanas.count()}")
for h in huerfanas:
    print(f"  - {h.name} ({h.company.name})")
