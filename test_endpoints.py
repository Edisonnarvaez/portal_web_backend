#!/usr/bin/env python
"""
Script para validar todos los endpoints documentados en documentos.md
"""
import requests
import json
import sys

BASE = 'http://localhost:8000'

# Authenticate
print("=" * 80)
print("VALIDACIÓN DE ENDPOINTS - Portal Web Backend")
print("=" * 80)

r = requests.post(f'{BASE}/api/token/', json={'username': 'admin', 'password': 'admin'})
if r.status_code != 200:
    print(f"ERROR: No se pudo autenticar. Status: {r.status_code}")
    sys.exit(1)

TOKEN = r.json()['access']
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
HEADERS_NO_AUTH = {'Content-Type': 'application/json'}

results = []

def test_endpoint(method, path, data=None, auth=True, description=""):
    """Test a single endpoint and record result."""
    url = f"{BASE}{path}"
    headers = HEADERS if auth else HEADERS_NO_AUTH
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            r = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == 'PATCH':
            r = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            r = requests.delete(url, headers=headers, timeout=10)
        
        status = r.status_code
        ok = status < 500
        error_detail = ""
        if status >= 400:
            try:
                error_detail = r.json() if len(r.text) < 500 else r.text[:500]
            except:
                error_detail = r.text[:500]
        
        result = {
            'method': method,
            'path': path,
            'status': status,
            'ok': ok,
            'description': description,
            'error': error_detail if not ok else ""
        }
    except Exception as e:
        result = {
            'method': method,
            'path': path,
            'status': 'ERR',
            'ok': False,
            'description': description,
            'error': str(e)
        }
    
    icon = "OK" if result['ok'] else "FAIL"
    print(f"  [{icon}] {method:6s} {path:55s} -> {result['status']}")
    if not result['ok']:
        error_str = str(result['error'])[:200]
        print(f"         ERROR: {error_str}")
    
    results.append(result)
    return result


# ============================================================
# 1. AUTH ENDPOINTS
# ============================================================
print("\n--- AUTH ---")
test_endpoint('POST', '/api/token/', data={'username': 'admin', 'password': 'admin'}, auth=False, description="Obtener JWT token")
test_endpoint('POST', '/api/token/refresh/', data={'refresh': r.json()['refresh']}, auth=False, description="Refrescar JWT token")

# ============================================================
# 2. HABILITACIÓN - PRESTADORES (DatosPrestador)
# ============================================================
print("\n--- HABILITACIÓN / PRESTADORES ---")
res = test_endpoint('GET', '/api/habilitacion/prestadores/', description="Listar prestadores")
test_endpoint('GET', '/api/habilitacion/prestadores/?page=1', description="Listar prestadores paginado")
test_endpoint('GET', '/api/habilitacion/prestadores/proximos_a_vencer/', description="Prestadores próximos a vencer")
test_endpoint('GET', '/api/habilitacion/prestadores/vencidas/', description="Prestadores vencidas")

# Get a prestador ID for detail/action tests
prestador_id = None
if res['ok'] and res['status'] == 200:
    try:
        data = requests.get(f'{BASE}/api/habilitacion/prestadores/', headers=HEADERS).json()
        items = data.get('results', data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            prestador_id = items[0]['id']
    except:
        pass

if prestador_id:
    test_endpoint('GET', f'/api/habilitacion/prestadores/{prestador_id}/', description="Detalle prestador")
    test_endpoint('GET', f'/api/habilitacion/prestadores/{prestador_id}/servicios/', description="Servicios del prestador")
    test_endpoint('GET', f'/api/habilitacion/prestadores/{prestador_id}/autoevaluaciones/', description="Autoevaluaciones del prestador")
    test_endpoint('POST', f'/api/habilitacion/prestadores/{prestador_id}/iniciar_renovacion/', description="Iniciar renovación")
else:
    print("  [SKIP] No hay prestadores para probar endpoints de detalle")

# ============================================================
# 3. HABILITACIÓN - SERVICIOS (ServicioSede)
# ============================================================
print("\n--- HABILITACIÓN / SERVICIOS ---")
res = test_endpoint('GET', '/api/habilitacion/servicios/', description="Listar servicios")
test_endpoint('GET', '/api/habilitacion/servicios/proximos_a_vencer/', description="Servicios próximos a vencer")
test_endpoint('GET', '/api/habilitacion/servicios/por_complejidad/?complejidad=ALTA', description="Servicios por complejidad")

servicio_id = None
if res['ok'] and res['status'] == 200:
    try:
        data = requests.get(f'{BASE}/api/habilitacion/servicios/', headers=HEADERS).json()
        items = data.get('results', data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            servicio_id = items[0]['id']
    except:
        pass

if servicio_id:
    test_endpoint('GET', f'/api/habilitacion/servicios/{servicio_id}/', description="Detalle servicio")
    test_endpoint('GET', f'/api/habilitacion/servicios/{servicio_id}/cumplimientos/', description="Cumplimientos del servicio")
else:
    print("  [SKIP] No hay servicios para probar endpoints de detalle")

# ============================================================
# 4. HABILITACIÓN - AUTOEVALUACIONES
# ============================================================
print("\n--- HABILITACIÓN / AUTOEVALUACIONES ---")
res = test_endpoint('GET', '/api/habilitacion/autoevaluaciones/', description="Listar autoevaluaciones")
test_endpoint('GET', '/api/habilitacion/autoevaluaciones/por_completar/', description="Autoevaluaciones por completar")

autoeval_id = None
if res['ok'] and res['status'] == 200:
    try:
        data = requests.get(f'{BASE}/api/habilitacion/autoevaluaciones/', headers=HEADERS).json()
        items = data.get('results', data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            autoeval_id = items[0]['id']
    except:
        pass

if autoeval_id:
    test_endpoint('GET', f'/api/habilitacion/autoevaluaciones/{autoeval_id}/', description="Detalle autoevaluación")
    test_endpoint('GET', f'/api/habilitacion/autoevaluaciones/{autoeval_id}/resumen/', description="Resumen autoevaluación")
    test_endpoint('POST', f'/api/habilitacion/autoevaluaciones/{autoeval_id}/validar/', description="Validar autoevaluación")
    test_endpoint('POST', f'/api/habilitacion/autoevaluaciones/{autoeval_id}/duplicar/', description="Duplicar autoevaluación")
else:
    print("  [SKIP] No hay autoevaluaciones para probar endpoints de detalle")

# ============================================================
# 5. HABILITACIÓN - CUMPLIMIENTOS
# ============================================================
print("\n--- HABILITACIÓN / CUMPLIMIENTOS ---")
res = test_endpoint('GET', '/api/habilitacion/cumplimientos/', description="Listar cumplimientos")
test_endpoint('GET', '/api/habilitacion/cumplimientos/sin_cumplir/', description="Sin cumplir")
test_endpoint('GET', '/api/habilitacion/cumplimientos/con_plan_mejora/', description="Con plan de mejora")
test_endpoint('GET', '/api/habilitacion/cumplimientos/mejoras_vencidas/', description="Mejoras vencidas")

cumplimiento_id = None
if res['ok'] and res['status'] == 200:
    try:
        data = requests.get(f'{BASE}/api/habilitacion/cumplimientos/', headers=HEADERS).json()
        items = data.get('results', data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            cumplimiento_id = items[0]['id']
    except:
        pass

if cumplimiento_id:
    test_endpoint('GET', f'/api/habilitacion/cumplimientos/{cumplimiento_id}/', description="Detalle cumplimiento")
else:
    print("  [SKIP] No hay cumplimientos para probar endpoints de detalle")

# ============================================================
# 6. NORMATIVITY
# ============================================================
print("\n--- NORMATIVITY ---")
test_endpoint('GET', '/api/normativity/estandares/', auth=False, description="Listar estándares")
test_endpoint('GET', '/api/normativity/criterios/', auth=False, description="Listar criterios")
test_endpoint('GET', '/api/normativity/documentos-normativos/', auth=False, description="Listar docs normativos")
test_endpoint('GET', '/api/normativity/estandares/todos/', auth=False, description="Todos los estándares con criterios")
test_endpoint('GET', '/api/normativity/criterios/mandatorios/', auth=False, description="Criterios mandatorios")
test_endpoint('GET', '/api/normativity/criterios/con_evidencia/', auth=False, description="Criterios con evidencia")
test_endpoint('GET', '/api/normativity/criterios/por_complejidad/?complejidad=ALTA', auth=False, description="Criterios por complejidad")

# ============================================================
# 7. OTHER APPS
# ============================================================
print("\n--- COMPANIES ---")
test_endpoint('GET', '/api/companies/companies/', description="Listar companies")
test_endpoint('GET', '/api/companies/departments/', description="Listar departments")
test_endpoint('GET', '/api/companies/headquarters/', description="Listar headquarters")
test_endpoint('GET', '/api/companies/process_types/', description="Listar process types")
test_endpoint('GET', '/api/companies/processes/', description="Listar processes")

print("\n--- INDICATORS ---")
test_endpoint('GET', '/api/indicators/indicators/', description="Listar indicadores")
test_endpoint('GET', '/api/indicators/results/', description="Listar resultados")

print("\n--- PROCESSES ---")
test_endpoint('GET', '/api/processes/documentos/', description="Listar documentos")

print("\n--- MAIN ---")
test_endpoint('GET', '/api/main/funcionarios/', description="Listar funcionarios")
test_endpoint('GET', '/api/main/contenidos/', description="Listar contenidos")
test_endpoint('GET', '/api/main/eventos/', description="Listar eventos")
test_endpoint('GET', '/api/main/felicitaciones/', description="Listar felicitaciones")
test_endpoint('GET', '/api/main/reconocimientos/', description="Listar reconocimientos")

print("\n--- USERS ---")
test_endpoint('GET', '/api/users/me/', description="Current user")
test_endpoint('GET', '/api/users/', description="Listar users")

# ============================================================
# RESUMEN
# ============================================================
print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
total = len(results)
passed = sum(1 for r in results if r['ok'])
failed = sum(1 for r in results if not r['ok'])

print(f"  Total: {total}")
print(f"  OK:    {passed}")
print(f"  FAIL:  {failed}")

if failed > 0:
    print(f"\n  Endpoints FALLIDOS (5xx):")
    for r in results:
        if not r['ok']:
            print(f"    {r['method']:6s} {r['path']:50s} -> {r['status']} - {r['description']}")

print("\n" + "=" * 80)
