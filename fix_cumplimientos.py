#!/usr/bin/env python
"""
Script para verificar y corregir cumplimientos en autoevaluaciones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from habilitacion.models import Autoevaluacion, Cumplimiento

print("\n" + "="*80)
print("VERIFICAR Y CORREGIR CUMPLIMIENTOS")
print("="*80 + "\n")

# Obtener todas las autoevaluaciones
autoevaluaciones = Autoevaluacion.objects.all()
print(f"Total autoevaluaciones: {autoevaluaciones.count()}\n")

for auto in autoevaluaciones:
    print(f"\n{'='*80}")
    print(f"Autoevaluación: {auto.numero_autoevaluacion} (ID: {auto.id})")
    print(f"{'='*80}")
    
    # Contar cumplimientos totales
    total = auto.cumplimientos.count()
    print(f"\nTotal cumplimientos: {total}")
    
    # Desglose por estado
    cumple = auto.cumplimientos.filter(cumple='CUMPLE').count()
    no_cumple = auto.cumplimientos.filter(cumple='NO_CUMPLE').count()
    parcialmente = auto.cumplimientos.filter(cumple='PARCIALMENTE').count()
    no_aplica = auto.cumplimientos.filter(cumple='NO_APLICA').count()
    
    print(f"  • CUMPLE: {cumple}")
    print(f"  • NO_CUMPLE: {no_cumple}")
    print(f"  • PARCIALMENTE: {parcialmente}")
    print(f"  • NO_APLICA: {no_aplica}")
    
    # Calcular porcentaje
    porcentaje = auto.porcentaje_cumplimiento()
    print(f"\nPorcentaje calculado: {porcentaje}%")
    
    # Si no hay cumplimientos, crear algunos
    if total == 0:
        print("\n⚠️  NO HAY CUMPLIMIENTOS - Creando datos de ejemplo...\n")
        
        from normativity.models import Criterio
        from random import choice
        
        criterios = Criterio.objects.all()
        servicios = auto.datos_prestador.servicios_habilitacion.all()
        
        if not servicios.exists():
            print("❌ No hay servicios de sede para esta autoevaluación")
        else:
            resultados = ['CUMPLE', 'NO_CUMPLE', 'PARCIALMENTE', 'NO_APLICA']
            cumplimientos_creados = 0
            
            for servicio in servicios:
                for criterio in criterios[:10]:  # Crear primeros 10
                    try:
                        cumplimiento, created = Cumplimiento.objects.get_or_create(
                            autoevaluacion=auto,
                            servicio_sede=servicio,
                            criterio=criterio,
                            defaults={
                                'cumple': choice(resultados),
                            }
                        )
                        if created:
                            cumplimientos_creados += 1
                    except Exception as e:
                        print(f"  ❌ Error en {criterio.codigo}: {str(e)[:50]}")
            
            print(f"✅ Cumplimientos creados: {cumplimientos_creados}")
            
            # Recalcular
            nuevo_total = auto.cumplimientos.count()
            nuevo_porcentaje = auto.porcentaje_cumplimiento()
            print(f"\nNuevo total: {nuevo_total}")
            print(f"Nuevo porcentaje: {nuevo_porcentaje}%")

print("\n" + "="*80)
print("VERIFICACIÓN COMPLETADA")
print("="*80 + "\n")
