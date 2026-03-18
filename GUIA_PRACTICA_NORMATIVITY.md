# 🧪 GUÍA PRÁCTICA - CÓMO PROBAR ENDPOINTS DE NORMATIVITY

## Paso 1: Iniciar el Servidor

```bash
cd d:\portal_web_backend
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

Deberías ver:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## Paso 2: Probar Endpoints

### Opción A: En el Navegador (para GET requests)

#### 1. Listar Estándares
```
http://127.0.0.1:8000/api/normativity/estandares/
```

✅ Verás una lista de 7 estándares

#### 2. Listar Criterios
```
http://127.0.0.1:8000/api/normativity/criterios/
```

✅ Verás una lista de 32 criterios

#### 3. Criterios de un estándar específico
```
http://127.0.0.1:8000/api/normativity/criterios/?estandar=1
```

✅ Verás criterios filtrados

#### 4. Criterios mandatorios
```
http://127.0.0.1:8000/api/normativity/criterios/mandatorios/
```

✅ Verás solo criterios marcados como mandatorios

#### 5. Criterios que requieren evidencia
```
http://127.0.0.1:8000/api/normativity/criterios/con_evidencia/
```

✅ Verás criterios que requieren documentos de evidencia

#### 6. Criterios por complejidad
```
http://127.0.0.1:8000/api/normativity/criterios/por_complejidad/?complejidad=ALTA
```

✅ Cambia ALTA por MEDIA o BAJA

---

### Opción B: Con PowerShell/cURL

#### Listar criterios y convertir a tabla:
```powershell
$response = curl -s "http://127.0.0.1:8000/api/normativity/criterios/" | ConvertFrom-Json
$response | Select-Object codigo, nombre, complejidad_display, es_mandatorio | Format-Table -AutoSize | Out-Host
```

#### Contar criterios por estándar:
```powershell
$response = curl -s "http://127.0.0.1:8000/api/normativity/estandares/" | ConvertFrom-Json
foreach ($e in $response) {
    $count = ($e.criterios | Measure-Object).Count
    Write-Host "$($e.codigo_display): $count criterios"
}
```

---

### Opción C: Con Postman

1. **Crear Colección** o Importar:
   - Archivo: `Portal_Habilitacion_API_completo.postman_collection.json`

2. **Agregar Requests:**

   **Request 1:**
   ```
   GET http://127.0.0.1:8000/api/normativity/estandares/
   ```

   **Request 2:**
   ```
   GET http://127.0.0.1:8000/api/normativity/criterios/
   ```

   **Request 3 (con filtro):**
   ```
   GET http://127.0.0.1:8000/api/normativity/criterios/?estandar=1&complejidad=ALTA
   ```

3. **Click "Send"** en cada request

---

## Paso 3: Verificar Respuestas

### GET /api/normativity/estandares/

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "codigo": "DOT",
    "codigo_display": "Dotación, Medicamentos e Insumos",
    "nombre": "Dotación, Medicamentos e Insumos",
    "descripcion": "Los servicios de salud deben garantizar...",
    "estado": true,
    "version_resolucion": "3100/2019",
    "criterios": [
      {
        "id": 1,
        "codigo": "1.1",
        "nombre": "Disponibilidad de medicamentos",
        "complejidad": "MEDIA",
        "es_mandatorio": true
      }
    ],
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_actualizacion": "2024-01-15T10:30:00Z"
  }
]
```

✅ **Status 200 OK**

### GET /api/normativity/criterios/

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "estandar": 1,
    "estandar_display": "Dotación, Medicamentos e Insumos",
    "codigo": "1.1",
    "nombre": "Disponibilidad de medicamentos",
    "descripcion": "Descripción completa del criterio...",
    "complejidad": "MEDIA",
    "complejidad_display": "Media",
    "aplica_todos": true,
    "es_mandatorio": true,
    "requiere_evidencia_documental": false,
    "estado": true
  }
]
```

✅ **Status 200 OK**

---

## Paso 4: Problemas Comunes

### ❌ Error: "404 Not Found"

**Causa:** URL incorrecto

| ❌ Incorrecto | ✅ Correcto |
|---|---|
| `/api/normativity/criterio/` | `/api/normativity/criterios/` |
| `/api/normativity/estandar/` | `/api/normativity/estandares/` |

**Solución:** Verifica que uses el plural

### ❌ Error: "400 Bad Request"

**Causa:** Parámetro de filtro inválido

```
http://127.0.0.1:8000/api/normativity/criterios/por_complejidad/
# ❌ Falta el parámetro
```

```
http://127.0.0.1:8000/api/normativity/criterios/por_complejidad/?complejidad=BAJISIMO
# ❌ Valor incorrecto (debe ser: BAJA, MEDIA, ALTA)
```

**Solución:** Incluye parámetros válidos

### ❌ Error: "Invalid HTTP_HOST"

**Causa:** Django no reconoce el host

**Solución:** Asegúrate que ALLOWED_HOSTS en settings.py incluya:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
```

---

## 📊 Script de Verificación Completa

Ejecuta este script para verificar que TODO funciona:

```powershell
$base_url = "http://127.0.0.1:8000/api/normativity"

# Test 1
Write-Host "[TEST 1] Listar estándares"
$response = curl -s "$base_url/estandares/" | ConvertFrom-Json
Write-Host "OK: $($response.Count) estándares" -ForegroundColor Green

# Test 2
Write-Host "[TEST 2] Listar criterios"
$response = curl -s "$base_url/criterios/" | ConvertFrom-Json
Write-Host "OK: $($response.Count) criterios" -ForegroundColor Green

# Test 3
Write-Host "[TEST 3] Mandatorios"
$response = curl -s "$base_url/criterios/mandatorios/" | ConvertFrom-Json
Write-Host "OK: $($response.Count) mandatorios" -ForegroundColor Green

# Test 4
Write-Host "[TEST 4] Con evidencia"
$response = curl -s "$base_url/criterios/con_evidencia/" | ConvertFrom-Json
Write-Host "OK: $($response.Count) con evidencia" -ForegroundColor Green

Write-Host "`nTodos los endpoints funcionan correctamente!" -ForegroundColor Green
```

---

## 🔍 Admin Django

También puedes verificar los datos en el admin Django:

1. Navega a: `http://127.0.0.1:8000/admin/`

2. Login con credenciales (si no tienes, crea con: `python manage.py createsuperuser`)

3. Ve a:
   - **Estándares**: Verás los 7 estándares con badges coloreados
   - **Criterios**: Verás los 32 criterios con filtros avanzados
   - **Documentos Normativos**: Vacío (sin datos de prueba)

---

## 💡 Casos de Uso

### 1. Frontend: Cargar Taxonomía Completa
```javascript
async function cargarTaxonomia() {
  const response = await fetch('http://localhost:8000/api/normativity/estandares/todos/');
  const estandares = await response.json();
  // Cargar select con estandares
  estandares.forEach(e => {
    console.log(`${e.codigo_display}: ${e.criterios.length} criterios`);
  });
}
```

### 2. Filtrar Criterios Complejos
```javascript
async function filtrarCriterios(estandarId, complejidad) {
  const url = `http://localhost:8000/api/normativity/criterios/?estandar=${estandarId}&complejidad=${complejidad}`;
  const response = await fetch(url);
  return await response.json();
}
```

### 3. Buscar Criterios Mandatorios
```javascript
async function obtenerMandatorios() {
  const response = await fetch('http://localhost:8000/api/normativity/criterios/mandatorios/');
  return await response.json();
}
```

---

## ✅ Checklist de Validación

- [ ] Servidor corriendo: `python manage.py runserver 8000`
- [ ] Puedo acceder a: `http://127.0.0.1:8000/api/normativity/estandares/`
- [ ] Obtengo lista de 7 estándares
- [ ] Puedo listar criterios: `/api/normativity/criterios/`
- [ ] Obtengo lista de 32 criterios
- [ ] Filtro por estándar funciona: `?estandar=1`
- [ ] Endpoint mandatorios funciona: `/criterios/mandatorios/`
- [ ] Endpoint con_evidencia funciona: `/criterios/con_evidencia/`
- [ ] Badge de admin muestra colores: `/admin/normativity/criterio/`

---

_Guía práctica: 2026-03-11_
