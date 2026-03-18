"""Test script for mejoras endpoints."""
import requests
import json

BASE = 'http://localhost:8000'

# Auth
r = requests.post(f'{BASE}/api/token/', json={'username': 'admin', 'password': 'admin'})
token = r.json()['access']
h = {'Authorization': f'Bearer {token}'}

# Get autoevaluacion
r = requests.get(f'{BASE}/api/habilitacion/autoevaluaciones/', headers=h)
autos = r.json()
if isinstance(autos, dict):
    autos = autos.get('results', [])
auto_id = autos[0]['id']
print(f"Using autoevaluacion id: {auto_id}")

print("\n=== CREATE PLAN ===")
data = {
    'numero_plan': 'PM-TEST-003',
    'descripcion': 'Plan de prueba',
    'origen_tipo': 'HABILITACION',
    'acciones_implementar': 'Controles de calidad',
    'fecha_inicio': '2026-02-20',
    'fecha_vencimiento': '2026-12-31',
    'estado': 'PENDIENTE',
    'porcentaje_avance': 0,
    'autoevaluacion': auto_id
}
r = requests.post(f'{BASE}/api/mejoras/planes-mejora/', headers=h, json=data)
print(f"POST plan -> {r.status_code}")
plan = r.json()
plan_id = plan.get('id')
plan_estado = plan.get('estado')
print(f"  id={plan_id}, estado={plan_estado}")
assert plan_id is not None, f"id missing from response: {plan}"
assert plan_estado == 'PENDIENTE', f"Unexpected estado: {plan_estado}"

print("\n=== GET DETAIL ===")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/{plan_id}/', headers=h)
print(f"GET detail -> {r.status_code}")
d = r.json()
print(f"  hallazgos={len(d.get('hallazgos', []))}")
assert r.status_code == 200

print("\n=== PATCH ===")
r = requests.patch(f'{BASE}/api/mejoras/planes-mejora/{plan_id}/', headers=h, 
                   json={'porcentaje_avance': 50, 'estado': 'EN_CURSO'})
print(f"PATCH -> {r.status_code}, estado={r.json().get('estado')}")
assert r.status_code == 200

print("\n=== CREATE HALLAZGO ===")
hall_data = {
    'numero_hallazgo': 'H-TEST-002',
    'descripcion': 'Hallazgo test',
    'origen_tipo': 'HABILITACION',
    'tipo': 'NO_CONFORMIDAD',
    'severidad': 'MEDIA',
    'estado': 'ABIERTO',
    'plan_mejora': plan_id,
    'fecha_identificacion': '2026-02-20',
    'autoevaluacion': auto_id
}
r = requests.post(f'{BASE}/api/mejoras/hallazgos/', headers=h, json=hall_data)
print(f"POST hallazgo -> {r.status_code}")
hall = r.json()
hall_id = hall.get('id')
print(f"  id={hall_id}, tipo={hall.get('tipo')}")
assert hall_id is not None, f"id missing: {hall}"

print("\n=== GET HALLAZGO DETAIL ===")
r = requests.get(f'{BASE}/api/mejoras/hallazgos/{hall_id}/', headers=h)
print(f"GET hallazgo detail -> {r.status_code}")
assert r.status_code == 200

print("\n=== VERIFY PLAN HAS HALLAZGO ===")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/{plan_id}/', headers=h)
d = r.json()
h_count = len(d.get('hallazgos', []))
print(f"  Plan has {h_count} hallazgo(s)")
assert h_count == 1

print("\n=== RESUMEN ===")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/resumen/', headers=h)
print(f"GET resumen -> {r.status_code}")
print(f"  {json.dumps(r.json())}")
assert r.status_code == 200

print("\n=== ESTADISTICAS ===")
r = requests.get(f'{BASE}/api/mejoras/hallazgos/estadisticas/', headers=h)
print(f"GET estadisticas -> {r.status_code}")
print(f"  {json.dumps(r.json())}")
assert r.status_code == 200

print("\n=== SIN-PLAN ===")
r = requests.get(f'{BASE}/api/mejoras/hallazgos/sin-plan/', headers=h)
print(f"GET sin-plan -> {r.status_code}")
assert r.status_code == 200

print("\n=== POR-ORIGEN ===")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/por-origen/', headers=h)
print(f"GET planes por-origen -> {r.status_code}")
print(f"  {json.dumps(r.json())}")
r = requests.get(f'{BASE}/api/mejoras/hallazgos/por-origen/', headers=h)
print(f"GET hallazgos por-origen -> {r.status_code}")
print(f"  {json.dumps(r.json())}")

print("\n=== VENCIDOS ===")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/vencidos/', headers=h)
print(f"GET vencidos -> {r.status_code}")

print("\n=== PROXIMOS-VENCER ===")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/proximos-vencer/', headers=h)
print(f"GET proximos-vencer -> {r.status_code}")

print("\n=== FILTERS ===")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/?origen_tipo=HABILITACION', headers=h)
print(f"GET ?origen_tipo=HABILITACION -> {r.status_code}")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/?estado=EN_CURSO', headers=h)
print(f"GET ?estado=EN_CURSO -> {r.status_code}")
r = requests.get(f'{BASE}/api/mejoras/hallazgos/?severidad=MEDIA', headers=h)
print(f"GET ?severidad=MEDIA -> {r.status_code}")
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/?search=prueba', headers=h)
print(f"GET ?search=prueba -> {r.status_code}")

print("\n=== CLEANUP ===")
requests.delete(f'{BASE}/api/mejoras/hallazgos/{hall_id}/', headers=h)
requests.delete(f'{BASE}/api/mejoras/planes-mejora/{plan_id}/', headers=h)
# Also clean old test plans
r = requests.get(f'{BASE}/api/mejoras/planes-mejora/', headers=h)
plans = r.json() if isinstance(r.json(), list) else r.json().get('results', [])
for p in plans:
    if 'TEST' in p.get('numero_plan', ''):
        requests.delete(f"{BASE}/api/mejoras/planes-mejora/{p['id']}/", headers=h)
        print(f"  Cleaned up {p['numero_plan']}")
print("Cleanup done")

print("\n" + "="*50)
print("ALL TESTS PASSED!")
print("="*50)
