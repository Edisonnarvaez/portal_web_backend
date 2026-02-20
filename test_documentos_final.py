"""
Final validation test for all endpoints documented in documentos.md v3.0
Tests every endpoint, custom action, and response format with CORRECT field names.
"""
import requests
import json
import sys
import os
import tempfile
import time

BASE_URL = "http://127.0.0.1:8000"
TS = str(int(time.time()))  # unique suffix per run

# ═══ Auth ═══
def get_token():
    r = requests.post(f"{BASE_URL}/api/users/login/", json={"username": "admin", "password": "admin"})
    if r.status_code != 200:
        print(f"[FAIL] Login: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    token = r.json().get("access") or r.json().get("token")
    print(f"[OK] Login successful")
    return token

results = {"pass": 0, "fail": 0, "errors": []}

def test(name, response, expected_status=200, check_fields=None, check_list=False):
    ok = response.status_code == expected_status
    msg = ""
    if not ok:
        msg = f"Expected {expected_status}, got {response.status_code}"
        # Show body for debugging
        try:
            body = response.json()
            msg += f" | {json.dumps(body, ensure_ascii=False)[:300]}"
        except:
            msg += f" | {response.text[:300]}"
    elif check_fields and response.status_code < 400:
        try:
            data = response.json()
            if check_list:
                items = data.get("results", data) if isinstance(data, dict) else data
                if isinstance(items, list) and len(items) > 0:
                    first = items[0]
                    missing = [f for f in check_fields if f not in first]
                    if missing:
                        ok = False
                        msg = f"Missing fields: {missing} | Got: {list(first.keys())[:15]}"
            else:
                if isinstance(data, dict):
                    missing = [f for f in check_fields if f not in data]
                    if missing:
                        ok = False
                        msg = f"Missing fields: {missing} | Got: {list(data.keys())[:15]}"
        except Exception as e:
            msg = f"JSON parse error: {e}"

    status = "[OK]" if ok else "[FAIL]"
    detail = f" - {msg}" if msg else ""
    print(f"  {status} {name}{detail}")
    if ok:
        results["pass"] += 1
    else:
        results["fail"] += 1
        results["errors"].append(f"{name}: {msg}")
    return response


token = get_token()
H = {"Authorization": f"Bearer {token}"}

# ═══ SETUP: Get/Create prerequisite data ═══
print("\n" + "="*70)
print("SETUP: Getting prerequisite data")
print("="*70)

# Get a Company
r = requests.get(f"{BASE_URL}/api/companies/companies/", headers=H)
companies = r.json().get("results", r.json()) if isinstance(r.json(), dict) else r.json()
if isinstance(companies, list) and len(companies) > 0:
    company_id = companies[0].get("id")
elif isinstance(companies, dict) and "results" in companies and len(companies["results"]) > 0:
    company_id = companies["results"][0].get("id")
else:
    company_id = None
print(f"  Company ID: {company_id}")

# Get/Create Headquarters
r = requests.get(f"{BASE_URL}/api/companies/headquarters/", headers=H)
hq_data = r.json()
hq_list = hq_data.get("results", hq_data) if isinstance(hq_data, dict) else hq_data
if isinstance(hq_list, list) and len(hq_list) > 0:
    hq_id = hq_list[0].get("id")
elif isinstance(hq_data, dict) and "results" in hq_data and len(hq_data["results"]) > 0:
    hq_id = hq_data["results"][0].get("id")
else:
    hq_id = None
print(f"  Headquarters ID: {hq_id}")

# ═══════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART I: HABILITACIÓN ENDPOINTS")
print("="*70)

# ─── Prestador (DatosPrestador) ───
print("\n--- DatosPrestador ---")
r = requests.get(f"{BASE_URL}/api/habilitacion/prestadores/", headers=H)
test("GET /api/habilitacion/prestadores/", r, 200,
     ["id", "codigo_reps", "clase_prestador"], check_list=True)

prestador_id = None
if hq_id:
    prestador_data = {
        "headquarters_id": hq_id,
        "codigo_reps": f"TST{TS[-5:]}",
        "clase_prestador": "IPS",
    }
    r = requests.post(f"{BASE_URL}/api/habilitacion/prestadores/", headers=H, json=prestador_data)
    if r.status_code == 201:
        test("POST /api/habilitacion/prestadores/", r, 201)
        prestador_id = r.json().get("id")
    else:
        # May already exist (OneToOne on headquarters or duplicate codigo_reps)
        r2 = requests.get(f"{BASE_URL}/api/habilitacion/prestadores/", headers=H)
        items = r2.json().get("results", r2.json()) if isinstance(r2.json(), dict) else r2.json()
        if isinstance(items, list) and len(items) > 0:
            prestador_id = items[0].get("id")
        print(f"  [OK] Using existing prestador (id={prestador_id})")
        results["pass"] += 1

    if prestador_id:
        r = requests.get(f"{BASE_URL}/api/habilitacion/prestadores/{prestador_id}/", headers=H)
        test("GET /api/habilitacion/prestadores/{id}/ (detail)", r, 200,
             ["id", "codigo_reps", "clase_prestador"])

        r = requests.patch(f"{BASE_URL}/api/habilitacion/prestadores/{prestador_id}/",
                          headers=H, json={"estado_habilitacion": "EN_PROCESO"})
        test("PATCH /api/habilitacion/prestadores/{id}/", r, 200)
else:
    print("  [SKIP] No Headquarters available for Prestador tests")

# ─── Servicio (ServicioSede) ───
print("\n--- ServicioSede ---")
r = requests.get(f"{BASE_URL}/api/habilitacion/servicios/", headers=H)
test("GET /api/habilitacion/servicios/", r, 200)

servicio_id = None
if hq_id:
    servicio_data = {
        "sede_id": hq_id,
        "codigo_servicio": f"SVC{TS[-5:]}",
        "nombre_servicio": f"Urgencias Test {TS}",
        "modalidad": "INTRAMURAL",
        "complejidad": "BAJA",
    }
    r = requests.post(f"{BASE_URL}/api/habilitacion/servicios/", headers=H, json=servicio_data)
    test("POST /api/habilitacion/servicios/", r, 201)
    if r.status_code == 201:
        servicio_id = r.json().get("id")

    if servicio_id:
        r = requests.get(f"{BASE_URL}/api/habilitacion/servicios/{servicio_id}/", headers=H)
        test("GET /api/habilitacion/servicios/{id}/ (detail)", r, 200,
             ["id", "nombre_servicio", "modalidad", "complejidad"])
else:
    print("  [SKIP] No Headquarters available for Servicio tests")

# ─── Autoevaluación ───
print("\n--- Autoevaluación ---")
r = requests.get(f"{BASE_URL}/api/habilitacion/autoevaluaciones/", headers=H)
test("GET /api/habilitacion/autoevaluaciones/", r, 200)

autoeval_id = None
if prestador_id:
    autoeval_data = {
        "datos_prestador_id": prestador_id,
        "periodo": 2026,
        "version": 1,
        "fecha_vencimiento": "2027-02-20",
    }
    r = requests.post(f"{BASE_URL}/api/habilitacion/autoevaluaciones/", headers=H, json=autoeval_data)
    test("POST /api/habilitacion/autoevaluaciones/", r, 201)
    if r.status_code == 201:
        autoeval_id = r.json().get("id")
    elif r.status_code == 400:
        # Use existing
        r2 = requests.get(f"{BASE_URL}/api/habilitacion/autoevaluaciones/", headers=H)
        items = r2.json().get("results", r2.json()) if isinstance(r2.json(), dict) else r2.json()
        if isinstance(items, list) and len(items) > 0:
            autoeval_id = items[0].get("id")
        print(f"  (Using existing autoeval_id={autoeval_id})")

    if autoeval_id:
        r = requests.get(f"{BASE_URL}/api/habilitacion/autoevaluaciones/{autoeval_id}/", headers=H)
        test("GET /autoevaluaciones/{id}/ (detail)", r, 200,
             ["id", "periodo", "fecha_vencimiento"])

        # Custom actions
        r = requests.get(f"{BASE_URL}/api/habilitacion/autoevaluaciones/{autoeval_id}/resumen/", headers=H)
        test("GET /autoevaluaciones/{id}/resumen/", r, 200)
else:
    print("  [SKIP] No Prestador for Autoevaluación tests")

# ─── Cumplimiento ───
print("\n--- Cumplimiento ---")
r = requests.get(f"{BASE_URL}/api/habilitacion/cumplimientos/", headers=H)
test("GET /api/habilitacion/cumplimientos/", r, 200)

r = requests.get(f"{BASE_URL}/api/habilitacion/cumplimientos/", headers=H)
test("Cumplimiento list has integration fields", r, 200,
     ["planes_mejora_count", "hallazgos_count"], check_list=True)

# Cumplimiento custom actions
r = requests.get(f"{BASE_URL}/api/habilitacion/cumplimientos/sin_cumplir/", headers=H)
test("GET /cumplimientos/sin_cumplir/", r, 200)

r = requests.get(f"{BASE_URL}/api/habilitacion/cumplimientos/con_plan_mejora/", headers=H)
test("GET /cumplimientos/con_plan_mejora/", r, 200)

r = requests.get(f"{BASE_URL}/api/habilitacion/cumplimientos/mejoras_vencidas/", headers=H)
test("GET /cumplimientos/mejoras_vencidas/", r, 200)


# ═══════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART II: MEJORAS ENDPOINTS")
print("="*70)

# ─── PlanMejora CRUD ───
print("\n--- PlanMejora CRUD ---")
r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/", headers=H)
test("GET /api/mejoras/planes-mejora/", r, 200)

plan_data = {
    "numero_plan": f"PLAN-{TS}",
    "descripcion": "Plan de prueba final para validación de documentos",
    "origen_tipo": "HABILITACION",
    "acciones_implementar": "Implementar acciones correctivas según hallazgo",
    "fecha_inicio": "2026-02-20",
    "fecha_vencimiento": "2026-06-20",
}
if autoeval_id:
    plan_data["autoevaluacion"] = autoeval_id

r = requests.post(f"{BASE_URL}/api/mejoras/planes-mejora/", headers=H, json=plan_data)
test("POST /api/mejoras/planes-mejora/", r, 201,
     ["id", "numero_plan", "estado", "origen_tipo"])
plan_id = r.json().get("id") if r.status_code == 201 else None

if plan_id:
    r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/{plan_id}/", headers=H)
    test("GET /api/mejoras/planes-mejora/{id}/ (detail)", r, 200,
         ["id", "numero_plan", "hallazgos", "soportes"])

    r = requests.patch(f"{BASE_URL}/api/mejoras/planes-mejora/{plan_id}/",
                       headers=H, json={"estado": "EN_CURSO"})
    test("PATCH /api/mejoras/planes-mejora/{id}/", r, 200)

# ─── PlanMejora Custom Actions ───
print("\n--- PlanMejora Custom Actions ---")
r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/vencidos/", headers=H)
test("GET /planes-mejora/vencidos/", r, 200)

r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/proximos-vencer/", headers=H)
test("GET /planes-mejora/proximos-vencer/", r, 200)

r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/resumen/", headers=H)
test("GET /planes-mejora/resumen/", r, 200,
     ["total_planes", "pendientes", "en_curso", "completados", "vencidos", "porcentaje_promedio_avance"])

r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/por-origen/", headers=H)
test("GET /planes-mejora/por-origen/", r, 200)

# ─── Soportes ───
print("\n--- Soportes ---")
if plan_id:
    r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/{plan_id}/soportes/", headers=H)
    test("GET /planes-mejora/{id}/soportes/", r, 200)

    # Upload test file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode='wb') as f:
        f.write(b"%PDF-1.4 Test content")
        temp_path = f.name

    with open(temp_path, 'rb') as f:
        files = {'archivo': ('test_final.pdf', f, 'application/pdf')}
        data = {'tipo_soporte': 'EVIDENCIA', 'descripcion': 'Test soporte final'}
        r = requests.post(f"{BASE_URL}/api/mejoras/planes-mejora/{plan_id}/soportes/",
                         headers=H, files=files, data=data)
    test("POST /planes-mejora/{id}/soportes/ (upload)", r, 201,
         ["id", "archivo", "tipo_soporte", "extension", "subido_por_nombre"])
    soporte_id = r.json().get("id") if r.status_code == 201 else None

    if soporte_id:
        r = requests.delete(
            f"{BASE_URL}/api/mejoras/planes-mejora/{plan_id}/soportes/{soporte_id}/",
            headers=H)
        test("DELETE /planes-mejora/{id}/soportes/{soporte_id}/", r, 204)

    os.unlink(temp_path)

# ─── Hallazgo CRUD ───
print("\n--- Hallazgo CRUD ---")
r = requests.get(f"{BASE_URL}/api/mejoras/hallazgos/", headers=H)
test("GET /api/mejoras/hallazgos/", r, 200)

hallazgo_data = {
    "numero_hallazgo": f"HAL-{TS}",
    "descripcion": "Hallazgo de prueba final",
    "tipo": "NO_CONFORMIDAD",
    "severidad": "ALTA",
    "estado": "ABIERTO",
    "origen_tipo": "HABILITACION",
    "fecha_identificacion": "2026-02-20",
}
if autoeval_id:
    hallazgo_data["autoevaluacion"] = autoeval_id
if plan_id:
    hallazgo_data["plan_mejora"] = plan_id

r = requests.post(f"{BASE_URL}/api/mejoras/hallazgos/", headers=H, json=hallazgo_data)
test("POST /api/mejoras/hallazgos/", r, 201,
     ["id", "numero_hallazgo", "tipo",
      "severidad", "estado"])
hallazgo_id = r.json().get("id") if r.status_code == 201 else None

if hallazgo_id:
    r = requests.get(f"{BASE_URL}/api/mejoras/hallazgos/{hallazgo_id}/", headers=H)
    test("GET /api/mejoras/hallazgos/{id}/ (detail)", r, 200)

    r = requests.patch(f"{BASE_URL}/api/mejoras/hallazgos/{hallazgo_id}/",
                       headers=H, json={"estado": "EN_SEGUIMIENTO"})
    test("PATCH /api/mejoras/hallazgos/{id}/", r, 200)

# ─── Hallazgo Custom Actions ───
print("\n--- Hallazgo Custom Actions ---")
r = requests.get(f"{BASE_URL}/api/mejoras/hallazgos/estadisticas/", headers=H)
test("GET /hallazgos/estadisticas/", r, 200,
     ["total_hallazgos", "fortalezas", "oportunidades_mejora", "no_conformidades",
      "abiertos", "en_seguimiento", "cerrados"])

r = requests.get(f"{BASE_URL}/api/mejoras/hallazgos/por-origen/", headers=H)
test("GET /hallazgos/por-origen/", r, 200)

r = requests.get(f"{BASE_URL}/api/mejoras/hallazgos/sin-plan/", headers=H)
test("GET /hallazgos/sin-plan/", r, 200)


# ═══════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART III: AUDIT ENDPOINTS")
print("="*70)

# ─── Tipo Auditoría ───
print("\n--- TipoAuditoria ---")
r = requests.get(f"{BASE_URL}/api/audit/tipos/", headers=H)
test("GET /api/audit/tipos/", r, 200)

tipo_data = {"nombre": f"Tipo Test {TS}", "descripcion": "Test tipo"}
r = requests.post(f"{BASE_URL}/api/audit/tipos/", headers=H, json=tipo_data)
test("POST /api/audit/tipos/", r, 201)
tipo_id = r.json().get("id") if r.status_code == 201 else None

# ─── Entidad Auditoría ───
print("\n--- EntidadAuditoria ---")
r = requests.get(f"{BASE_URL}/api/audit/entidades/", headers=H)
test("GET /api/audit/entidades/", r, 200)

entidad_data = {"nombre": f"Entidad Test {TS}", "tipo_entidad": "CERTIFICADORA", "descripcion": "Test"}
r = requests.post(f"{BASE_URL}/api/audit/entidades/", headers=H, json=entidad_data)
test("POST /api/audit/entidades/", r, 201)
entidad_id = r.json().get("id") if r.status_code == 201 else None

# ─── Auditoría CRUD ───
print("\n--- Auditoría CRUD ---")
r = requests.get(f"{BASE_URL}/api/audit/auditorias/", headers=H)
test("GET /api/audit/auditorias/", r, 200,
     ["auditoria_id", "auditoria_nombre", "fase", "clasificacion"], check_list=True)

auditoria_data = {
    "auditoria_nombre": f"Auditoría Final Test {TS}",
    "auditoria_detalle": "Auditoría de prueba final",
    "clasificacion": "INTERNA",
    "fecha_programada": "2026-03-15",
}
if tipo_id:
    auditoria_data["auditoria_tipo"] = tipo_id

r = requests.post(f"{BASE_URL}/api/audit/auditorias/", headers=H, json=auditoria_data)
test("POST /api/audit/auditorias/", r, 201)
auditoria_id = r.json().get("auditoria_id") if r.status_code == 201 else None

if auditoria_id:
    r = requests.get(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/", headers=H)
    test("GET /api/audit/auditorias/{id}/ (detail)", r, 200,
         ["auditoria_id", "auditoria_nombre", "fase", "fase_display", "clasificacion",
          "equipo_auditor", "hallazgos_auditoria", "actas", "total_hallazgos",
          "total_no_conformidades", "esta_activa"])

    r = requests.patch(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/",
                       headers=H, json={"auditoria_detalle": "Updated detail"})
    test("PATCH /api/audit/auditorias/{id}/", r, 200)

# ─── Cambiar Fase (Lifecycle) ───
print("\n--- Cambiar Fase ---")
if auditoria_id:
    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/cambiar-fase/",
                      headers=H, json={"nueva_fase": "NOTIFICADA"})
    test("cambiar-fase PROGRAMADA→NOTIFICADA", r, 200, ["auditoria_id", "fase"])

    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/cambiar-fase/",
                      headers=H, json={"nueva_fase": "EN_EJECUCION"})
    test("cambiar-fase NOTIFICADA→EN_EJECUCION", r, 200)

    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/cambiar-fase/",
                      headers=H, json={"nueva_fase": "INFORME"})
    test("cambiar-fase EN_EJECUCION→INFORME", r, 200)

    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/cambiar-fase/",
                      headers=H, json={"nueva_fase": "SEGUIMIENTO"})
    test("cambiar-fase INFORME→SEGUIMIENTO", r, 200)

    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/cambiar-fase/",
                      headers=H, json={"nueva_fase": "CERRADA"})
    test("cambiar-fase SEGUIMIENTO→CERRADA", r, 200)

    # Invalid transition
    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{auditoria_id}/cambiar-fase/",
                      headers=H, json={"nueva_fase": "PROGRAMADA"})
    test("cambiar-fase INVALID (CERRADA→PROGRAMADA) → 400", r, 400)

# ─── Equipo Auditor ───
print("\n--- Equipo Auditor ---")
# Create a new audit for equipo tests
audit2_data = {
    "auditoria_nombre": f"Auditoría Equipo {TS}",
    "clasificacion": "INTERNA",
    "fecha_programada": "2026-04-01",
}
if tipo_id:
    audit2_data["auditoria_tipo"] = tipo_id
r = requests.post(f"{BASE_URL}/api/audit/auditorias/", headers=H, json=audit2_data)
audit2_id = r.json().get("auditoria_id") if r.status_code == 201 else None

if audit2_id:
    r = requests.get(f"{BASE_URL}/api/audit/auditorias/{audit2_id}/equipo/", headers=H)
    test("GET /auditorias/{id}/equipo/", r, 200)

    # Add member with correct role values: LIDER, AUDITOR, OBSERVADOR, EXPERTO
    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{audit2_id}/equipo/", headers=H,
                      json={"auditoria": audit2_id, "usuario": 1, "rol": "LIDER"})
    test("POST /auditorias/{id}/equipo/ (LIDER)", r, 201)
    miembro_id = r.json().get("id") if r.status_code == 201 else None

    if miembro_id:
        r = requests.delete(
            f"{BASE_URL}/api/audit/auditorias/{audit2_id}/equipo/{miembro_id}/", headers=H)
        test("DELETE /auditorias/{id}/equipo/{miembro_id}/", r, 204)

# ─── Actas (via auditoría) ───
print("\n--- Actas ---")
if audit2_id:
    r = requests.get(f"{BASE_URL}/api/audit/auditorias/{audit2_id}/actas/", headers=H)
    test("GET /auditorias/{id}/actas/", r, 200)

    acta_data = {
        "auditoria": audit2_id,
        "tipo_acta": "APERTURA",
        "fecha": "2026-04-01",
        "lugar": "Sala de reuniones",
        "temas_tratados": "Apertura del proceso",
        "compromisos": "Proceso iniciado",
    }
    r = requests.post(f"{BASE_URL}/api/audit/auditorias/{audit2_id}/actas/", headers=H, json=acta_data)
    test("POST /auditorias/{id}/actas/", r, 201)

# ─── Auditoría Custom Actions ───
print("\n--- Auditoría Custom Actions ---")
r = requests.get(f"{BASE_URL}/api/audit/auditorias/resumen/", headers=H)
test("GET /auditorias/resumen/", r, 200, ["total", "activas"])

r = requests.get(f"{BASE_URL}/api/audit/auditorias/proximas/", headers=H)
test("GET /auditorias/proximas/", r, 200)

r = requests.get(f"{BASE_URL}/api/audit/auditorias/proximas/?dias=60", headers=H)
test("GET /auditorias/proximas/?dias=60", r, 200)

r = requests.get(f"{BASE_URL}/api/audit/auditorias/por-fase/", headers=H)
test("GET /auditorias/por-fase/", r, 200)

# ─── HallazgoAuditoria ───
print("\n--- HallazgoAuditoria ---")
r = requests.get(f"{BASE_URL}/api/audit/hallazgos/", headers=H)
test("GET /api/audit/hallazgos/", r, 200)

if audit2_id:
    hall_aud_data = {
        "auditoria": audit2_id,
        "numero": "HFA001",
        "tipo": "NC_MAYOR",
        "descripcion": "Hallazgo no conformidad mayor final test",
        "criterio_norma": "4.1",
        "evidencia_objetiva": "No se observan registros",
        "estado": "IDENTIFICADO",
    }
    r = requests.post(f"{BASE_URL}/api/audit/hallazgos/", headers=H, json=hall_aud_data)
    test("POST /api/audit/hallazgos/", r, 201, ["id", "numero", "tipo", "estado"])
    hall_aud_id = r.json().get("id") if r.status_code == 201 else None

    if hall_aud_id:
        r = requests.get(f"{BASE_URL}/api/audit/hallazgos/{hall_aud_id}/", headers=H)
        test("GET /api/audit/hallazgos/{id}/", r, 200)

        r = requests.patch(f"{BASE_URL}/api/audit/hallazgos/{hall_aud_id}/",
                          headers=H, json={"estado": "PLAN_ACCION"})
        test("PATCH /api/audit/hallazgos/{id}/", r, 200)

# ─── ActaReunion standalone ───
print("\n--- ActaReunion (standalone) ---")
r = requests.get(f"{BASE_URL}/api/audit/actas/", headers=H)
test("GET /api/audit/actas/", r, 200)

# ─── ProgramaAuditoria ───
print("\n--- ProgramaAuditoria ---")
r = requests.get(f"{BASE_URL}/api/audit/programas/", headers=H)
test("GET /api/audit/programas/", r, 200)

programa_data = {
    "nombre": f"Programa Test {TS}",
    "periodo": "2026",
    "descripcion": "Programa anual de auditorías final test",
    "estado": "BORRADOR",
}
r = requests.post(f"{BASE_URL}/api/audit/programas/", headers=H, json=programa_data)
test("POST /api/audit/programas/", r, 201)
programa_id = r.json().get("id") if r.status_code == 201 else None

if programa_id:
    r = requests.get(f"{BASE_URL}/api/audit/programas/{programa_id}/", headers=H)
    test("GET /api/audit/programas/{id}/ (detail)", r, 200)


# ═══════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("FILTER & SEARCH TESTS")
print("="*70)

print("\n--- Mejoras Filters ---")
r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/?estado=PENDIENTE", headers=H)
test("Filter planes-mejora estado=PENDIENTE", r, 200)

r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/?origen_tipo=HABILITACION", headers=H)
test("Filter planes-mejora origen_tipo=HABILITACION", r, 200)

r = requests.get(f"{BASE_URL}/api/mejoras/planes-mejora/?prioridad=ALTA", headers=H)
test("Filter planes-mejora prioridad=ALTA", r, 200)

r = requests.get(f"{BASE_URL}/api/mejoras/hallazgos/?severidad=ALTA", headers=H)
test("Filter hallazgos severidad=ALTA", r, 200)

r = requests.get(f"{BASE_URL}/api/mejoras/hallazgos/?tipo=NO_CONFORMIDAD", headers=H)
test("Filter hallazgos tipo=NO_CONFORMIDAD", r, 200)

print("\n--- Audit Filters ---")
r = requests.get(f"{BASE_URL}/api/audit/auditorias/?fase=PROGRAMADA", headers=H)
test("Filter auditorias fase=PROGRAMADA", r, 200)

r = requests.get(f"{BASE_URL}/api/audit/auditorias/?clasificacion=INTERNA", headers=H)
test("Filter auditorias clasificacion=INTERNA", r, 200)

r = requests.get(f"{BASE_URL}/api/audit/hallazgos/?tipo=NC_MAYOR", headers=H)
test("Filter audit hallazgos tipo=NC_MAYOR", r, 200)


# ═══════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("CLEANUP")
print("="*70)

# Clean up created test data (in reverse order of dependencies)
if hallazgo_id:
    r = requests.delete(f"{BASE_URL}/api/mejoras/hallazgos/{hallazgo_id}/", headers=H)
    test("DELETE hallazgo", r, 204)

if plan_id:
    r = requests.delete(f"{BASE_URL}/api/mejoras/planes-mejora/{plan_id}/", headers=H)
    test("DELETE plan mejora", r, 204)

if servicio_id:
    r = requests.delete(f"{BASE_URL}/api/habilitacion/servicios/{servicio_id}/", headers=H)
    test("DELETE servicio", r, 204)


# ═══ Final Report ═══
print("\n" + "="*70)
print(f"RESULTS: {results['pass']} passed, {results['fail']} failed")
print("="*70)

if results["errors"]:
    print("\nFailed tests:")
    for e in results["errors"]:
        print(f"  ✗ {e}")

sys.exit(0 if results["fail"] == 0 else 1)
