#!/usr/bin/env python
"""
Script para crear más cumplimientos de ejemplo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from habilitacion.models import Autoevaluacion, Cumplimiento
from normativity.models import Criterio
from random import choice
from datetime import date, timedelta

print("\n" + "="*80)
print("CREAR MÁS CUMPLIMIENTOS DE EJEMPLO")
print("="*80 + "\n")

# Obtener la autoevaluación
auto = Autoevaluacion.objects.get(id=5)
servicios = auto.datos_prestador.headquarters.servicios_salud.all()
criterios = Criterio.objects.all()

print(f"Autoevaluación: {auto.numero_autoevaluacion}")
print(f"Servicios: {servicios.count()}")
print(f"Criterios disponibles: {criterios.count()}\n")

resultados = ['CUMPLE', 'NO_CUMPLE', 'PARCIALMENTE', 'NO_APLICA']
cumplimientos_creados = 0
cumplimientos_existentes = 0

for servicio in servicios:
    for criterio in criterios:
        cumplimiento, created = Cumplimiento.objects.get_or_create(
            autoevaluacion=auto,
            servicio_sede=servicio,
            criterio=criterio,
            defaults={
                'cumple': choice(resultados),
                'fecha_compromiso': date.today() + timedelta(days=30)
            }
        )
        if created:
            cumplimientos_creados += 1
        else:
            cumplimientos_existentes += 1

print(f"Cumplimientos creados: {cumplimientos_creados}")
print(f"Cumplimientos existentes: {cumplimientos_existentes}")

# Recalcular
total = auto.cumplimientos.count()
cumple_count = auto.cumplimientos.filter(cumple='CUMPLE').count()
parcialmente_count = auto.cumplimientos.filter(cumple='PARCIALMENTE').count()
no_cumple_count = auto.cumplimientos.filter(cumple='NO_CUMPLE').count()
no_aplica_count = auto.cumplimientos.filter(cumple='NO_APLICA').count()

print(f"\n{'='*80}")
print("DESGLOSE ACTUAL:")
print(f"{'='*80}")
print(f"Total cumplimientos: {total}")
print(f"  • CUMPLE: {cumple_count}")
print(f"  • PARCIALMENTE: {parcialmente_count}")
print(f"  • NO_CUMPLE: {no_cumple_count}")
print(f"  • NO_APLICA: {no_aplica_count}")

porcentaje = auto.porcentaje_cumplimiento()
print(f"\nPorcentaje de cumplimiento: {porcentaje}%")
print(f"\n{'='*80}\n")
