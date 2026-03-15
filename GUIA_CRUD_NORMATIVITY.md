# Guía CRUD - Normativity API

## Estado de la API

La API de Normativity ahora es **completamente funcional** con operaciones de lectura y escritura:

- **Lectura (GET)**: Acceso público, sin autenticación
- **Escritura (POST/PUT/DELETE)**: Requiere autenticación (token JWT)

---

## Endpoints Disponibles

### 1. ESTÁNDARES

#### Listar (GET)
```
GET /api/normativity/estandares/
GET /api/normativity/estandares/?codigo=TH&estado=true
```

**Filtros disponibles:**
- `codigo`: Código del estándar (TH, INF, DOT, PO, RS, GI, SA)
- `estado`: true/false
- `search`: Búsqueda en nombre, código, descripción

**Respuesta:**
```json
[
  {
    "id": 1,
    "codigo": "TH",
    "codigo_display": "Talento Humano",
    "nombre": "Gestión del Talento Humano",
    "estado": true,
    "criterios_count": 15
  }
]
```

#### Obtener uno (GET)
```
GET /api/normativity/estandares/{id}/
```

**Respuesta incluye criterios anidados:**
```json
{
  "id": 1,
  "codigo": "TH",
  "codigo_display": "Talento Humano",
  "nombre": "Gestión del Talento Humano",
  "descripcion": "...",
  "estado": true,
  "version_resolucion": "3100/2019",
  "criterios": [
    {
      "id": 10,
      "codigo": "1.1",
      "nombre": "Director o Gerente",
      ...
    }
  ]
}
```

#### Obtener todos (GET)
```
GET /api/normativity/estandares/todos/
```

**Respuesta:** Todos los estándares con criterios anidados

#### Crear (POST) - **Requiere autenticación**
```
POST /api/normativity/estandares/
Authorization: Bearer {token}

{
  "codigo": "TH",
  "nombre": "Talento Humano",
  "descripcion": "Estándar de gestión del talento humano",
  "estado": true,
  "version_resolucion": "3100/2019"
}
```

#### Actualizar (PUT/PATCH) - **Requiere autenticación**
```
PUT /api/normativity/estandares/{id}/
Authorization: Bearer {token}

{
  "nombre": "Talento Humano - Actualizado",
  "estado": false
}
```

#### Eliminar (DELETE) - **Requiere autenticación**
```
DELETE /api/normativity/estandares/{id}/
Authorization: Bearer {token}
```

---

### 2. CRITERIOS

#### Listar (GET)
```
GET /api/normativity/criterios/
GET /api/normativity/criterios/?estandar=1&complejidad=ALTA&es_mandatorio=true
```

**Filtros disponibles:**
- `estandar`: ID del estándar
- `complejidad`: BAJA, MEDIA, ALTA
- `aplica_todos`: true/false
- `es_mandatorio`: true/false
- `estado`: true/false
- `search`: Búsqueda en código, nombre, descripción
- `ordering`: codigo, nombre, -complejidad

**Respuesta:**
```json
[
  {
    "id": 10,
    "estandar": 1,
    "estandar_display": "Talento Humano",
    "codigo": "1.1",
    "nombre": "Director o Gerente",
    "complejidad": "ALTA",
    "complejidad_display": "Alta",
    "aplica_todos": true,
    "es_mandatorio": true,
    "requiere_evidencia_documental": true,
    "estado": true
  }
]
```

#### Obtener por complejidad (GET)
```
GET /api/normativity/criterios/por_complejidad/?complejidad=ALTA
```

#### Obtener mandatorios (GET)
```
GET /api/normativity/criterios/mandatorios/
```

#### Obtener con evidencia (GET)
```
GET /api/normativity/criterios/con_evidencia/
```

#### Crear (POST) - **Requiere autenticación**
```
POST /api/normativity/criterios/
Authorization: Bearer {token}

{
  "estandar": 1,
  "codigo": "1.5",
  "nombre": "Personal medico",
  "descripcion": "La IPS debe contar con...",
  "complejidad": "MEDIA",
  "aplica_todos": true,
  "es_mandatorio": true,
  "requiere_evidencia_documental": false,
  "estado": true
}
```

#### Actualizar (PUT/PATCH) - **Requiere autenticación**
```
PATCH /api/normativity/criterios/{id}/
Authorization: Bearer {token}

{
  "nombre": "Personal médico actualizado"
}
```

#### Eliminar (DELETE) - **Requiere autenticación**
```
DELETE /api/normativity/criterios/{id}/
Authorization: Bearer {token}
```

---

### 3. DOCUMENTOS NORMATIVOS

#### Listar (GET)
```
GET /api/normativity/documentos-normativos/
GET /api/normativity/documentos-normativos/?tipo=RESOLUCION
```

**Filtros disponibles:**
- `tipo`: RESOLUCION, ACUERDO, DECRETO, MANUAL, GUIA, CIRCULAR, OTRO
- `search`: Búsqueda en título, número, descripción
- `ordering`: fecha_publicacion, -titulo

**Respuesta:**
```json
[
  {
    "id": 1,
    "titulo": "Resolución 3100 de 2019",
    "tipo": "RESOLUCION",
    "tipo_display": "Resolución",
    "numero_referencia": "3100/2019",
    "fecha_publicacion": "2019-07-08",
    "url_documento": "https://...",
    "descripcion": "...",
    "criterios_relacionados": []
  }
]
```

#### Obtener uno (GET)
```
GET /api/normativity/documentos-normativos/{id}/
```

#### Obtener criterios del documento (GET)
```
GET /api/normativity/documentos-normativos/{id}/criterios/
```

#### Crear (POST) - **Requiere autenticación**
```
POST /api/normativity/documentos-normativos/
Authorization: Bearer {token}

{
  "titulo": "Manual de Evaluación",
  "tipo": "MANUAL",
  "numero_referencia": "MAN-001/2023",
  "fecha_publicacion": "2023-01-15",
  "url_documento": "https://ejemplo.com/manual.pdf",
  "descripcion": "Manual completo de evaluación",
  "criterios_relacionados_ids": [1, 2, 3, 4]
}
```

**Nota:** `criterios_relacionados_ids` es un array de IDs de criterios relacionados.

#### Actualizar (PUT/PATCH) - **Requiere autenticación**
```
PATCH /api/normativity/documentos-normativos/{id}/
Authorization: Bearer {token}

{
  "titulo": "Manual de Evaluación - v2",
  "criterios_relacionados_ids": [1, 2, 5, 6]
}
```

#### Eliminar (DELETE) - **Requiere autenticación**
```
DELETE /api/normativity/documentos-normativos/{id}/
Authorization: Bearer {token}
```

---

## Ejemplos con JavaScript/Fetch

### Listar estándares (sin autenticación)
```javascript
fetch('/api/normativity/estandares/')
  .then(res => res.json())
  .then(data => console.log(data));
```

### Crear estándar (con autenticación)
```javascript
fetch('/api/normativity/estandares/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    codigo: 'TH',
    nombre: 'Talento Humano',
    descripcion: 'Nuevo estándar',
    estado: true,
    version_resolucion: '3100/2019'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Crear documento normativo con criterios
```javascript
fetch('/api/normativity/documentos-normativos/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    titulo: 'Resolución ABC',
    tipo: 'RESOLUCION',
    numero_referencia: 'ABC/2024',
    fecha_publicacion: '2024-01-01',
    url_documento: 'https://...',
    descripcion: 'Descripción de la resolución',
    criterios_relacionados_ids: [1, 2, 3]
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Actualizar criterio
```javascript
fetch('/api/normativity/criterios/10/', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    nombre: 'Nombre actualizado',
    complejidad: 'ALTA'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Códigos de Respuesta HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado |
| 204 | No Content - Recurso eliminado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Requiere autenticación |
| 403 | Forbidden - Permiso denegado |
| 404 | Not Found - Recurso no existe |
| 500 | Server Error |

---

## Permisos y Autenticación

### Campo `permission_classes`
- **PublicReadOnly**: Permite GET sin autenticación, POST/PUT/DELETE con token JWT

### Obtener Token JWT
```bash
POST /api/auth/login/
{
  "username": "usuario",
  "password": "contraseña"
}

Respuesta:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usar Token en Requests
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Validaciones

### Estándar
- `codigo`: Debe ser único y estar en las opciones permitidas (TH, INF, DOT, PO, RS, GI, SA)
- `nombre`: Requerido, máx 255 caracteres
- `version_resolucion`: Por defecto "3100/2019"

### Criterio
- `estandar`: Requerido (FK a Estandar)
- `codigo`: Requerido, debe contener punto (ej: 1.1, 2.3)
- `nombre`: Requerido, máx 255 caracteres
- `complejidad`: BAJA, MEDIA o ALTA
- `estandar` + `codigo`: Combinación única

### Documento Normativo
- `titulo`: Requerido, máx 255 caracteres
- `tipo`: RESOLUCION, ACUERDO, DECRETO, MANUAL, GUIA, CIRCULAR, OTRO
- `fecha_publicacion`: Formato YYYY-MM-DD
- `url_documento`: Formato URL válido (opcional)

---

## Estado Actual

✅ Todos los endoints CRUD implementados
✅ Permisos configurados (lectura pública, escritura autenticada)
✅ Filtros y búsquedas disponibles
✅ Validaciones en todos los modelos
✅ Documentación completa
✅ Relaciones entre modelos funcionales

