"""
Test script for all new endpoints:
- Mejoras: SoportePlan upload/list/delete
- Audit: Full lifecycle, equipo, hallazgos, actas, programas
- Habilitacion: Integration fields
"""
import requests
import json
import os
import tempfile

BASE = "http://localhost:8000/api"
TOKEN = None
RESULTS = {"passed": 0, "failed": 0, "errors": []}

def get_token():
    global TOKEN
    r = requests.post(f"{BASE}/users/login/", json={"username": "admin", "password": "admin"})
    if r.status_code == 200:
        TOKEN = r.json().get("access") or r.json().get("token")
        print(f"[OK] Auth token obtained")
    else:
        print(f"[FAIL] Auth failed: {r.status_code} {r.text[:200]}")
    return TOKEN

def h():
    return {"Authorization": f"Bearer {TOKEN}"}

def test(name, method, url, expected_status=None, data=None, files=None, json_data=None):
    try:
        kwargs = {"headers": h()}
        if files:
            kwargs["files"] = files
            if data:
                kwargs["data"] = data
        elif json_data is not None:
            kwargs["json"] = json_data
        elif data is not None:
            kwargs["json"] = data
        
        r = getattr(requests, method)(url, **kwargs)
        
        if expected_status:
            if isinstance(expected_status, list):
                ok = r.status_code in expected_status
            else:
                ok = r.status_code == expected_status
        else:
            ok = r.status_code < 400
        
        if ok:
            RESULTS["passed"] += 1
            print(f"  [PASS] {name} -> {r.status_code}")
        else:
            RESULTS["failed"] += 1
            RESULTS["errors"].append(f"{name}: expected {expected_status}, got {r.status_code}")
            print(f"  [FAIL] {name} -> {r.status_code} (expected {expected_status})")
            if r.status_code >= 400:
                print(f"         Response: {r.text[:300]}")
        
        try:
            return r.json(), r.status_code
        except:
            return r.text, r.status_code
    except Exception as e:
        RESULTS["failed"] += 1
        RESULTS["errors"].append(f"{name}: Exception {e}")
        print(f"  [ERROR] {name} -> {e}")
        return None, 0


def test_audit_catalogos():
    print("\n=== AUDIT: Tipos de Auditoría ===")
    
    # Create tipo
    data, sc = test("Create TipoAuditoria", "post", f"{BASE}/audit/tipos/",
        expected_status=201,
        data={"nombre": "Auditoría de Calidad", "descripcion": "Auditoría enfocada en calidad", "requiere_entidad_externa": False})
    tipo_id = data.get("tipo_auditoria_id") if isinstance(data, dict) else None
    
    # List
    test("List TipoAuditoria", "get", f"{BASE}/audit/tipos/", expected_status=200)
    
    # Create entidad
    print("\n=== AUDIT: Entidades de Auditoría ===")
    data, sc = test("Create EntidadAuditoria", "post", f"{BASE}/audit/entidades/",
        expected_status=201,
        data={
            "nombre": "Bureau Veritas",
            "tipo_entidad": "CERTIFICADORA",
            "contacto": "Juan Perez",
            "telefono": "3001234567",
            "email": "contacto@bv.com"
        })
    entidad_id = data.get("entidad_auditoria_id") if isinstance(data, dict) else None
    
    # List
    test("List EntidadAuditoria", "get", f"{BASE}/audit/entidades/", expected_status=200)
    
    return tipo_id, entidad_id


def test_audit_lifecycle(tipo_id, entidad_id):
    print("\n=== AUDIT: Crear Auditoría ===")
    
    audit_data = {
        "titulo": "Auditoría de Certificación ISO 9001",
        "clasificacion": "EXTERNA",
        "tipo_auditoria": tipo_id,
        "entidad_auditoria": entidad_id,
        "fecha_programada": "2026-03-15",
        "fecha_auditoria": "2026-03-20",
        "alcance": "Todos los procesos del sistema de gestión de calidad",
        "objetivo": "Obtener certificación ISO 9001:2015",
        "norma_referencia": "ISO 9001:2015"
    }
    data, sc = test("Create Auditoria", "post", f"{BASE}/audit/auditorias/",
        expected_status=201, data=audit_data)
    
    if not isinstance(data, dict):
        print(f"  [SKIP] Cannot continue lifecycle - create failed")
        return None
    
    audit_id = data.get("auditoria_id")
    print(f"  -> Auditoría ID: {audit_id}, Fase: {data.get('fase')}")
    
    # Detail
    test("Detail Auditoria", "get", f"{BASE}/audit/auditorias/{audit_id}/",
        expected_status=200)
    
    # List
    data, sc = test("List Auditorias", "get", f"{BASE}/audit/auditorias/",
        expected_status=200)
    
    # Phase transitions
    print("\n=== AUDIT: Ciclo de Vida (Fases) ===")
    
    phases = ["NOTIFICADA", "EN_EJECUCION", "INFORME", "SEGUIMIENTO", "CERRADA"]
    for fase in phases:
        data, sc = test(f"Cambiar fase -> {fase}", "post",
            f"{BASE}/audit/auditorias/{audit_id}/cambiar-fase/",
            expected_status=200,
            data={"nueva_fase": fase})
        if isinstance(data, dict):
            print(f"     Fase actual: {data.get('fase_actual', data.get('fase'))}")
    
    # Resumen
    print("\n=== AUDIT: Endpoints Especiales ===")
    test("Resumen auditorías", "get", f"{BASE}/audit/auditorias/resumen/",
        expected_status=200)
    
    test("Próximas auditorías", "get", f"{BASE}/audit/auditorias/proximas/",
        expected_status=200)
    
    test("Por fase", "get", f"{BASE}/audit/auditorias/por-fase/",
        expected_status=200)
    
    return audit_id


def test_audit_equipo(audit_id):
    print("\n=== AUDIT: Equipo Auditor ===")
    
    # First, create a second auditoría in PROGRAMADA to add equipo (closed one can't be modified)
    # Actually let's create a new one for equipo tests
    data, sc = test("Create Auditoria para equipo", "post", f"{BASE}/audit/auditorias/",
        expected_status=201,
        data={
            "titulo": "Auditoría Interna Q1",
            "clasificacion": "INTERNA",
            "fecha_programada": "2026-04-01",
            "fecha_auditoria": "2026-04-10",
            "alcance": "Procesos administrativos",
            "objetivo": "Verificar cumplimiento"
        })
    
    if not isinstance(data, dict):
        print("  [SKIP] Cannot test equipo")
        return
    
    eq_audit_id = data.get("auditoria_id")
    
    # Add member
    data, sc = test("Add miembro equipo", "post",
        f"{BASE}/audit/auditorias/{eq_audit_id}/equipo/",
        expected_status=201,
        data={"usuario": 1, "rol": "LIDER", "area_responsable": "Calidad"})
    
    miembro_id = data.get("id") if isinstance(data, dict) else None
    
    # List equipo
    test("List equipo", "get", f"{BASE}/audit/auditorias/{eq_audit_id}/equipo/",
        expected_status=200)
    
    # Remove member
    if miembro_id:
        test("Remove miembro", "delete",
            f"{BASE}/audit/auditorias/{eq_audit_id}/eliminar-miembro/",
            expected_status=204,
            data={"miembro_id": miembro_id})
    
    return eq_audit_id


def test_audit_hallazgos(audit_id):
    print("\n=== AUDIT: Hallazgos de Auditoría ===")
    
    # Need an audit in EN_EJECUCION phase for hallazgos
    # Let's use the equipo audit and advance it
    data, sc = test("Avanzar a NOTIFICADA", "post",
        f"{BASE}/audit/auditorias/{audit_id}/cambiar-fase/",
        expected_status=200,
        data={"nueva_fase": "NOTIFICADA"})
    
    data, sc = test("Avanzar a EN_EJECUCION", "post",
        f"{BASE}/audit/auditorias/{audit_id}/cambiar-fase/",
        expected_status=200,
        data={"nueva_fase": "EN_EJECUCION"})
    
    # Create hallazgo
    data, sc = test("Create HallazgoAuditoria", "post", f"{BASE}/audit/hallazgos/",
        expected_status=201,
        data={
            "auditoria": audit_id,
            "tipo": "NC_MENOR",
            "descripcion": "No se encontró evidencia del control de documentos",
            "criterio_norma": "ISO 9001:2015 Cláusula 7.5",
            "evidencia_objetiva": "Se revisaron 10 documentos, 3 sin control",
            "fecha_limite_accion": "2026-05-01",
            "responsable_accion": 1
        })
    
    hallazgo_id = data.get("hallazgo_id") if isinstance(data, dict) else None
    
    # List hallazgos
    test("List Hallazgos", "get", f"{BASE}/audit/hallazgos/", expected_status=200)
    
    # Detail
    if hallazgo_id:
        test("Detail Hallazgo", "get", f"{BASE}/audit/hallazgos/{hallazgo_id}/",
            expected_status=200)
    
    # Estadísticas
    test("Estadísticas hallazgos", "get", f"{BASE}/audit/hallazgos/estadisticas/",
        expected_status=200)
    
    # Vencidos
    test("Hallazgos vencidos", "get", f"{BASE}/audit/hallazgos/vencidos/",
        expected_status=200)
    
    return hallazgo_id


def test_audit_actas(audit_id):
    print("\n=== AUDIT: Actas de Reunión ===")
    
    # Create acta via auditoría action
    data, sc = test("Create Acta (via auditoria)", "post",
        f"{BASE}/audit/auditorias/{audit_id}/actas/",
        expected_status=201,
        data={
            "tipo_acta": "APERTURA",
            "fecha": "2026-04-10T09:00:00",
            "lugar": "Sala de Reuniones A",
            "asistentes": "Director, Jefe de Calidad, Auditor Líder",
            "temas_tratados": "Alcance, objetivo, metodología",
            "compromisos": "Entregar documentación antes del 12 de abril"
        })
    
    acta_id = data.get("id") if isinstance(data, dict) else None
    
    # List actas via auditoría
    test("List Actas (via auditoria)", "get",
        f"{BASE}/audit/auditorias/{audit_id}/actas/",
        expected_status=200)
    
    # Direct CRUD
    test("List Actas (direct)", "get", f"{BASE}/audit/actas/", expected_status=200)
    
    if acta_id:
        test("Detail Acta", "get", f"{BASE}/audit/actas/{acta_id}/", expected_status=200)


def test_audit_programas():
    print("\n=== AUDIT: Programas de Auditoría ===")
    
    data, sc = test("Create Programa", "post", f"{BASE}/audit/programas/",
        expected_status=201,
        data={
            "nombre": "Programa Anual de Auditorías 2026",
            "periodo": "2026",
            "estado": "BORRADOR",
            "responsable": 1
        })
    
    programa_id = data.get("id") if isinstance(data, dict) else None
    
    test("List Programas", "get", f"{BASE}/audit/programas/", expected_status=200)
    
    if programa_id:
        test("Detail Programa", "get", f"{BASE}/audit/programas/{programa_id}/",
            expected_status=200)


def test_mejoras_soportes():
    print("\n=== MEJORAS: Soportes de Plan ===")
    
    # First create a plan
    data, sc = test("Create PlanMejora (para soportes)", "post",
        f"{BASE}/mejoras/planes-mejora/",
        expected_status=201,
        data={
            "titulo": "Plan de mejora para prueba de soportes",
            "descripcion": "Plan creado para probar la carga de soportes",
            "origen_tipo": "AUTOEVALUACION",
            "responsable": 1,
            "fecha_inicio": "2026-02-20",
            "fecha_vencimiento": "2026-06-30"
        })
    
    if not isinstance(data, dict):
        print("  [SKIP] Cannot test soportes - plan creation failed")
        return
    
    plan_id = data.get("plan_mejora_id")
    print(f"  -> Plan ID: {plan_id}")
    
    # Upload a test PDF-like file
    tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb")
    tmp_pdf.write(b"%PDF-1.4 test content for soporte upload")
    tmp_pdf.close()
    
    with open(tmp_pdf.name, "rb") as f:
        data, sc = test("Upload soporte PDF", "post",
            f"{BASE}/mejoras/planes-mejora/{plan_id}/soportes/",
            expected_status=201,
            files={"archivo": ("test_document.pdf", f, "application/pdf")},
            data={"tipo_soporte": "EVIDENCIA", "descripcion": "Documento de prueba"})
    
    soporte_id = data.get("id") if isinstance(data, dict) else None
    
    # Upload a PNG
    tmp_png = tempfile.NamedTemporaryFile(suffix=".png", delete=False, mode="wb")
    tmp_png.write(b"\x89PNG\r\n\x1a\n fake png content")
    tmp_png.close()
    
    with open(tmp_png.name, "rb") as f:
        data, sc = test("Upload soporte PNG", "post",
            f"{BASE}/mejoras/planes-mejora/{plan_id}/soportes/",
            expected_status=201,
            files={"archivo": ("foto_evidencia.png", f, "image/png")},
            data={"tipo_soporte": "FOTOGRAFIA", "descripcion": "Foto de evidencia"})
    
    soporte2_id = data.get("id") if isinstance(data, dict) else None
    
    # List soportes
    data, sc = test("List soportes", "get",
        f"{BASE}/mejoras/planes-mejora/{plan_id}/soportes/",
        expected_status=200)
    
    if isinstance(data, list):
        print(f"     Soportes encontrados: {len(data)}")
    
    # Check plan detail includes soportes
    data, sc = test("Plan detail con soportes", "get",
        f"{BASE}/mejoras/planes-mejora/{plan_id}/",
        expected_status=200)
    
    if isinstance(data, dict):
        print(f"     soportes_count: {data.get('soportes_count')}")
        print(f"     soportes: {len(data.get('soportes', []))} items")
    
    # Delete soporte
    if soporte_id:
        test("Delete soporte", "delete",
            f"{BASE}/mejoras/planes-mejora/{plan_id}/eliminar-soporte/",
            expected_status=204,
            data={"soporte_id": soporte_id})
    
    # Verify count after delete
    data, sc = test("List soportes after delete", "get",
        f"{BASE}/mejoras/planes-mejora/{plan_id}/soportes/",
        expected_status=200)
    
    if isinstance(data, list):
        print(f"     Soportes restantes: {len(data)}")
    
    # Clean up temp files
    os.unlink(tmp_pdf.name)
    os.unlink(tmp_png.name)
    
    # Test invalid extension
    tmp_exe = tempfile.NamedTemporaryFile(suffix=".exe", delete=False, mode="wb")
    tmp_exe.write(b"MZ fake exe")
    tmp_exe.close()
    
    with open(tmp_exe.name, "rb") as f:
        data, sc = test("Upload soporte .exe (should fail)", "post",
            f"{BASE}/mejoras/planes-mejora/{plan_id}/soportes/",
            expected_status=400,
            files={"archivo": ("malware.exe", f, "application/octet-stream")},
            data={"tipo_soporte": "OTRO", "descripcion": "Bad file"})
    
    os.unlink(tmp_exe.name)


def test_habilitacion_integration():
    print("\n=== HABILITACION: Integración con Mejoras ===")
    
    # List autoevaluaciones
    data, sc = test("List Autoevaluaciones", "get",
        f"{BASE}/habilitacion/autoevaluaciones/", expected_status=200)
    
    if isinstance(data, dict) and "results" in data:
        results = data["results"]
    elif isinstance(data, list):
        results = data
    else:
        results = []
    
    if results:
        ae_id = results[0].get("autoevaluacion_id")
        data, sc = test("Detail Autoevaluacion (con mejoras_resumen)", "get",
            f"{BASE}/habilitacion/autoevaluaciones/{ae_id}/",
            expected_status=200)
        if isinstance(data, dict):
            print(f"     mejoras_resumen: {data.get('mejoras_resumen', 'N/A')}")
            print(f"     planes_mejora_count: {data.get('planes_mejora_count', 'N/A')}")
            print(f"     hallazgos_count: {data.get('hallazgos_count', 'N/A')}")
    else:
        print("  [INFO] No autoevaluaciones found to test integration")
    
    # List cumplimientos
    data, sc = test("List Cumplimientos", "get",
        f"{BASE}/habilitacion/cumplimientos/", expected_status=200)
    
    if isinstance(data, dict) and "results" in data:
        cump_results = data["results"]
    elif isinstance(data, list):
        cump_results = data
    else:
        cump_results = []
    
    if cmp_results := cump_results:
        cump_id = cmp_results[0].get("cumplimiento_id")
        data, sc = test("Detail Cumplimiento (con planes vinculados)", "get",
            f"{BASE}/habilitacion/cumplimientos/{cump_id}/",
            expected_status=200)
        if isinstance(data, dict):
            print(f"     planes_mejora_vinculados: {data.get('planes_mejora_vinculados', 'N/A')}")
            print(f"     hallazgos_vinculados: {data.get('hallazgos_vinculados', 'N/A')}")
    else:
        print("  [INFO] No cumplimientos found to test integration")


def test_existing_endpoints():
    print("\n=== EXISTING: Verificar endpoints previos ===")
    
    endpoints = [
        ("Users profile", "get", f"{BASE}/users/profile/"),
        ("Companies", "get", f"{BASE}/companies/companies/"),
        ("Processes", "get", f"{BASE}/processes/procesos/"),
        ("Mejoras planes", "get", f"{BASE}/mejoras/planes-mejora/"),
        ("Mejoras hallazgos", "get", f"{BASE}/mejoras/hallazgos/"),
        ("Mejoras resumen", "get", f"{BASE}/mejoras/planes-mejora/resumen/"),
        ("Mejoras stats", "get", f"{BASE}/mejoras/hallazgos/estadisticas/"),
    ]
    
    for name, method, url in endpoints:
        test(name, method, url, expected_status=200)


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: All New Endpoints")
    print("=" * 60)
    
    get_token()
    if not TOKEN:
        print("Cannot proceed without authentication")
        exit(1)
    
    # 1. Existing endpoints still work
    test_existing_endpoints()
    
    # 2. Audit catalogos
    tipo_id, entidad_id = test_audit_catalogos()
    
    # 3. Audit lifecycle
    audit_id = test_audit_lifecycle(tipo_id, entidad_id)
    
    # 4. Audit equipo
    eq_audit_id = test_audit_equipo(audit_id)
    
    # 5. Audit hallazgos
    if eq_audit_id:
        test_audit_hallazgos(eq_audit_id)
    
    # 6. Audit actas
    if eq_audit_id:
        test_audit_actas(eq_audit_id)
    
    # 7. Audit programas
    test_audit_programas()
    
    # 8. Mejoras soportes
    test_mejoras_soportes()
    
    # 9. Habilitacion integration
    test_habilitacion_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print(f"  RESULTS: {RESULTS['passed']} passed, {RESULTS['failed']} failed")
    print("=" * 60)
    
    if RESULTS["errors"]:
        print("\nFailures:")
        for e in RESULTS["errors"]:
            print(f"  - {e}")
    
    print("\nDone!")
