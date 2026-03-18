# 🔧 GUÍA DE PRUEBA DE ENDPOINTS

## Comenzar

### 1. Activar Virtual Environment
```bash
cd d:\portal_web_backend
.\venv\Scripts\Activate.ps1
```

### 2. Iniciar Servidor
```bash
python manage.py runserver 8000
```

El servidor estará disponible en: `http://localhost:8000`

---

## Acceso a Admin Django

### URL
```
http://localhost:8000/admin/
```

### Credenciales (crear si no existen)
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### Probar la Interfaz Admin

**1. Ir a Prestadores**
```
http://localhost:8000/admin/habilitacion/datosprestador/
```
✅ Debería mostrar lista de prestadores sin errores

**2. Seleccionar una Sede con múltiples Prestadores**
- Buscar por nombre de sede
- Verificar que aparecen los prestadores asociados
- ✅ No debería haber error de `'Cumplimiento' object has no attribute 'servicio_sede'`

**3. Ir a Cumplimientos**
```
http://localhost:8000/admin/habilitacion/cumplimiento/
```
✅ Debería mostrar lista sin errores

---

## Pruebas de API REST

### Opción 1: Usar curl

#### 1. Obtener Token JWT
```bash
$response = curl -X POST http://localhost:8000/api/token/ `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"admin123"}'

# Guardar access token
$token = $response | ConvertFrom-Json | Select-Object -ExpandProperty access
```

#### 2. Listar Prestadores
```bash
curl -H "Authorization: Bearer $token" `
  http://localhost:8000/api/habilitacion/prestadores/
```

**Respuesta esperada**:
```json
[
  {
    "id": 1,
    "codigo_reps": "REPS-001",
    "clase_prestador_display": "Institución Prestadora de Servicios",
    "estado_display": "Habilitada",
    "proxima_vencer": true,
    "dias_vencimiento": 365
  },
  {
    "id": 2,
    "codigo_reps": "REPS-002",
    "clase_prestador_display": "Profesional de Salud",
    "estado_display": "En Proceso",
    "proxima_vencer": false,
    "dias_vencimiento": 180
  }
]
```

#### 3. Listar Servicios
```bash
curl -H "Authorization: Bearer $token" `
  http://localhost:8000/api/habilitacion/servicios/
```

**Respuesta esperada**:
```json
[
  {
    "id": 1,
    "codigo_servicio": "SERV-001",
    "nombre_servicio": "Urgencias",
    "prestador_codigo": "REPS-001",
    "modalidad_display": "Urgencias",
    "complejidad_display": "Alta",
    "estado_display": "Habilitado"
  }
]
```

#### 4. Crear Prestador
```bash
curl -X POST http://localhost:8000/api/habilitacion/prestadores/ `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "headquarters_id": 1,
    "codigo_reps": "REPS-TEST-NEW",
    "clase_prestador": "IPS",
    "estado_habilitacion": "EN_PROCESO",
    "fecha_vencimiento_habilitacion": "2025-12-31"
  }'
```

---

### Opción 2: Usar Postman

**1. Configurar Colección**
- Importar: `Portal_Habilitacion_API_completo.postman_collection.json`

**2. Autenticación**
- En "Authorization" → Bearer Token
- Usar token obtenido de `/api/token/`

**3. Endpoints Disponibles**

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/habilitacion/prestadores/` | Listar todos |
| GET | `/api/habilitacion/prestadores/{id}/` | Detalle |
| POST | `/api/habilitacion/prestadores/` | Crear |
| PUT | `/api/habilitacion/prestadores/{id}/` | Actualizar |
| DELETE | `/api/habilitacion/prestadores/{id}/` | Eliminar |
| GET | `/api/habilitacion/servicios/` | Listar servicios |
| POST | `/api/habilitacion/servicios/` | Crear servicio |
| GET | `/api/habilitacion/autoevaluaciones/` | Listar evaluaciones |
| GET | `/api/habilitacion/cumplimientos/` | Listar cumplimientos |

---

## Pruebas Manuales de Lógica

### Test 1: Crear Múltiples Prestadores en una Sede

```bash
# 1. Listar sedes
curl -H "Authorization: Bearer $token" \
  http://localhost:8000/api/companies/headquarters/

# 2. Usar sede existente (por ejemplo id=1)
# 3. Crear prestador 1
curl -X POST http://localhost:8000/api/habilitacion/prestadores/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "headquarters_id": 1,
    "codigo_reps": "REPS-MULTI-001",
    "clase_prestador": "IPS",
    "estado_habilitacion": "HABILITADA",
    "fecha_vencimiento_habilitacion": "2025-12-31"
  }'

# 4. Crear prestador 2 (misma sede)
curl -X POST http://localhost:8000/api/habilitacion/prestadores/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "headquarters_id": 1,
    "codigo_reps": "REPS-MULTI-002",
    "clase_prestador": "PROF",
    "estado_habilitacion": "EN_PROCESO",
    "fecha_vencimiento_habilitacion": "2025-06-30"
  }'

# 5. Verificar que ambos existen en la lista
curl -H "Authorization: Bearer $token" \
  "http://localhost:8000/api/habilitacion/prestadores/?headquarters_id=1"

# ✅ ÉXITO si ambos prestadores aparecen
```

---

### Test 2: Crear Servicios para Diferentes Prestadores

```bash
# 1. Obtener IDs de los prestadores creados (del test anterior)
# Prestador 1 ID = 1, Prestador 2 ID = 2

# 2. Crear servicio para prestador 1
curl -X POST http://localhost:8000/api/habilitacion/servicios/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "prestador_id": 1,
    "codigo_servicio": "SERV-MULTI-001-P1",
    "nombre_servicio": "Urgencias - Prestador 1",
    "modalidad": "URGENCIAS",
    "complejidad": "ALTA",
    "estado_habilitacion": "HABILITADO"
  }'

# 3. Crear servicio para prestador 2
curl -X POST http://localhost:8000/api/habilitacion/servicios/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "prestador_id": 2,
    "codigo_servicio": "SERV-MULTI-001-P2",
    "nombre_servicio": "Consulta Externa - Prestador 2",
    "modalidad": "AMBULATORIA",
    "complejidad": "MEDIA",
    "estado_habilitacion": "HABILITADO"
  }'

# 4. Verificar que servicios están correctamente asociados
curl -H "Authorization: Bearer $token" \
  http://localhost:8000/api/habilitacion/servicios/

# ✅ ÉXITO si los servicios muestran prestador_id diferente
```

---

### Test 3: Crear Autoevaluación y Cumplimientos

```bash
# 1. Crear autoevaluación para prestador 1
curl -X POST http://localhost:8000/api/habilitacion/autoevaluaciones/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "datos_prestador_id": 1,
    "periodo": 2025,
    "fecha_vencimiento": "2025-12-31",
    "estado": "BORRADOR"
  }'

# Guardar el ID de la autoevaluación (por ejemplo: 1)

# 2. Crear cumplimiento
curl -X POST http://localhost:8000/api/habilitacion/cumplimientos/ \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "autoevaluacion_id": 1,
    "servicio_sede_id": 1,
    "criterio_id": 1,
    "cumple": "CUMPLE"
  }'

# ✅ ÉXITO si no hay error de 'servicio_sede' field
```

---

## Verificaciones Esperadas

### ✅ Verificación 1: Campo `servicio_sede` Consistente
```bash
# Obtener detalle de cumplimiento
curl -H "Authorization: Bearer $token" \
  http://localhost:8000/api/habilitacion/cumplimientos/1/

# En JSON debería haber:
# "servicio_sede_id": 1  ← correcto
# NO debería haber: "servicio_prestador_id"
```

### ✅ Verificación 2: Múltiples Prestadores en Sede
```bash
# Filtrar prestadores por sede
curl -H "Authorization: Bearer $token" \
  "http://localhost:8000/api/habilitacion/prestadores/?headquarters_id=1"

# Debería devolver > 1 prestador
```

### ✅ Verificación 3: Admin Sin Errores
Navegar a:
```
http://localhost:8000/admin/habilitacion/cumplimiento/
```
✅ No debería mostrar: `'Cumplimiento' object has no attribute 'servicio_sede'`

---

## Script Automatizado de Prueba

Ejecutar el script manual que valida todo:
```bash
python test_endpoints_manual.py
```

Salida esperada:
```
[PRUEBA 1] Validar que múltiples prestadores pueden existir en misma sede...
✅ PRUEBA 1 PASÓ

[PRUEBA 2] Validar que servicios están ligados a prestador, no a sede...
✅ PRUEBA 2 PASÓ

[PRUEBA 3] Validar estructura de datos en serialización...
✅ PRUEBA 3 PASÓ

CONCLUSIÓN: Sistema funcionando correctamente con nueva lógica ✅
```

---

## Troubleshooting

### Error: `'Cumplimiento' object has no attribute 'servicio_sede'`
**Causa**: Campo aún se llama `servicio_prestador`
**Solución**: Verificar que migraciones se aplicaron:
```bash
python manage.py migrate habilitacion
```

### Error: `Invalid HTTP_HOST header: 'testserver'`
**Causa**: Cliente de prueba no está validando hosts
**Solución**: Agregar a `ALLOWED_HOSTS` en settings.py:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
```

### Error: `UNIQUE constraint failed`
**Causa**: Prestador con mismo código_reps ya existe
**Solución**: Usar código_reps único en cada prueba

### Error: `Foreign key constraint failed`
**Causa**: Intentar crear servicio con prestador_id que no existe
**Solución**: Verificar IDs con GET antes de POST

---

## Checklist de Validación

- [ ] Servidor corre sin errores: `python manage.py runserver`
- [ ] Admin accesible: `http://localhost:8000/admin/`
- [ ] Login funciona con credenciales
- [ ] Pueden listar prestadores: GET `/api/habilitacion/prestadores/`
- [ ] Pueden crear prestador: POST `/api/habilitacion/prestadores/`
- [ ] Pueden crear 2+ prestadores en misma sede
- [ ] Pueden crear servicios para cada prestador
- [ ] Campo `servicio_sede` en cumplimientos (no `servicio_prestador`)
- [ ] Admin de cumplimientos sin errores: `/admin/habilitacion/cumplimiento/`
- [ ] Tests pasan: `python manage.py test habilitacion` (30+ pasando)

---

_Guía de Pruebas: 2026-03-11_
