"""
test_all_endpoints.py

Test comprehensivo de todos los endpoints nuevos:
- Mejoras: Planes de Mejora, Hallazgos, Soportes
- Audit: Auditorías (ciclo de vida), Hallazgos, Actas, Programas, Tipos, Entidades
- Habilitación: Integración con mejoras
"""

import os
import sys
import json
import random
import string
import tempfile
import requests

BASE_URL = 'http://localhost:8000/api'
TOKEN = None
HEADERS = {}

# ─── Contadores ───
passed = 0
failed = 0
errors = []


def log_result(test_name, response, expected_status=None):
    global passed, failed, errors
    ok = True
    if expected_status and response.status_code != expected_status:
        ok = False

    status_icon = "✅" if ok else "❌"
    print(f"  {status_icon} {test_name}: {response.status_code}", end="")

    if not ok:
        failed += 1
        detail = ""
        try:
            detail = response.json()
        except Exception:
            detail = response.text[:200]
        errors.append(f"{test_name}: expected {expected_status}, got {response.status_code} -> {detail}")
        print(f" (expected {expected_status})")
    else:
        passed += 1
        print()

    return ok


def get_token():
    global TOKEN, HEADERS
    resp = requests.post(f'{BASE_URL}/users/login/', json={
        'username': 'admin',
        'password': 'admin'
    })
    if resp.status_code == 200:
        TOKEN = resp.json().get('access') or resp.json().get('token')
        HEADERS = {'Authorization': f'Bearer {TOKEN}'}
        print(f"✅ Login exitoso (token: {TOKEN[:20]}...)")
    else:
        print(f"❌ Login fallido: {resp.status_code} {resp.text}")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════
# TEST MEJORAS
# ═══════════════════════════════════════════════════════════════════

def test_planes_mejora():
    print("\n═══ PLANES DE MEJORA ═══")

    # 1. LIST
    r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/', headers=HEADERS)
    log_result("GET /mejoras/planes-mejora/", r, 200)

    # 2. CREATE (use audit_id global if available, else skip FK validation issue)
    plan_num = f"PM-TEST-{''.join(random.choices(string.digits, k=6))}"
    plan_data = {
        "numero_plan": plan_num,
        "origen_tipo": "AUDITORIA",
        "descripcion": "Plan de prueba endpoints",
        "acciones_implementar": "Acciones de prueba",
        "estado": "PENDIENTE",
        "porcentaje_avance": 0,
        "fecha_inicio": "2026-02-20",
        "fecha_vencimiento": "2026-06-20",
    }
    # We need an auditoria for AUDITORIA origin - create one first
    pre_audit = requests.post(f'{BASE_URL}/audit/auditorias/', json={
        "auditoria_nombre": "Audit temp para plan",
        "fecha_programada": "2026-06-01",
    }, headers=HEADERS)
    if pre_audit.status_code == 201:
        plan_data["auditoria"] = pre_audit.json().get('auditoria_id')
    r = requests.post(f'{BASE_URL}/mejoras/planes-mejora/', json=plan_data, headers=HEADERS)
    log_result("POST /mejoras/planes-mejora/ (crear)", r, 201)
    plan_id = r.json().get('id') if r.status_code == 201 else None

    if plan_id:
        # 3. RETRIEVE
        r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/', headers=HEADERS)
        log_result("GET /mejoras/planes-mejora/{id}/", r, 200)

        # 4. PATCH
        r = requests.patch(f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/',
                           json={"porcentaje_avance": 50, "estado": "EN_CURSO"},
                           headers=HEADERS)
        log_result("PATCH /mejoras/planes-mejora/{id}/", r, 200)

    # 5. Vencidos
    r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/vencidos/', headers=HEADERS)
    log_result("GET /mejoras/planes-mejora/vencidos/", r, 200)

    # 6. Próximos a vencer
    r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/proximos-vencer/', headers=HEADERS)
    log_result("GET /mejoras/planes-mejora/proximos-vencer/", r, 200)

    # 7. Resumen
    r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/resumen/', headers=HEADERS)
    log_result("GET /mejoras/planes-mejora/resumen/", r, 200)

    # 8. Por origen
    r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/por-origen/', headers=HEADERS)
    log_result("GET /mejoras/planes-mejora/por-origen/", r, 200)

    return plan_id


def test_soportes(plan_id):
    print("\n═══ SOPORTES DE PLANES ═══")

    if not plan_id:
        print("  ⚠️  No hay plan_id, saltando tests de soportes")
        return

    # 1. GET soportes (vacío)
    r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/soportes/', headers=HEADERS)
    log_result("GET /mejoras/planes-mejora/{id}/soportes/ (vacío)", r, 200)

    # 2. POST soporte - PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'%PDF-1.4 fake pdf content for testing')
        pdf_path = f.name

    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'archivo': ('test_document.pdf', pdf_file, 'application/pdf')}
            data = {
                'tipo_soporte': 'EVIDENCIA',
                'descripcion': 'Soporte de prueba PDF',
            }
            r = requests.post(
                f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/soportes/',
                files=files, data=data, headers=HEADERS
            )
            log_result("POST /mejoras/planes-mejora/{id}/soportes/ (PDF)", r, 201)
            soporte_id = r.json().get('id') if r.status_code == 201 else None
    finally:
        os.unlink(pdf_path)

    # 3. POST soporte - PNG
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        png_path = f.name

    try:
        with open(png_path, 'rb') as png_file:
            files = {'archivo': ('foto_evidencia.png', png_file, 'image/png')}
            data = {
                'tipo_soporte': 'FOTOGRAFIA',
                'descripcion': 'Foto de evidencia',
            }
            r = requests.post(
                f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/soportes/',
                files=files, data=data, headers=HEADERS
            )
            log_result("POST /mejoras/planes-mejora/{id}/soportes/ (PNG)", r, 201)
    finally:
        os.unlink(png_path)

    # 4. POST soporte - Excel
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        f.write(b'PK\x03\x04' + b'\x00' * 100)
        xlsx_path = f.name

    try:
        with open(xlsx_path, 'rb') as xlsx_file:
            files = {'archivo': ('reporte.xlsx', xlsx_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {
                'tipo_soporte': 'INFORME',
                'descripcion': 'Reporte Excel',
            }
            r = requests.post(
                f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/soportes/',
                files=files, data=data, headers=HEADERS
            )
            log_result("POST /mejoras/planes-mejora/{id}/soportes/ (XLSX)", r, 201)
    finally:
        os.unlink(xlsx_path)

    # 5. POST soporte - extensión inválida
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
        f.write(b'\x00' * 50)
        exe_path = f.name

    try:
        with open(exe_path, 'rb') as exe_file:
            files = {'archivo': ('virus.exe', exe_file, 'application/octet-stream')}
            data = {
                'tipo_soporte': 'OTRO',
                'descripcion': 'Archivo no permitido',
            }
            r = requests.post(
                f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/soportes/',
                files=files, data=data, headers=HEADERS
            )
            log_result("POST soporte extensión inválida (.exe → 400)", r, 400)
    finally:
        os.unlink(exe_path)

    # 6. GET soportes (con datos)
    r = requests.get(f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/soportes/', headers=HEADERS)
    log_result("GET /mejoras/planes-mejora/{id}/soportes/ (con datos)", r, 200)
    soportes = r.json() if r.status_code == 200 else []
    if isinstance(soportes, dict):
        soportes = soportes.get('results', [])
    print(f"     → Soportes encontrados: {len(soportes)}")

    # 7. DELETE soporte
    if soporte_id:
        r = requests.delete(
            f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/soportes/{soporte_id}/',
            headers=HEADERS
        )
        log_result("DELETE soporte específico", r, 204)


def test_hallazgos_mejoras():
    print("\n═══ HALLAZGOS (MEJORAS) ═══")

    # 1. LIST
    r = requests.get(f'{BASE_URL}/mejoras/hallazgos/', headers=HEADERS)
    log_result("GET /mejoras/hallazgos/", r, 200)

    # 2. CREATE
    hal_num = f"HAL-TEST-{''.join(random.choices(string.digits, k=6))}"
    # Create an audit for AUDITORIA origin
    pre_audit2 = requests.post(f'{BASE_URL}/audit/auditorias/', json={
        "auditoria_nombre": "Audit temp para hallazgo",
        "fecha_programada": "2026-07-01",
    }, headers=HEADERS)
    hallazgo_data = {
        "numero_hallazgo": hal_num,
        "origen_tipo": "AUDITORIA",
        "tipo": "NO_CONFORMIDAD",
        "severidad": "ALTA",
        "descripcion": "Hallazgo de prueba automatizada",
        "area_responsable": "Calidad",
        "fecha_identificacion": "2026-02-20",
    }
    if pre_audit2.status_code == 201:
        hallazgo_data["auditoria"] = pre_audit2.json().get('auditoria_id')
    r = requests.post(f'{BASE_URL}/mejoras/hallazgos/', json=hallazgo_data, headers=HEADERS)
    log_result("POST /mejoras/hallazgos/ (crear)", r, 201)
    hallazgo_id = r.json().get('id') if r.status_code == 201 else None

    if hallazgo_id:
        # 3. RETRIEVE
        r = requests.get(f'{BASE_URL}/mejoras/hallazgos/{hallazgo_id}/', headers=HEADERS)
        log_result("GET /mejoras/hallazgos/{id}/", r, 200)

        # 4. PATCH
        r = requests.patch(f'{BASE_URL}/mejoras/hallazgos/{hallazgo_id}/',
                           json={"estado": "EN_SEGUIMIENTO"},
                           headers=HEADERS)
        log_result("PATCH /mejoras/hallazgos/{id}/", r, 200)

    # 5. Estadísticas
    r = requests.get(f'{BASE_URL}/mejoras/hallazgos/estadisticas/', headers=HEADERS)
    log_result("GET /mejoras/hallazgos/estadisticas/", r, 200)

    # 6. Por origen
    r = requests.get(f'{BASE_URL}/mejoras/hallazgos/por-origen/', headers=HEADERS)
    log_result("GET /mejoras/hallazgos/por-origen/", r, 200)

    # 7. Sin plan
    r = requests.get(f'{BASE_URL}/mejoras/hallazgos/sin-plan/', headers=HEADERS)
    log_result("GET /mejoras/hallazgos/sin-plan/", r, 200)

    return hallazgo_id


# ═══════════════════════════════════════════════════════════════════
# TEST AUDIT
# ═══════════════════════════════════════════════════════════════════

def test_audit_tipos():
    print("\n═══ AUDIT: TIPOS ═══")

    r = requests.get(f'{BASE_URL}/audit/tipos/', headers=HEADERS)
    log_result("GET /audit/tipos/", r, 200)

    tipo_name = f"Auditoría de Calidad {''.join(random.choices(string.digits, k=4))}"
    r = requests.post(f'{BASE_URL}/audit/tipos/', json={
        "nombre": tipo_name,
        "descripcion": "Auditoría enfocada en procesos de calidad",
        "requiere_entidad_externa": False,
    }, headers=HEADERS)
    log_result("POST /audit/tipos/ (crear)", r, 201)
    tipo_id = r.json().get('tipo_id') if r.status_code == 201 else None

    return tipo_id


def test_audit_entidades():
    print("\n═══ AUDIT: ENTIDADES ═══")

    r = requests.get(f'{BASE_URL}/audit/entidades/', headers=HEADERS)
    log_result("GET /audit/entidades/", r, 200)

    ent_name = f"Bureau Veritas {''.join(random.choices(string.digits, k=4))}"
    r = requests.post(f'{BASE_URL}/audit/entidades/', json={
        "nombre": ent_name,
        "tipo_entidad": "CERTIFICADORA",
        "contacto": "Juan Pérez",
        "email": "contacto@bureauveritas.com",
    }, headers=HEADERS)
    log_result("POST /audit/entidades/ (crear)", r, 201)
    entidad_id = r.json().get('entidad_id') if r.status_code == 201 else None

    return entidad_id


def test_audit_auditorias(tipo_id=None, entidad_id=None):
    print("\n═══ AUDIT: AUDITORÍAS (Ciclo de Vida) ═══")

    # 1. LIST
    r = requests.get(f'{BASE_URL}/audit/auditorias/', headers=HEADERS)
    log_result("GET /audit/auditorias/", r, 200)

    # 2. CREATE
    audit_data = {
        "auditoria_nombre": "Auditoría Integral Q1 2026",
        "auditoria_detalle": "Auditoría de procesos de calidad y habilitación",
        "clasificacion": "INTERNA",
        "norma_referencia": "ISO 9001:2015",
        "fecha_programada": "2026-03-15",
    }
    if tipo_id:
        audit_data["auditoria_tipo"] = tipo_id
    if entidad_id:
        audit_data["auditoria_entidad"] = entidad_id

    r = requests.post(f'{BASE_URL}/audit/auditorias/', json=audit_data, headers=HEADERS)
    log_result("POST /audit/auditorias/ (crear PROGRAMADA)", r, 201)
    audit_id = None
    if r.status_code == 201:
        resp_data = r.json()
        audit_id = resp_data.get('auditoria_id') or resp_data.get('id')
        fase = resp_data.get('fase', '?')
        print(f"     → Auditoría #{audit_id}, fase: {fase}")

    if audit_id:
        # 3. RETRIEVE
        r = requests.get(f'{BASE_URL}/audit/auditorias/{audit_id}/', headers=HEADERS)
        log_result("GET /audit/auditorias/{id}/ (detalle)", r, 200)

        # 4. Cambiar fase: PROGRAMADA → NOTIFICADA
        r = requests.post(f'{BASE_URL}/audit/auditorias/{audit_id}/cambiar-fase/',
                          json={"nueva_fase": "NOTIFICADA"},
                          headers=HEADERS)
        log_result("POST cambiar-fase (PROGRAMADA → NOTIFICADA)", r, 200)
        if r.status_code == 200:
            print(f"     → Fase actual: {r.json().get('fase', '?')}")

        # 5. Cambiar fase: NOTIFICADA → EN_EJECUCION
        r = requests.post(f'{BASE_URL}/audit/auditorias/{audit_id}/cambiar-fase/',
                          json={"nueva_fase": "EN_EJECUCION"},
                          headers=HEADERS)
        log_result("POST cambiar-fase (NOTIFICADA → EN_EJECUCION)", r, 200)

        # 6. Cambiar fase: EN_EJECUCION → INFORME
        r = requests.post(f'{BASE_URL}/audit/auditorias/{audit_id}/cambiar-fase/',
                          json={"nueva_fase": "INFORME"},
                          headers=HEADERS)
        log_result("POST cambiar-fase (EN_EJECUCION → INFORME)", r, 200)

        # 7. Transición inválida (debería fallar)
        r = requests.post(f'{BASE_URL}/audit/auditorias/{audit_id}/cambiar-fase/',
                          json={"nueva_fase": "PROGRAMADA"},
                          headers=HEADERS)
        log_result("POST cambiar-fase inválida (INFORME → PROGRAMADA → 400)", r, 400)

        # 8. Equipo auditor
        r = requests.get(f'{BASE_URL}/audit/auditorias/{audit_id}/equipo/', headers=HEADERS)
        log_result("GET /audit/auditorias/{id}/equipo/", r, 200)

        # 9. Actas
        r = requests.get(f'{BASE_URL}/audit/auditorias/{audit_id}/actas/', headers=HEADERS)
        log_result("GET /audit/auditorias/{id}/actas/", r, 200)

        # 10. Resumen (detail=False → no {id})
        r = requests.get(f'{BASE_URL}/audit/auditorias/resumen/', headers=HEADERS)
        log_result("GET /audit/auditorias/resumen/", r, 200)

    # 11. Próximas
    r = requests.get(f'{BASE_URL}/audit/auditorias/proximas/', headers=HEADERS)
    log_result("GET /audit/auditorias/proximas/", r, 200)

    # 12. Por fase
    r = requests.get(f'{BASE_URL}/audit/auditorias/por-fase/', headers=HEADERS)
    log_result("GET /audit/auditorias/por-fase/", r, 200)

    return audit_id


def test_audit_hallazgos(audit_id=None):
    print("\n═══ AUDIT: HALLAZGOS AUDITORÍA ═══")

    r = requests.get(f'{BASE_URL}/audit/hallazgos/', headers=HEADERS)
    log_result("GET /audit/hallazgos/", r, 200)

    if audit_id:
        ah_num = f"AH-TEST-{''.join(random.choices(string.digits, k=6))}"
        hallazgo_data = {
            "auditoria": audit_id,
            "numero": ah_num,
            "tipo": "NC_MENOR",
            "descripcion": "Falta procedimiento actualizado",
            "criterio_norma": "ISO 9001:2015 - 7.5.1",
            "evidencia_objetiva": "Se verificó que el documento está desactualizado",
        }
        r = requests.post(f'{BASE_URL}/audit/hallazgos/', json=hallazgo_data, headers=HEADERS)
        log_result("POST /audit/hallazgos/ (crear)", r, 201)
        hallazgo_id = None
        if r.status_code == 201:
            resp = r.json()
            hallazgo_id = resp.get('id') or resp.get('hallazgo_id')

        if hallazgo_id:
            r = requests.get(f'{BASE_URL}/audit/hallazgos/{hallazgo_id}/', headers=HEADERS)
            log_result("GET /audit/hallazgos/{id}/", r, 200)

    # Vencidos
    r = requests.get(f'{BASE_URL}/audit/hallazgos/vencidos/', headers=HEADERS)
    log_result("GET /audit/hallazgos/vencidos/", r, 200)

    # Estadísticas
    r = requests.get(f'{BASE_URL}/audit/hallazgos/estadisticas/', headers=HEADERS)
    log_result("GET /audit/hallazgos/estadisticas/", r, 200)


def test_audit_actas():
    print("\n═══ AUDIT: ACTAS ═══")

    r = requests.get(f'{BASE_URL}/audit/actas/', headers=HEADERS)
    log_result("GET /audit/actas/", r, 200)


def test_audit_programas():
    print("\n═══ AUDIT: PROGRAMAS ═══")

    r = requests.get(f'{BASE_URL}/audit/programas/', headers=HEADERS)
    log_result("GET /audit/programas/", r, 200)

    r = requests.post(f'{BASE_URL}/audit/programas/', json={
        "nombre": "Programa Anual de Auditorías 2026",
        "descripcion": "Plan de auditorías para el año 2026",
        "periodo": "2026",
        "estado": "BORRADOR",
    }, headers=HEADERS)
    log_result("POST /audit/programas/ (crear)", r, 201)


# ═══════════════════════════════════════════════════════════════════
# TEST HABILITACIÓN (integración con mejoras)
# ═══════════════════════════════════════════════════════════════════

def test_habilitacion_integration():
    print("\n═══ HABILITACIÓN (integración con mejoras) ═══")

    # Autoevaluaciones
    r = requests.get(f'{BASE_URL}/habilitacion/autoevaluaciones/', headers=HEADERS)
    log_result("GET /habilitacion/autoevaluaciones/", r, 200)

    autoevals = []
    if r.status_code == 200:
        data = r.json()
        autoevals = data.get('results', data) if isinstance(data, dict) else data

    if autoevals and len(autoevals) > 0:
        ae_id = autoevals[0].get('id')
        r = requests.get(f'{BASE_URL}/habilitacion/autoevaluaciones/{ae_id}/', headers=HEADERS)
        log_result("GET /habilitacion/autoevaluaciones/{id}/ (con mejoras_resumen)", r, 200)
        if r.status_code == 200:
            detail = r.json()
            has_mejoras = 'mejoras_resumen' in detail or 'planes_mejora_count' in detail
            print(f"     → Campos de mejoras presentes: {has_mejoras}")

    # Cumplimientos
    r = requests.get(f'{BASE_URL}/habilitacion/cumplimientos/', headers=HEADERS)
    log_result("GET /habilitacion/cumplimientos/", r, 200)

    cumples = []
    if r.status_code == 200:
        data = r.json()
        cumples = data.get('results', data) if isinstance(data, dict) else data

    if cumples and len(cumples) > 0:
        c_id = cumples[0].get('id')
        r = requests.get(f'{BASE_URL}/habilitacion/cumplimientos/{c_id}/', headers=HEADERS)
        log_result("GET /habilitacion/cumplimientos/{id}/ (con planes vinculados)", r, 200)
        if r.status_code == 200:
            detail = r.json()
            has_planes = 'planes_mejora_vinculados' in detail or 'planes_mejora_count' in detail
            has_hall = 'hallazgos_vinculados' in detail or 'hallazgos_count' in detail
            print(f"     → planes_mejora_vinculados: {has_planes}")
            print(f"     → hallazgos_vinculados: {has_hall}")


# ═══════════════════════════════════════════════════════════════════
# TEST API ROOT
# ═══════════════════════════════════════════════════════════════════

def test_api_root():
    print("\n═══ API ROOT ═══")

    r = requests.get(f'{BASE_URL}/mejoras/')
    log_result("GET /api/mejoras/ (router)", r, 200)

    r = requests.get(f'{BASE_URL}/audit/')
    log_result("GET /api/audit/ (router)", r, 200)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("  TEST COMPREHENSIVO DE ENDPOINTS")
    print("  Portal Web Backend - v2.0")
    print("=" * 60)

    get_token()

    # Test API Root
    test_api_root()

    # Test Mejoras
    plan_id = test_planes_mejora()
    test_soportes(plan_id)
    hallazgo_id = test_hallazgos_mejoras()

    # Test Audit
    tipo_id = test_audit_tipos()
    entidad_id = test_audit_entidades()
    audit_id = test_audit_auditorias(tipo_id, entidad_id)
    test_audit_hallazgos(audit_id)
    test_audit_actas()
    test_audit_programas()

    # Test Habilitación integration
    test_habilitacion_integration()

    # ─── Cleanup ───
    print("\n═══ CLEANUP ═══")
    if plan_id:
        r = requests.delete(f'{BASE_URL}/mejoras/planes-mejora/{plan_id}/', headers=HEADERS)
        log_result("DELETE plan de prueba", r, 204)
    if hallazgo_id:
        r = requests.delete(f'{BASE_URL}/mejoras/hallazgos/{hallazgo_id}/', headers=HEADERS)
        log_result("DELETE hallazgo de prueba", r, 204)

    # ─── Resumen ───
    print("\n" + "=" * 60)
    print(f"  RESULTADOS: ✅ {passed} pasaron | ❌ {failed} fallaron")
    print(f"  TOTAL: {passed + failed} tests")
    print("=" * 60)

    if errors:
        print("\n  ERRORES DETALLADOS:")
        for e in errors:
            print(f"    ❌ {e}")
        print()

    sys.exit(0 if failed == 0 else 1)
