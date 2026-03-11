# 🗺️ MAPA DE URLS - APP NORMATIVITY

## Estructura del Router

```
backend/urls.py
└── path('api/normativity/', include('normativity.urls'))
    └── normativity/urls.py
        └── DefaultRouter()
            ├── register('estandares', EstandarViewSet)
            ├── register('criterios', CriterioViewSet)
            └── register('documentos-normativos', DocumentoNormativoViewSet)
```

---

## Árbol de URLs Generadas Automáticamente

```
/api/normativity/
│
├── estandares/                              ✅ [GET] Listar
│   ├── 1/                                   ✅ [GET] Detalle
│   ├── 1/criterios/                         ✅ [GET] Acción: criterios de estándar
│   └── todos/                               ✅ [GET] Acción: todos con criterios
│
├── criterios/                               ✅ [GET] Listar
│   ├── 1/                                   ✅ [GET] Detalle
│   ├── mandatorios/                         ✅ [GET] Acción: criterios mandatorios
│   ├── con_evidencia/                       ✅ [GET] Acción: con evidencia
│   └── por_complejidad/                     ✅ [GET] Acción: por complejidad
│
└── documentos-normativos/                   ✅ [GET] Listar
    ├── 1/                                   ✅ [GET] Detalle
    └── 1/criterios/                         ✅ [GET] Acción: criterios relacionados

❌ criterio/                                 NO EXISTE (singular)
❌ estandar/                                 NO EXISTE (singular)
```

---

## Endpoints por ViewSet

### EstandarViewSet (ReadOnlyModelViewSet)

| Método | URL | Handler | Descripción |
|--------|-----|---------|-------------|
| GET | `/estandares/` | list | Listar todos |
| GET | `/estandares/<id>/` | retrieve | Obtener uno |
| GET | `/estandares/<id>/criterios/` | criterios (action) | Criterios de estándar |
| GET | `/estandares/todos/` | todos (action) | Todos con criterios |

**Filtros disponibles:**
- search_fields: `nombre`, `codigo`, `descripcion`
- filterset_fields: `codigo`, `estado`

---

### CriterioViewSet (ReadOnlyModelViewSet)

| Método | URL | Handler | Descripción |
|--------|-----|---------|-------------|
| GET | `/criterios/` | list | Listar todos |
| GET | `/criterios/<id>/` | retrieve | Obtener uno |
| GET | `/criterios/mandatorios/` | mandatorios (action) | Solo mandatorios |
| GET | `/criterios/con_evidencia/` | con_evidencia (action) | Con evidencia |
| GET | `/criterios/por_complejidad/` | por_complejidad (action) | Por complejidad |

**Filtros disponibles:**
- search_fields: `codigo`, `nombre`, `descripcion`
- filterset_fields: `estandar`, `complejidad`, `aplica_todos`, `es_mandatorio`
- ordering_fields: `codigo`, `nombre`, `complejidad`
- Orden por defecto: `codigo` ASC

**Parámetros de query:**
```
?estandar=1                    # ID del estándar
?complejidad=ALTA              # BAJA, MEDIA, ALTA
?aplica_todos=true             # true/false
?es_mandatorio=true            # true/false
?search=medicamentos           # Búsqueda por texto
?ordering=nombre               # Ordenar por campo
```

---

### DocumentoNormativoViewSet (ReadOnlyModelViewSet)

| Método | URL | Handler | Descripción |
|--------|-----|---------|-------------|
| GET | `/documentos-normativos/` | list | Listar todos |
| GET | `/documentos-normativos/<id>/` | retrieve | Obtener uno |
| GET | `/documentos-normativos/<id>/criterios/` | criterios (action) | Criterios relacionados |

**Filtros disponibles:**
- search_fields: `titulo`, `numero_referencia`, `descripcion`
- filterset_fields: `tipo`
- ordering_fields: `fecha_publicacion`, `titulo`
- Orden por defecto: `fecha_publicacion` DESC

---

## Ejemplos de URLs Completas

### Listar
```
✅ GET /api/normativity/estandares/
✅ GET /api/normativity/criterios/
✅ GET /api/normativity/documentos-normativos/
```

### Detalle
```
✅ GET /api/normativity/estandares/1/
✅ GET /api/normativity/criterios/5/
✅ GET /api/normativity/documentos-normativos/1/
```

### Con Filtros
```
✅ GET /api/normativity/criterios/?estandar=1
✅ GET /api/normativity/criterios/?complejidad=ALTA
✅ GET /api/normativity/criterios/?aplica_todos=true&es_mandatorio=true
✅ GET /api/normativity/criterios/?estandar=1&complejidad=MEDIA
✅ GET /api/normativity/documentos-normativos/?tipo=RESOLUCION
```

### Búsqueda
```
✅ GET /api/normativity/criterios/?search=medicamentos
✅ GET /api/normativity/estandares/?search=talento
✅ GET /api/normativity/documentos-normativos/?search=3100
```

### Acciones Custom
```
✅ GET /api/normativity/estandares/1/criterios/
✅ GET /api/normativity/estandares/todos/
✅ GET /api/normativity/criterios/mandatorios/
✅ GET /api/normativity/criterios/con_evidencia/
✅ GET /api/normativity/criterios/por_complejidad/?complejidad=ALTA
✅ GET /api/normativity/documentos-normativos/1/criterios/
```

### Pagination (si está habilitada)
```
✅ GET /api/normativity/criterios/?page=1&page_size=10
```

---

## Errores Comunes

### ❌ URL Incorrecto (Singular)
```
GET /api/normativity/criterio/        # 404 Not Found
GET /api/normativity/estandar/         # 404 Not Found
GET /api/normativity/documento/        # 404 Not Found
```

**Corrección:**
```
GET /api/normativity/criterios/        # ✅ Correcto
GET /api/normativity/estandares/       # ✅ Correcto
GET /api/normativity/documentos-normativos/  # ✅ Correcto
```

### ❌ Acción sin parámetro requerido
```
GET /api/normativity/criterios/por_complejidad/
# 400 Bad Request: Falta parámetro "complejidad"
```

**Corrección:**
```
GET /api/normativity/criterios/por_complejidad/?complejidad=ALTA
# ✅ 200 OK
```

### ❌ ID inválido
```
GET /api/normativity/criterios/99999/
# 404 Not Found: ID no existe
```

---

## Respuesta JSON Típica

### GET /api/normativity/criterios/

```json
[
  {
    "id": 1,
    "estandar": 1,
    "estandar_display": "Dotación, Medicamentos e Insumos",
    "codigo": "1.1",
    "nombre": "Medicamentos básicos",
    "descripcion": "La IPS debe contar con...",
    "complejidad": "MEDIA",
    "complejidad_display": "Media",
    "aplica_todos": true,
    "es_mandatorio": true,
    "requiere_evidencia_documental": false,
    "notas_interpretacion": "Notas...",
    "estado": true,
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_actualizacion": "2024-01-15T10:30:00Z"
  }
]
```

### GET /api/normativity/estandares/1/

```json
{
  "id": 1,
  "codigo": "DOT",
  "codigo_display": "Dotación, Medicamentos e Insumos",
  "nombre": "Dotación, Medicamentos e Insumos",
  "descripcion": "Los servicios de salud...",
  "estado": true,
  "version_resolucion": "3100/2019",
  "criterios": [
    {
      "id": 1,
      "codigo": "1.1",
      "nombre": "Medicamentos básicos",
      ...
    }
  ],
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_actualizacion": "2024-01-15T10:30:00Z"
}
```

---

## Matriz de Métodos HTTP

| ViewSet | LIST | CREATE | RETRIEVE | UPDATE | PATCH | DELETE |
|---------|------|--------|----------|--------|-------|--------|
| EstandarViewSet | ✅ GET | ❌ | ✅ GET | ❌ | ❌ | ❌ |
| CriterioViewSet | ✅ GET | ❌ | ✅ GET | ❌ | ❌ | ❌ |
| DocumentoNormativoViewSet | ✅ GET | ❌ | ✅ GET | ❌ | ❌ | ❌ |

**Nota:** Todos son ReadOnlyModelViewSet (solo lectura)

---

## Configuración del Router

```python
# normativity/urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'estandares', EstandarViewSet, basename='estandar')
router.register(r'criterios', CriterioViewSet, basename='criterio')
router.register(r'documentos-normativos', DocumentoNormativoViewSet, basename='documento-normativo')

urlpatterns = [
    path('', include(router.urls)),
]

# Genera automáticamente:
# - Listar: /estandares/, /criterios/, /documentos-normativos/
# - Detalle: /estandares/{id}/, /criterios/{id}/, /documentos-normativos/{id}/
# - Acciones: /estandares/{id}/{action_name}/, etc.
```

---

## 🎯 Regla de Oro para DRF

```python
router.register(r'nombre_plural', ViewSet)
# ↓ Genera automáticamente
/nombre_plural/           # Listar
/nombre_plural/<id>/      # Detalle
# NO genera
/nombre_singular/         # ❌ No existe
```

---

_Mapa de URLs: 2026-03-11_  
_Status: ✅ COMPLETO Y DOCUMENTADO_
