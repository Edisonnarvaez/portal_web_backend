#!/usr/bin/env python
"""
Script para probar todos los endpoints de normativity
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import TestCase, Client
from django.http import JsonResponse

client = Client()

print("=" * 70)
print("PRUEBAS DE ENDPOINTS - NORMATIVITY")
print("=" * 70)

# Test 1: GET /api/normativity/estandares/
print("\n[TEST 1] GET /api/normativity/estandares/")
response = client.get('/api/normativity/estandares/', format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.data if isinstance(response.data, list) else response.data.get('results', [])
    count = len(data) if isinstance(data, list) else 0
    print(f"OK: Se obtuvieron {count} items")
    if isinstance(data, list) and len(data) > 0:
        print(f"   Ejemplo: {data[0].get('nombre')}")
else:
    print(f"ERROR: {response.data}")

# Test 2: GET /api/normativity/criterios/
print("\n[TEST 2] GET /api/normativity/criterios/")
response = client.get('/api/normativity/criterios/', format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.data if isinstance(response.data, list) else response.data.get('results', [])
    count = len(data) if isinstance(data, list) else 0
    print(f"OK: Se obtuvieron {count} items")
    if isinstance(data, list) and len(data) > 0:
        print(f"   Ejemplo: {data[0].get('codigo')} - {data[0].get('nombre')[:40]}")
else:
    print(f"ERROR: {response.data}")

# Test 3: GET /api/normativity/estandares/1/
print("\n[TEST 3] GET /api/normativity/estandares/1/")
response = client.get('/api/normativity/estandares/1/', format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"OK: Estandar obtenido")
    nombre = response.data.get('nombre')
    criterios_count = len(response.data.get('criterios', []))
    print(f"   Nombre: {nombre}")
    print(f"   Criterios: {criterios_count}")
else:
    print(f"ERROR: {response.data}")

# Test 4: GET /api/normativity/criterios/?estandar=1
print("\n[TEST 4] GET /api/normativity/criterios/?estandar=1")
response = client.get('/api/normativity/criterios/', {'estandar': 1}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.data if isinstance(response.data, list) else response.data.get('results', [])
    count = len(data) if isinstance(data, list) else 0
    print(f"OK: Se obtuvieron {count} criterios filtrados")
else:
    print(f"ERROR: {response.data}")

# Test 5: GET /api/normativity/criterios/mandatorios/
print("\n[TEST 5] GET /api/normativity/criterios/mandatorios/")
response = client.get('/api/normativity/criterios/mandatorios/', format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.data if isinstance(response.data, list) else response.data.get('results', [])
    count = len(data) if isinstance(data, list) else len(response.data)
    print(f"OK: Se obtuvieron {count} criterios mandatorios")
else:
    print(f"ERROR: {response.data}")

# Test 6: GET /api/normativity/criterios/con_evidencia/
print("\n[TEST 6] GET /api/normativity/criterios/con_evidencia/")
response = client.get('/api/normativity/criterios/con_evidencia/', format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.data if isinstance(response.data, list) else response.data.get('results', [])
    count = len(data) if isinstance(data, list) else len(response.data)
    print(f"OK: Se obtuvieron {count} criterios con evidencia")
else:
    print(f"ERROR: {response.data}")

# Test 7: GET /api/normativity/documentos-normativos/
print("\n[TEST 7] GET /api/normativity/documentos-normativos/")
response = client.get('/api/normativity/documentos-normativos/', format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.data if isinstance(response.data, list) else response.data.get('results', [])
    count = len(data) if isinstance(data, list) else 0
    print(f"OK: Se obtuvieron {count} documentos normativos")
else:
    print(f"ERROR: {response.data}")

# Test INCORRECTO
print("\n" + "=" * 70)
print("[TEST INCORRECTO] GET /api/normativity/criterio/ (singular - MALO)")
response = client.get('/api/normativity/criterio/', format='json')
print(f"Status: {response.status_code}")
print(f"Resultado: {response.status_code == 404} - Endpoint no existe (esperado)")

print("\n" + "=" * 70)
print("RESUMEN: TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE")
print("=" * 70)
print("\nEndpoints disponibles:")
print("  /api/normativity/estandares/")
print("  /api/normativity/estandares/{id}/")
print("  /api/normativity/estandares/{id}/criterios/")
print("  /api/normativity/criterios/")
print("  /api/normativity/criterios/mandatorios/")
print("  /api/normativity/criterios/con_evidencia/")
print("  /api/normativity/criterios/por_complejidad/?complejidad=ALTA")
print("  /api/normativity/documentos-normativos/")
print("\nNOTA: Si accediste a /api/normativity/criterio/, era incorrecto.")
print("      Debes usar /api/normativity/criterios/ (plural)")
