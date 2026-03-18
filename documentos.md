# Documentación Frontend - Portal Web Backend

Fecha: 2026-02-20  
Versión: 3.0  
Aplicación: Portal Web Backend - Habilitación, Mejoras, Auditorías

---

## Tabla de Contenidos

### Parte I - Habilitación
1. [Introducción](#introducción)
2. [Arquitectura de Modelos](#arquitectura-de-modelos)
3. [Endpoints de API](#endpoints-de-api)
4. [Autenticación y Autorización](#autenticación-y-autorización)
5. [Flujos Principales](#flujos-principales)
6. [Estados y Enumeraciones](#estados-y-enumeraciones)
7. [Ejemplos de Requests/Responses](#ejemplos-de-requestsresponses)
8. [Pantallas Recomendadas](#pantallas-recomendadas)
9. [Relaciones entre Entidades](#relaciones-entre-entidades)

### Parte II - Mejoras (Planes de Mejora y Hallazgos)
10. [Módulo de Mejoras](#módulo-de-mejoras)
11. [Soportes / Archivos Adjuntos](#soportes--archivos-adjuntos)
12. [Integración Habilitación ↔ Mejoras](#integración-habilitación--mejoras)

### Parte III - Auditoría
13. [Módulo de Auditoría](#módulo-de-auditoría)
14. [Ciclo de Vida de Auditoría](#ciclo-de-vida-de-auditoría)
15. [Hallazgos de Auditoría](#hallazgos-de-auditoría)
16. [Actas y Programas](#actas-y-programas)

---

## Introducción

El módulo de **Habilitación** es el corazón del Portal Web Backend. Permite gestionar la habilitación de servicios de salud siguiendo la **Resolución 3100 de 2019** de Colombia.

### Conceptos Clave

- **DatosPrestador**: Información de habilitación de una Institución Prestadora de Servicios (IPS) o prestador individual
- **ServicioSede**: Servicios de salud específicos habilitados en una sede
- **Autoevaluación**: Evaluación periódica contra criterios de calidad
- **Cumplimiento**: Registro detallado de cumplimiento de un criterio específico
- **Criterio**: Requisito de la Resolución 3100 que debe cumplirse

### Base URL
```
http://localhost:8000/api/habilitacion/
```

---

## Arquitectura de Modelos

### 1. DatosPrestador

**Descripción**: Datos específicos de habilitación vinculados a una Headquarters (Sede). Es la información principal de cada prestador o IPS habilitada.

**Relaciones**:
- OneToOne → `Headquarters` (app companies)
- ForeignKey → `User` (usuario responsable)
- ForeignKey ← `Autoevaluacion` (múltiples)

**Campos Principales**:

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `headquarters` | FK(Headquarters) | Sí | Sede asociada (OneToOne) |
| `codigo_reps` | CharField(20) | Sí | Código REPS único de la Superintendencia |
| `clase_prestador` | Choice | Sí | IPS, PROF, PH, PJ |
| `estado_habilitacion` | Choice | No | Default: EN_PROCESO. Opciones: HABILITADA, EN_PROCESO, SUSPENDIDA, NO_HABILITADA, CANCELADA |
| `fecha_inscripcion` | DateField | No | Fecha de inscripción en REPS |
| `fecha_renovacion` | DateField | No | Fecha de última renovación |
| `fecha_vencimiento_habilitacion` | DateField | No | Cuándo expira la habilitación |
| `aseguradora_pep` | CharField(255) | No | Nombre de aseguradora responsabilidad civil |
| `numero_poliza` | CharField(50) | No | Número de póliza |
| `vigencia_poliza` | DateField | No | Hasta cuándo es válida la póliza |
| `usuario_responsable` | FK(User) | No | Asignado automáticamente en creación |
| `fecha_creacion` | DateTime | Auto | Cuándo se creó el registro |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

**Métodos Útiles**:
- `dias_para_vencimiento()`: Retorna días faltantes
- `esta_proxima_a_vencer(dias=90)`: Boolean si vence en X días
- `esta_vencida()`: Boolean si ya venció

**Tabla en BD**: `habilitacion_datosprestador`

---

### 2. ServicioSede

**Descripción**: Servicios de salud específicos habilitados en una sede. Un servicio es la combinación de modalidad + tipo en una sede.

**Relaciones**:
- ForeignKey → `Headquarters` (la sede)
- ForeignKey ← `Cumplimiento` (múltiples)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `sede` | FK(Headquarters) | Sí | Sede donde opera el servicio |
| `codigo_servicio` | CharField(20) | Sí | Código identificador del servicio |
| `nombre_servicio` | CharField(255) | Sí | Nombre del servicio |
| `descripcion` | TextField | No | Descripción del servicio |
| `modalidad` | Choice | Sí | INTRAMURAL, AMBULATORIA, TELEMEDICINA, URGENCIAS, AMBULANCIA |
| `complejidad` | Choice | Sí | BAJA, MEDIA, ALTA |
| `estado_habilitacion` | Choice | No | Default: EN_PROCESO. Opciones: HABILITADO, EN_PROCESO, SUSPENDIDO, NO_HABILITADO, CANCELADO |
| `fecha_habilitacion` | DateField | No | Fecha de habilitación |
| `fecha_vencimiento` | DateField | No | Vencimiento de la habilitación |
| `fecha_creacion` | DateTime | Auto | Creación del registro |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

**Tabla en BD**: `habilitacion_serviciosede`

---

### 3. Autoevaluación

**Descripción**: Evaluación periódica de un prestador contra los criterios de la Resolución 3100.

**Relaciones**:
- ForeignKey → `DatosPrestador`
- ForeignKey → `User` (usuario responsable)
- ForeignKey ← `Cumplimiento` (múltiples)
- ForeignKey ← `PlanMejora` (app mejoras, múltiples)
- ForeignKey ← `Hallazgo` (app mejoras, múltiples)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `datos_prestador` | FK(DatosPrestador) | Sí | Prestador evaluado |
| `periodo` | IntegerField | Sí | Año del periodo (2024-2028) |
| `numero_autoevaluacion` | CharField(50) | Auto | Generado automáticamente |
| `version` | Integer | No | Default: 1 |
| `fecha_inicio` | DateField | Auto | Fecha de creación |
| `fecha_completacion` | DateField | No | Fecha en que se completó |
| `fecha_vencimiento` | DateField | Sí | Fecha límite de la autoevaluación |
| `estado` | Choice | No | Default: BORRADOR. Opciones: BORRADOR, EN_CURSO, COMPLETADA, REVISADA, VALIDADA |
| `usuario_responsable` | FK(User) | No | Asignado automáticamente |
| `observaciones` | TextField | No | Notas u observaciones |
| `fecha_creacion` | DateTime | Auto | Creación del registro |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

**Métodos**:
- `porcentaje_cumplimiento`: Calcula el porcentaje de criterios cumplidos
- `vigente`: Si aún no ha vencido
- `total_cumplimientos`: Total de cumplimientos registrados

**Tabla en BD**: `habilitacion_autoevaluacion`

---

### 4. Cumplimiento

**Descripción**: Registro individual del cumplimiento de un criterio específico dentro de una autoevaluación.

**Relaciones**:
- ForeignKey → `Autoevaluacion`
- ForeignKey → `ServicioSede`
- ForeignKey → `Criterio` (app normativity)
- ForeignKey → `User` (responsable de mejora)
- ManyToMany → `Documento` (app main)
- ForeignKey ← `PlanMejora` (app mejoras, múltiples)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `autoevaluacion` | FK(Autoevaluacion) | Sí | Autoevaluación padre |
| `servicio_sede` | FK(ServicioSede) | Sí | Servicio evaluado |
| `criterio` | FK(Criterio) | Sí | Criterio de la norma |
| `cumple` | Choice | Sí | CUMPLE, NO_CUMPLE, PARCIALMENTE, NO_APLICA |
| `documentos_evidencia` | M2M(Documento) | No | Documentos de soporte |
| `hallazgo` | TextField | No | Texto de hallazgo (campo legacy) |
| `plan_mejora` | TextField | No | Texto plan de mejora (campo legacy) |
| `responsable_mejora` | FK(User) | No | Responsable de la mejora |
| `fecha_compromiso` | DateField | No | Fecha compromiso de mejora |
| `fecha_creacion` | DateTime | Auto | Creación del registro |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

**Tabla en BD**: `habilitacion_cumplimiento`

---

## Endpoints de API

### Base URLs

| Módulo | Base URL |
|--------|----------|
| Habilitación | `/api/habilitacion/` |
| Mejoras | `/api/mejoras/` |
| Auditoría | `/api/audit/` |
| Usuarios | `/api/users/` |

### 3.1 DatosPrestador

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/habilitacion/prestadores/` | Listar prestadores |
| POST | `/api/habilitacion/prestadores/` | Crear prestador |
| GET | `/api/habilitacion/prestadores/{id}/` | Detalle de prestador |
| PUT | `/api/habilitacion/prestadores/{id}/` | Actualizar prestador |
| PATCH | `/api/habilitacion/prestadores/{id}/` | Actualización parcial |
| DELETE | `/api/habilitacion/prestadores/{id}/` | Eliminar prestador |
| GET | `/api/habilitacion/prestadores/proximos_a_vencer/` | Próximos a vencer (90 días) |
| GET | `/api/habilitacion/prestadores/vencidas/` | Habilitaciones vencidas |
| GET | `/api/habilitacion/prestadores/{id}/servicios/` | Servicios del prestador |
| GET | `/api/habilitacion/prestadores/{id}/autoevaluaciones/` | Historial de autoevaluaciones |
| POST | `/api/habilitacion/prestadores/{id}/iniciar_renovacion/` | Iniciar proceso de renovación |

#### Campos de respuesta - Listado

```json
{
    "id": 1,
    "codigo_reps": "900077584-1",
    "company_name": "Clínica Integral de Salud",
    "clase_prestador": "IPS",
    "estado_habilitacion": "HABILITADA",
    "estado_display": "Habilitada",
    "fecha_vencimiento_habilitacion": "2025-12-31",
    "proxima_vencer": false,
    "dias_vencimiento": -51
}
```

#### Campos requeridos para crear

```json
{
    "headquarters_id": 1,
    "codigo_reps": "900077584-1",
    "clase_prestador": "IPS"
}
```

**Campos opcionales**: `estado_habilitacion`, `fecha_inscripcion`, `fecha_renovacion`, `fecha_vencimiento_habilitacion`, `aseguradora_pep`, `numero_poliza`, `vigencia_poliza`

#### Filtros disponibles

| Parámetro | Descripción |
|-----------|-------------|
| `?estado_habilitacion=HABILITADA` | Filtrar por estado |
| `?clase_prestador=IPS` | Filtrar por clase |
| `?search=clinica` | Buscar por nombre |

---

### 3.2 ServicioSede

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/habilitacion/servicios/` | Listar servicios |
| POST | `/api/habilitacion/servicios/` | Crear servicio |
| GET | `/api/habilitacion/servicios/{id}/` | Detalle de servicio |
| PUT | `/api/habilitacion/servicios/{id}/` | Actualizar servicio |
| PATCH | `/api/habilitacion/servicios/{id}/` | Actualización parcial |
| DELETE | `/api/habilitacion/servicios/{id}/` | Eliminar servicio |
| GET | `/api/habilitacion/servicios/proximos_a_vencer/` | Próximos a vencer |
| GET | `/api/habilitacion/servicios/por_complejidad/?complejidad=ALTA` | Filtrar por complejidad |
| GET | `/api/habilitacion/servicios/{id}/cumplimientos/` | Cumplimientos del servicio |

#### Campos requeridos para crear

```json
{
    "sede_id": 1,
    "codigo_servicio": "SVC001",
    "nombre_servicio": "Urgencias",
    "modalidad": "INTRAMURAL",
    "complejidad": "BAJA"
}
```

**Campos opcionales**: `descripcion`, `estado_habilitacion`, `fecha_habilitacion`, `fecha_vencimiento`

---

### 3.3 Autoevaluación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/habilitacion/autoevaluaciones/` | Listar autoevaluaciones |
| POST | `/api/habilitacion/autoevaluaciones/` | Crear autoevaluación |
| GET | `/api/habilitacion/autoevaluaciones/{id}/` | Detalle con cumplimientos |
| PUT | `/api/habilitacion/autoevaluaciones/{id}/` | Actualizar autoevaluación |
| PATCH | `/api/habilitacion/autoevaluaciones/{id}/` | Actualización parcial |
| DELETE | `/api/habilitacion/autoevaluaciones/{id}/` | Eliminar autoevaluación |
| GET | `/api/habilitacion/autoevaluaciones/por_completar/` | En BORRADOR o EN_CURSO |
| GET | `/api/habilitacion/autoevaluaciones/{id}/resumen/` | Resumen estadístico |
| POST | `/api/habilitacion/autoevaluaciones/{id}/validar/` | Cambiar estado a VALIDADA |
| POST | `/api/habilitacion/autoevaluaciones/{id}/duplicar/` | Crear nueva versión |

#### Campos de respuesta - Listado

```json
{
    "id": 1,
    "numero_autoevaluacion": "AE-2026-001",
    "prestador_codigo": "900077584-1",
    "periodo": 2026,
    "version": 1,
    "estado": "BORRADOR",
    "estado_display": "Borrador",
    "fecha_inicio": "2026-02-20",
    "fecha_completacion": null,
    "porcentaje_cumplimiento": 0.0
}
```

#### Campos de respuesta - Detalle

```json
{
    "id": 1,
    "numero_autoevaluacion": "AE-2026-001",
    "datos_prestador_detail": {
        "id": 1,
        "codigo_reps": "900077584-1",
        "company_name": "Clínica Integral"
    },
    "periodo": 2026,
    "version": 1,
    "estado": "BORRADOR",
    "estado_display": "Borrador",
    "fecha_inicio": "2026-02-20",
    "fecha_vencimiento": "2026-12-31",
    "porcentaje_cumplimiento": 75.0,
    "vigente": true,
    "total_cumplimientos": 20,
    "planes_mejora_count": 3,
    "hallazgos_count": 5,
    "mejoras_resumen": {
        "total_planes": 3,
        "planes_pendientes": 1,
        "planes_en_curso": 1,
        "planes_completados": 1,
        "total_hallazgos": 5,
        "hallazgos_abiertos": 2,
        "hallazgos_cerrados": 3
    },
    "cumplimientos_data": [...]
}
```

#### Campos requeridos para crear

```json
{
    "datos_prestador_id": 1,
    "periodo": 2026,
    "version": 1,
    "fecha_vencimiento": "2026-12-31"
}
```

**Campos opcionales**: `estado`, `fecha_completacion`, `observaciones`

> **Nota**: `version` es requerido por la restricción `unique_together(datos_prestador, periodo, version)`. Default: `1`.

---

### 3.4 Cumplimiento

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/habilitacion/cumplimientos/` | Listar cumplimientos |
| POST | `/api/habilitacion/cumplimientos/` | Crear cumplimiento |
| GET | `/api/habilitacion/cumplimientos/{id}/` | Detalle de cumplimiento |
| PUT | `/api/habilitacion/cumplimientos/{id}/` | Actualizar cumplimiento |
| PATCH | `/api/habilitacion/cumplimientos/{id}/` | Actualización parcial |
| DELETE | `/api/habilitacion/cumplimientos/{id}/` | Eliminar cumplimiento |
| GET | `/api/habilitacion/cumplimientos/sin_cumplir/` | Items con cumple=NO_CUMPLE |
| GET | `/api/habilitacion/cumplimientos/con_plan_mejora/` | Items con plan de mejora |
| GET | `/api/habilitacion/cumplimientos/mejoras_vencidas/` | Mejoras vencidas |

#### Campos de respuesta - Listado

```json
{
    "id": 1,
    "criterio_codigo": "C-1.1",
    "criterio_nombre": "Talento humano",
    "servicio_nombre": "Urgencias",
    "cumple": "CUMPLE",
    "cumple_display": "Cumple",
    "tiene_plan_mejora": false,
    "planes_mejora_count": 0,
    "hallazgos_count": 0,
    "fecha_compromiso": null
}
```

#### Campos requeridos para crear

```json
{
    "autoevaluacion_id": 1,
    "servicio_sede_id": 1,
    "criterio_id": 1,
    "cumple": "NO_CUMPLE"
}
```

**Campos opcionales**: `hallazgo`, `plan_mejora`, `responsable_mejora`, `fecha_compromiso`, `documentos_evidencia`

#### Filtros disponibles

| Parámetro | Descripción |
|-----------|-------------|
| `?autoevaluacion=1` | Filtrar por autoevaluación |
| `?cumple=NO_CUMPLE` | Filtrar por estado de cumplimiento |
| `?servicio_sede=1` | Filtrar por servicio |
| `?criterio=1` | Filtrar por criterio |

---

## Autenticación y Autorización

### JWT (JSON Web Token)

El sistema usa **SimpleJWT** para autenticación.

#### Login

```
POST /api/users/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "admin"
}
```

**Respuesta**:
```json
{
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    }
}
```

#### Usar el Token

Incluir en **TODOS** los requests (excepto login):

```
Authorization: Bearer eyJ...
```

#### Refresh Token

```
POST /api/users/token/refresh/
{
    "refresh": "eyJ..."
}
```

---

## Flujos Principales

### Flujo 1: Registro de un Nuevo Prestador

```
1. POST /api/habilitacion/prestadores/
   Body: { "headquarters_id": 1, "codigo_reps": "900XXXXX", "clase_prestador": "IPS" }

2. POST /api/habilitacion/servicios/
   Body: { "sede_id": 1, "codigo_servicio": "SVC001", "nombre_servicio": "Urgencias",
           "modalidad": "INTRAMURAL", "complejidad": "BAJA" }

3. POST /api/habilitacion/autoevaluaciones/
   Body: { "datos_prestador_id": 1, "periodo": 2026, "fecha_vencimiento": "2026-12-31" }

4. POST /api/habilitacion/cumplimientos/
   Body: { "autoevaluacion_id": 1, "servicio_sede_id": 1, "criterio_id": 1, "cumple": "CUMPLE" }
```

### Flujo 2: Evaluación de Cumplimiento

```
1. GET /api/habilitacion/autoevaluaciones/{id}/
   → Obtener autoevaluación con listado de cumplimientos

2. PATCH /api/habilitacion/cumplimientos/{id}/
   Body: { "cumple": "NO_CUMPLE" }

3. Si NO_CUMPLE → Crear plan de mejora (ver Parte II)

4. PATCH /api/habilitacion/autoevaluaciones/{id}/
   Body: { "estado": "COMPLETADA" }
```

### Flujo 3: Renovación de Habilitación

```
1. POST /api/habilitacion/prestadores/{id}/iniciar_renovacion/
   → Inicia proceso con nueva autoevaluación

2. GET /api/habilitacion/autoevaluaciones/{id}/resumen/
   → Verificar porcentaje de cumplimiento

3. POST /api/habilitacion/autoevaluaciones/{id}/validar/
   → Marcar como validada
```

### Flujo 4: Monitoreo y Seguimiento

```
1. GET /api/habilitacion/prestadores/proximos_a_vencer/
   → Prestadores con habilitación próxima a vencer (90 días)

2. GET /api/habilitacion/prestadores/vencidas/
   → Habilitaciones ya vencidas

3. GET /api/habilitacion/servicios/proximos_a_vencer/
   → Servicios por vencer

4. GET /api/habilitacion/cumplimientos/sin_cumplir/
   → Items que no cumplen

5. GET /api/habilitacion/cumplimientos/mejoras_vencidas/
   → Mejoras con fecha vencida
```

---

## Estados y Enumeraciones

### DatosPrestador.estado_habilitacion

| Valor | Display | Descripción |
|-------|---------|-------------|
| `HABILITADA` | Habilitada | Habilitación vigente |
| `EN_PROCESO` | En Proceso | En trámite (default) |
| `SUSPENDIDA` | Suspendida | Temporalmente suspendida |
| `NO_HABILITADA` | No Habilitada | No cumple requisitos |
| `CANCELADA` | Cancelada | Habilitación cancelada |

### DatosPrestador.clase_prestador

| Valor | Display |
|-------|---------|
| `IPS` | IPS |
| `PROF` | Profesional Independiente |
| `PH` | Persona Natural |
| `PJ` | Persona Jurídica |

### ServicioSede.modalidad

| Valor | Display |
|-------|---------|
| `INTRAMURAL` | Intramural |
| `AMBULATORIA` | Ambulatoria |
| `TELEMEDICINA` | Telemedicina |
| `URGENCIAS` | Urgencias |
| `AMBULANCIA` | Ambulancia |

### ServicioSede.complejidad

| Valor | Display |
|-------|---------|
| `BAJA` | Baja |
| `MEDIA` | Media |
| `ALTA` | Alta |

### Autoevaluacion.estado

| Valor | Display | Descripción |
|-------|---------|-------------|
| `BORRADOR` | Borrador | Recién creada (default) |
| `EN_CURSO` | En Curso | Evaluación en progreso |
| `COMPLETADA` | Completada | Todos los criterios evaluados |
| `REVISADA` | Revisada | Revisada por supervisor |
| `VALIDADA` | Validada | Aprobada oficialmente |

### Cumplimiento.cumple

| Valor | Display |
|-------|---------|
| `CUMPLE` | Cumple |
| `NO_CUMPLE` | No Cumple |
| `PARCIALMENTE` | Parcialmente |
| `NO_APLICA` | No Aplica |

---

## Ejemplos de Requests/Responses

### Crear Prestador completo

```http
POST /api/habilitacion/prestadores/
Authorization: Bearer eyJ...
Content-Type: application/json

{
    "headquarters_id": 1,
    "codigo_reps": "900077584-1",
    "clase_prestador": "IPS",
    "estado_habilitacion": "HABILITADA",
    "fecha_inscripcion": "2024-01-15",
    "fecha_vencimiento_habilitacion": "2026-12-31",
    "aseguradora_pep": "Seguros Bolívar",
    "numero_poliza": "POL-2024-001",
    "vigencia_poliza": "2026-12-31"
}
```

**Respuesta (201 Created)**:
```json
{
    "id": 1,
    "headquarters_id": 1,
    "codigo_reps": "900077584-1",
    "clase_prestador": "IPS",
    "estado_habilitacion": "HABILITADA",
    "estado_display": "Habilitada",
    "fecha_inscripcion": "2024-01-15",
    "fecha_renovacion": null,
    "fecha_vencimiento_habilitacion": "2026-12-31",
    "aseguradora_pep": "Seguros Bolívar",
    "numero_poliza": "POL-2024-001",
    "vigencia_poliza": "2026-12-31",
    "proxima_vencer": false,
    "dias_vencimiento": 314,
    "usuario_responsable": 1,
    "fecha_creacion": "2026-02-20T10:00:00Z",
    "fecha_actualizacion": "2026-02-20T10:00:00Z"
}
```

### Crear Servicio

```http
POST /api/habilitacion/servicios/
Authorization: Bearer eyJ...
Content-Type: application/json

{
    "sede_id": 1,
    "codigo_servicio": "URG-001",
    "nombre_servicio": "Urgencias",
    "descripcion": "Servicio de urgencias 24 horas",
    "modalidad": "URGENCIAS",
    "complejidad": "ALTA"
}
```

### Crear Autoevaluación

```http
POST /api/habilitacion/autoevaluaciones/
Authorization: Bearer eyJ...
Content-Type: application/json

{
    "datos_prestador_id": 1,
    "periodo": 2026,
    "fecha_vencimiento": "2026-12-31",
    "observaciones": "Autoevaluación anual 2026"
}
```

### Crear Cumplimiento

```http
POST /api/habilitacion/cumplimientos/
Authorization: Bearer eyJ...
Content-Type: application/json

{
    "autoevaluacion_id": 1,
    "servicio_sede_id": 1,
    "criterio_id": 1,
    "cumple": "NO_CUMPLE",
    "hallazgo": "No se encontraron registros de capacitación",
    "fecha_compromiso": "2026-06-30"
}
```

---

## Pantallas Recomendadas

### Dashboard de Habilitación
- Resumen de prestadores por estado
- Alertas de vencimiento (usar `/prestadores/proximos_a_vencer/`)
- Servicios por complejidad (usar `/servicios/por_complejidad/`)

### Gestión de Prestador
- Lista de prestadores con filtros por estado y clase
- Formulario de registro/edición
- Detalle con servicios y autoevaluaciones anidados

### Autoevaluación
- Lista de autoevaluaciones con porcentaje de cumplimiento
- Vista de evaluación por criterio
- Resumen estadístico (usar `/{id}/resumen/`)

### Cumplimientos
- Grid editable de cumplimiento por criterio
- Filtros por estado de cumplimiento
- Vinculación con planes de mejora

---

## Relaciones entre Entidades

### Diagrama de Relaciones

```
Headquarters ──1:1──→ DatosPrestador
     │                     │
     │                     │ 1:N
     │                     ↓
     │              Autoevaluación ←──── PlanMejora (app mejoras)
     │                     │   ↑              ↑
     │                     │   │              │
     ↓                     ↓   │              │
ServicioSede ───→ Cumplimiento ──────→ Hallazgo (app mejoras)
                       │
                       ↓
                   Criterio (app normativity)
```

### Reglas de integridad
- Un `DatosPrestador` siempre requiere una `Headquarters` existente
- Un `ServicioSede` siempre requiere una `Headquarters` (sede) existente
- Un `Cumplimiento` requiere: `Autoevaluacion`, `ServicioSede` y `Criterio` existentes
- Eliminar un prestador con autoevaluaciones genera error (PROTECT)

---

## Paginación

Todas las listas usan paginación automática:

```json
{
    "count": 150,
    "next": "http://localhost:8000/api/habilitacion/prestadores/?page=2",
    "previous": null,
    "results": [...]
}
```

- Default: 20 items por página
- Usar `?page=2` para navegar
- Usar `?page_size=50` para cambiar tamaño (máximo 100)

---

## Manejo de Errores

### Códigos HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 201 | Creado exitosamente |
| 204 | Eliminado (sin contenido) |
| 400 | Error de validación |
| 401 | No autenticado |
| 403 | Sin permisos |
| 404 | No encontrado |
| 500 | Error del servidor |

### Formato de errores de validación

```json
{
    "campo": ["Mensaje de error"],
    "otro_campo": ["Este campo es requerido."]
}
```

---

# Parte II - Módulo de Mejoras

## Módulo de Mejoras

El módulo de **Mejoras** (`mejoras/`) es un módulo transversal que permite gestionar planes de mejora y hallazgos provenientes de habilitación, auditoría o indicadores.

### Base URL
```
http://localhost:8000/api/mejoras/
```

### 10.1 PlanMejora

**Descripción**: Plan de mejora originado desde habilitación, auditoría o indicadores.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `numero_plan` | CharField(50) | Sí | Número único del plan |
| `descripcion` | TextField | Sí | Descripción del plan |
| `origen_tipo` | Choice | Sí | HABILITACION, AUDITORIA, INDICADOR |
| `cumplimiento` | FK(Cumplimiento) | No | Cumplimiento asociado (origen habilitación) |
| `autoevaluacion` | FK(Autoevaluacion) | Condicional | Requerido si origen_tipo=HABILITACION |
| `criterio` | FK(Criterio) | No | Criterio de la norma |
| `auditoria` | FK(Auditoria) | Condicional | Requerido si origen_tipo=AUDITORIA |
| `resultado_indicador` | FK(Result) | Condicional | Requerido si origen_tipo=INDICADOR |
| `estado_cumplimiento_actual` | CharField(100) | No | Estado actual del cumplimiento |
| `objetivo_mejorado` | TextField | No | Objetivo mejorado |
| `acciones_implementar` | TextField | Sí | Acciones a implementar |
| `responsable` | FK(User) | No | Usuario responsable |
| `fecha_inicio` | DateField | Sí | Fecha de inicio del plan |
| `fecha_vencimiento` | DateField | Sí | Fecha límite del plan |
| `fecha_implementacion` | DateField | No | Fecha real de implementación |
| `porcentaje_avance` | Integer | No | 0-100, default: 0 |
| `estado` | Choice | No | Default: PENDIENTE |
| `evidencia` | TextField | No | Texto de evidencia |
| `observaciones` | TextField | No | Notas adicionales |
| `fecha_creacion` | DateTime | Auto | Creación |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

**Propiedades calculadas**:
- `esta_vencido`: Boolean, si fecha_vencimiento pasó y no está completado
- `dias_restantes`: Días hasta el vencimiento (negativo si ya venció)
- `proximo_a_vencer`: Boolean, si vence en los próximos 30 días
- `origen_detalle`: Texto descriptivo del origen

#### Endpoints PlanMejora

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/mejoras/planes-mejora/` | Listar planes |
| POST | `/api/mejoras/planes-mejora/` | Crear plan |
| GET | `/api/mejoras/planes-mejora/{id}/` | Detalle del plan (incluye hallazgos y soportes) |
| PUT | `/api/mejoras/planes-mejora/{id}/` | Actualizar plan |
| PATCH | `/api/mejoras/planes-mejora/{id}/` | Actualización parcial |
| DELETE | `/api/mejoras/planes-mejora/{id}/` | Eliminar plan |
| GET | `/api/mejoras/planes-mejora/vencidos/` | Planes vencidos |
| GET | `/api/mejoras/planes-mejora/proximos-vencer/` | Próximos a vencer (30 días) |
| GET | `/api/mejoras/planes-mejora/proximos-vencer/?dias=15` | Próximos a vencer (N días) |
| GET | `/api/mejoras/planes-mejora/resumen/` | Resumen estadístico |
| GET | `/api/mejoras/planes-mejora/por-origen/` | Agrupado por origen |

#### Campos de respuesta - Listado

```json
{
    "id": 1,
    "numero_plan": "PM-HAB-001",
    "descripcion": "Plan de mejora para talento humano",
    "origen_tipo": "HABILITACION",
    "origen_tipo_display": "Habilitación",
    "criterio_id": 5,
    "criterio_codigo": "C-1.1",
    "criterio_nombre": "Talento humano",
    "autoevaluacion_id": 1,
    "autoevaluacion_numero": "AE-2026-001",
    "auditoria_id": null,
    "auditoria_nombre": "",
    "cumplimiento_id": 10,
    "resultado_indicador_id": null,
    "estado_cumplimiento_actual": "",
    "objetivo_mejorado": "",
    "acciones_implementar": "Capacitación al personal",
    "responsable": 1,
    "responsable_nombre": "Admin User",
    "fecha_inicio": "2026-02-20",
    "fecha_vencimiento": "2026-06-20",
    "fecha_implementacion": null,
    "porcentaje_avance": 0,
    "estado": "PENDIENTE",
    "estado_display": "Pendiente",
    "evidencia": "",
    "observaciones": "",
    "esta_vencido": false,
    "dias_restantes": 120,
    "proximo_a_vencer": false,
    "hallazgos_count": 2,
    "soportes_count": 1,
    "fecha_creacion": "2026-02-20T10:00:00Z",
    "fecha_actualizacion": "2026-02-20T10:00:00Z"
}
```

#### Campos de respuesta - Detalle (adicionales)

El detalle incluye todos los campos del listado más:

```json
{
    "...campos del listado...",
    "hallazgos": [
        {
            "id": 1,
            "numero_hallazgo": "H-001",
            "tipo": "NO_CONFORMIDAD",
            "severidad": "ALTA",
            "estado": "ABIERTO",
            "descripcion": "..."
        }
    ],
    "soportes": [
        {
            "id": 1,
            "archivo": "/media/SoportesPlanes/archivo.pdf",
            "nombre_original": "evidencia.pdf",
            "tipo_soporte": "EVIDENCIA",
            "tipo_soporte_display": "Evidencia",
            "extension": "pdf",
            "tamano_legible": "1.2 MB",
            "subido_por_nombre": "Admin"
        }
    ],
    "soportes_count": 1,
    "origen_detalle": "Habilitación - AE-2026-001"
}
```

#### Campos requeridos para crear

```json
{
    "numero_plan": "PM-HAB-001",
    "descripcion": "Plan de mejora para talento humano",
    "origen_tipo": "HABILITACION",
    "acciones_implementar": "Capacitación al personal de enfermería",
    "fecha_inicio": "2026-02-20",
    "fecha_vencimiento": "2026-06-20",
    "autoevaluacion": 1
}
```

> **Nota**: La FK de origen es condicional según `origen_tipo`:
> - `HABILITACION` → requiere `autoevaluacion`
> - `AUDITORIA` → requiere `auditoria`
> - `INDICADOR` → requiere `resultado_indicador`

**Campos opcionales**: `cumplimiento`, `criterio`, `estado_cumplimiento_actual`, `objetivo_mejorado`, `responsable`, `fecha_implementacion`, `porcentaje_avance`, `estado`, `evidencia`, `observaciones`

#### Respuesta de Resumen

```
GET /api/mejoras/planes-mejora/resumen/
GET /api/mejoras/planes-mejora/resumen/?origen_tipo=HABILITACION
GET /api/mejoras/planes-mejora/resumen/?autoevaluacion=1
```

```json
{
    "total_planes": 10,
    "pendientes": 3,
    "en_curso": 4,
    "completados": 2,
    "vencidos": 1,
    "porcentaje_promedio_avance": 45.5
}
```

#### Respuesta de Por-Origen

```
GET /api/mejoras/planes-mejora/por-origen/
```

```json
[
    {
        "origen_tipo": "HABILITACION",
        "total": 5,
        "pendientes": 2,
        "en_curso": 2,
        "completados": 1,
        "vencidos": 0
    },
    {
        "origen_tipo": "AUDITORIA",
        "total": 3,
        "pendientes": 1,
        "en_curso": 1,
        "completados": 1,
        "vencidos": 0
    }
]
```

#### Filtros disponibles PlanMejora

| Parámetro | Valores | Descripción |
|-----------|---------|-------------|
| `?origen_tipo=` | HABILITACION, AUDITORIA, INDICADOR | Filtrar por origen |
| `?estado=` | PENDIENTE, EN_CURSO, COMPLETADO, VENCIDO | Filtrar por estado |
| `?autoevaluacion=` | ID | Planes de una autoevaluación |
| `?auditoria=` | ID | Planes de una auditoría |
| `?criterio=` | ID | Planes de un criterio |
| `?responsable=` | ID | Planes de un usuario |
| `?cumplimiento=` | ID | Planes de un cumplimiento |
| `?resultado_indicador=` | ID | Planes de un indicador |
| `?search=` | texto | Buscar en numero_plan, descripcion, acciones |
| `?ordering=` | fecha_vencimiento, porcentaje_avance, etc. | Ordenar resultados |

#### Validaciones de negocio

- `fecha_vencimiento` debe ser posterior a `fecha_inicio`
- Para `estado=COMPLETADO`, `porcentaje_avance` debe ser 100
- La FK de origen debe corresponder al `origen_tipo` seleccionado

---

### 10.2 Hallazgo

**Descripción**: Hallazgo identificado desde habilitación, auditoría o indicadores. Puede vincularse a un plan de mejora.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `numero_hallazgo` | CharField(50) | Sí | Número único del hallazgo |
| `descripcion` | TextField | Sí | Descripción del hallazgo |
| `tipo` | Choice | Sí | FORTALEZA, OPORTUNIDAD_MEJORA, NO_CONFORMIDAD, HALLAZGO |
| `severidad` | Choice | Sí | BAJA, MEDIA, ALTA, CRÍTICA |
| `origen_tipo` | Choice | Sí | HABILITACION, AUDITORIA, INDICADOR |
| `autoevaluacion` | FK(Autoevaluacion) | Condicional | Requerido si origen_tipo=HABILITACION |
| `datos_prestador` | FK(DatosPrestador) | No | Prestador relacionado |
| `criterio` | FK(Criterio) | No | Criterio de la norma |
| `auditoria` | FK(Auditoria) | Condicional | Requerido si origen_tipo=AUDITORIA |
| `resultado_indicador` | FK(Result) | Condicional | Requerido si origen_tipo=INDICADOR |
| `plan_mejora` | FK(PlanMejora) | No | Plan de mejora vinculado |
| `area_responsable` | CharField(200) | No | Área responsable |
| `estado` | Choice | No | Default: ABIERTO |
| `fecha_identificacion` | DateField | Sí | Fecha cuando se identificó |
| `fecha_cierre` | DateField | No | Requerido para estado=CERRADO |
| `observaciones` | TextField | No | Notas adicionales |
| `fecha_creacion` | DateTime | Auto | Creación |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

> **Importante**: El campo `severidad` usa `CRÍTICA` (con tilde) como valor almacenado en BD. Al filtrar use: `?severidad=CRÍTICA`

#### Endpoints Hallazgo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/mejoras/hallazgos/` | Listar hallazgos |
| POST | `/api/mejoras/hallazgos/` | Crear hallazgo |
| GET | `/api/mejoras/hallazgos/{id}/` | Detalle del hallazgo |
| PUT | `/api/mejoras/hallazgos/{id}/` | Actualizar hallazgo |
| PATCH | `/api/mejoras/hallazgos/{id}/` | Actualización parcial |
| DELETE | `/api/mejoras/hallazgos/{id}/` | Eliminar hallazgo |
| GET | `/api/mejoras/hallazgos/estadisticas/` | Estadísticas de hallazgos |
| GET | `/api/mejoras/hallazgos/por-origen/` | Agrupado por origen |
| GET | `/api/mejoras/hallazgos/sin-plan/` | Hallazgos sin plan de mejora |

#### Campos de respuesta - Listado

```json
{
    "id": 1,
    "numero_hallazgo": "H-HAB-001",
    "descripcion": "Falta capacitación en protocolos",
    "tipo": "NO_CONFORMIDAD",
    "tipo_display": "No Conformidad",
    "severidad": "ALTA",
    "severidad_display": "Alta",
    "estado": "ABIERTO",
    "estado_display": "Abierto",
    "origen_tipo": "HABILITACION",
    "origen_tipo_display": "Habilitación",
    "area_responsable": "",
    "autoevaluacion_id": 1,
    "autoevaluacion_numero": "AE-2026-001",
    "datos_prestador_id": null,
    "auditoria_id": null,
    "auditoria_nombre": "",
    "resultado_indicador_id": null,
    "criterio_id": 5,
    "criterio_codigo": "C-1.1",
    "criterio_nombre": "Talento humano",
    "plan_mejora_id": 1,
    "plan_mejora_numero": "PM-HAB-001",
    "fecha_identificacion": "2026-02-20",
    "fecha_cierre": null,
    "observaciones": "",
    "fecha_creacion": "2026-02-20T10:00:00Z",
    "fecha_actualizacion": "2026-02-20T10:00:00Z"
}
```

#### Campos de respuesta - Detalle (adicionales)

```json
{
    "...campos del listado...",
    "origen_detalle": "Habilitación - AE-2026-001",
    "plan_mejora_detalle": {
        "id": 1,
        "numero_plan": "PM-HAB-001",
        "estado": "EN_CURSO",
        "porcentaje_avance": 50,
        "fecha_vencimiento": "2026-06-20"
    }
}
```

#### Campos requeridos para crear

```json
{
    "numero_hallazgo": "H-HAB-001",
    "descripcion": "Falta capacitación en protocolos",
    "tipo": "NO_CONFORMIDAD",
    "severidad": "ALTA",
    "origen_tipo": "HABILITACION",
    "fecha_identificacion": "2026-02-20",
    "autoevaluacion": 1
}
```

> **Nota**: Similar a PlanMejora, la FK de origen es condicional según `origen_tipo`.

**Campos opcionales**: `datos_prestador`, `criterio`, `plan_mejora`, `area_responsable`, `estado`, `fecha_cierre`, `observaciones`

#### Respuesta de Estadísticas

```
GET /api/mejoras/hallazgos/estadisticas/
GET /api/mejoras/hallazgos/estadisticas/?origen_tipo=HABILITACION
```

```json
{
    "total_hallazgos": 15,
    "fortalezas": 3,
    "oportunidades_mejora": 5,
    "no_conformidades": 6,
    "hallazgos": 1,
    "abiertos": 8,
    "en_seguimiento": 4,
    "cerrados": 3,
    "criticos": 2
}
```

#### Respuesta de Por-Origen

```json
[
    {
        "origen_tipo": "HABILITACION",
        "total": 10,
        "abiertos": 5,
        "en_seguimiento": 3,
        "cerrados": 2,
        "criticos": 1
    }
]
```

#### Filtros disponibles Hallazgo

| Parámetro | Valores | Descripción |
|-----------|---------|-------------|
| `?origen_tipo=` | HABILITACION, AUDITORIA, INDICADOR | Filtrar por origen |
| `?tipo=` | FORTALEZA, OPORTUNIDAD_MEJORA, NO_CONFORMIDAD, HALLAZGO | Filtrar por tipo |
| `?severidad=` | BAJA, MEDIA, ALTA, CRÍTICA | Filtrar por severidad |
| `?estado=` | ABIERTO, EN_SEGUIMIENTO, CERRADO | Filtrar por estado |
| `?autoevaluacion=` | ID | Hallazgos de una autoevaluación |
| `?auditoria=` | ID | Hallazgos de una auditoría |
| `?plan_mejora=` | ID | Hallazgos de un plan |
| `?criterio=` | ID | Hallazgos de un criterio |
| `?search=` | texto | Buscar en numero_hallazgo, descripcion, area_responsable |

---

## Soportes / Archivos Adjuntos

### 11.1 SoportePlan

**Descripción**: Archivos adjuntos vinculados a un plan de mejora. Se almacenan en `media/SoportesPlanes/`.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `plan_mejora` | FK(PlanMejora) | Sí | Plan de mejora padre |
| `archivo` | FileField | Sí | Archivo subido |
| `nombre_original` | CharField(255) | Auto | Nombre original del archivo |
| `tipo_soporte` | Choice | No | Default: EVIDENCIA |
| `descripcion` | CharField(500) | No | Descripción del soporte |
| `tamano_bytes` | BigInteger | Auto | Tamaño en bytes |
| `subido_por` | FK(User) | Auto | Usuario que subió el archivo |
| `fecha_subida` | DateTime | Auto | Fecha de subida |

#### Tipos de Soporte

| Valor | Display |
|-------|---------|
| `EVIDENCIA` | Evidencia |
| `ACTA` | Acta |
| `INFORME` | Informe |
| `FOTOGRAFIA` | Fotografía |
| `PLAN_ACCION` | Plan de Acción |
| `OTRO` | Otro |

#### Extensiones permitidas

PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, JPEG

Tamaño máximo: **10 MB**

#### Endpoints de Soportes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/mejoras/planes-mejora/{id}/soportes/` | Listar soportes del plan |
| POST | `/api/mejoras/planes-mejora/{id}/soportes/` | Subir soporte (multipart/form-data) |
| DELETE | `/api/mejoras/planes-mejora/{id}/soportes/{soporte_id}/` | Eliminar soporte |

#### Subir archivo

```http
POST /api/mejoras/planes-mejora/1/soportes/
Authorization: Bearer eyJ...
Content-Type: multipart/form-data

archivo: [archivo binario]
tipo_soporte: EVIDENCIA
descripcion: Fotografía de capacitación
```

**Respuesta (201 Created)**:
```json
{
    "id": 1,
    "plan_mejora": 1,
    "archivo": "/media/SoportesPlanes/uuid_evidencia.pdf",
    "nombre_original": "evidencia.pdf",
    "tipo_soporte": "EVIDENCIA",
    "tipo_soporte_display": "Evidencia",
    "descripcion": "Fotografía de capacitación",
    "tamano_bytes": 1258291,
    "tamano_legible": "1.2 MB",
    "extension": "pdf",
    "subido_por": 1,
    "subido_por_nombre": "Admin User",
    "fecha_subida": "2026-02-20T10:00:00Z"
}
```

#### Eliminar soporte

```http
DELETE /api/mejoras/planes-mejora/1/soportes/5/
Authorization: Bearer eyJ...
```

**Respuesta**: `204 No Content`

> El archivo físico se elimina del servidor junto con el registro.

---

## Integración Habilitación ↔ Mejoras

### Campos de Integración en Autoevaluación

El serializer de detalle de Autoevaluación incluye campos calculados desde el módulo de mejoras:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `planes_mejora_count` | Integer | Total de planes de mejora vinculados |
| `hallazgos_count` | Integer | Total de hallazgos vinculados |
| `mejoras_resumen` | Object | Resumen desglosado (ver abajo) |

#### Estructura de `mejoras_resumen`

```json
{
    "total_planes": 3,
    "planes_pendientes": 1,
    "planes_en_curso": 1,
    "planes_completados": 1,
    "total_hallazgos": 5,
    "hallazgos_abiertos": 2,
    "hallazgos_cerrados": 3
}
```

### Campos de Integración en Cumplimiento

El serializer de listado de Cumplimiento incluye:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `planes_mejora_count` | Integer | Planes de mejora vinculados al cumplimiento |
| `hallazgos_count` | Integer | Hallazgos vinculados (autoevaluación + criterio) |
| `tiene_plan_mejora` | Boolean | Si tiene algún plan (app mejoras o campo legacy) |

### Flujo de Integración

```
1. Evaluar cumplimiento → cumple=NO_CUMPLE

2. Crear hallazgo vinculado:
   POST /api/mejoras/hallazgos/
   { "origen_tipo": "HABILITACION", "autoevaluacion": 1, "criterio": 5, ... }

3. Crear plan de mejora vinculado:
   POST /api/mejoras/planes-mejora/
   { "origen_tipo": "HABILITACION", "autoevaluacion": 1, "cumplimiento": 10, ... }

4. Vincular hallazgo al plan:
   PATCH /api/mejoras/hallazgos/{id}/
   { "plan_mejora": 1 }

5. Subir evidencia:
   POST /api/mejoras/planes-mejora/1/soportes/
   archivo + tipo_soporte=EVIDENCIA

6. Consultar resultados integrados:
   GET /api/habilitacion/autoevaluaciones/{id}/
   → planes_mejora_count, hallazgos_count, mejoras_resumen
```

---

# Parte III - Módulo de Auditoría

## Módulo de Auditoría

El módulo de **Auditoría** (`audit/`) gestiona el ciclo de vida completo de auditorías internas y externas.

### Base URL
```
http://localhost:8000/api/audit/
```

### 13.1 Modelos del Módulo

#### Auditoria

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `auditoria_id` | Integer | Sí (PK) | Identificador único |
| `auditoria_nombre` | CharField(200) | Sí | Nombre de la auditoría |
| `auditoria_detalle` | TextField | No | Detalle o alcance |
| `clasificacion` | Choice | No | Default: INTERNA. Opciones: INTERNA, EXTERNA |
| `auditoria_tipo` | FK(TipoAuditoria) | No | Tipo de auditoría |
| `auditoria_entidad` | FK(EntidadAuditoria) | No | Entidad auditora |
| `auditoria_proceso` | FK(Process) | No | Proceso auditado |
| `sede` | FK(Headquarters) | No | Sede auditada |
| `norma_referencia` | CharField(200) | No | Norma de referencia |
| `fase` | Choice | No | Default: PROGRAMADA |
| `auditoria_estado` | Boolean | No | Default: true (activa) |
| `fecha_programada` | DateField | No | Fecha programada |
| `auditoria_fecha_notificacion` | DateField | No | Fecha de notificación |
| `fecha_inicio_ejecucion` | DateField | No | Inicio de ejecución |
| `auditoria_fecha_auditoria` | DateField | No | Fecha de la auditoría |
| `fecha_informe` | DateField | No | Fecha del informe |
| `fecha_cierre` | DateField | No | Fecha de cierre |
| `auditor_lider` | FK(User) | No | Auditor líder |
| `auditoria_responsable` | CharField(200) | No | Responsable |
| `conclusion` | TextField | No | Conclusión |
| `recomendaciones` | TextField | No | Recomendaciones |
| `auditoria_relacionada` | FK(self) | No | Auditoría de seguimiento |
| `creado_por` | FK(User) | Auto | Asignado automáticamente |
| `fecha_creacion` | DateTime | Auto | Creación |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

**Propiedades calculadas**:
- `esta_activa`: Boolean, si no está en CERRADA o CANCELADA
- `dias_para_ejecucion`: Días hasta la fecha programada
- `duracion_dias`: Días entre inicio y fin de ejecución
- `total_hallazgos`: Conteo de hallazgos
- `total_no_conformidades`: Conteo de NC_MAYOR + NC_MENOR

#### TipoAuditoria

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| `id` | Integer | PK |
| `nombre` | CharField(100) | Sí |
| `descripcion` | TextField | No |

#### EntidadAuditoria

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| `id` | Integer | PK |
| `nombre` | CharField(200) | Sí |
| `tipo_entidad` | Choice | Sí. Valores: CERTIFICADORA, ACREDITADORA, ENTE_CONTROL, INTERNA, OTRA |
| `descripcion` | TextField | No |
| `contacto` | CharField(200) | No |

#### MiembroEquipoAuditor

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| `id` | Integer | PK |
| `auditoria` | FK(Auditoria) | Sí |
| `usuario` | FK(User) | Sí |
| `rol` | Choice | No | Default: AUDITOR. Valores: LIDER, AUDITOR, OBSERVADOR, EXPERTO |
| `area_responsable` | CharField(200) | No |

> **Nota**: La combinación (auditoria, usuario) es única.

---

### 13.2 Endpoints de Auditoría

#### Catálogos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/audit/tipos/` | Listar tipos de auditoría |
| POST | `/api/audit/tipos/` | Crear tipo |
| GET | `/api/audit/tipos/{id}/` | Detalle tipo |
| PUT/PATCH | `/api/audit/tipos/{id}/` | Actualizar tipo |
| DELETE | `/api/audit/tipos/{id}/` | Eliminar tipo |
| GET | `/api/audit/entidades/` | Listar entidades |
| POST | `/api/audit/entidades/` | Crear entidad |
| GET | `/api/audit/entidades/{id}/` | Detalle entidad |
| PUT/PATCH | `/api/audit/entidades/{id}/` | Actualizar entidad |
| DELETE | `/api/audit/entidades/{id}/` | Eliminar entidad |

#### Auditoría CRUD

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/audit/auditorias/` | Listar auditorías |
| POST | `/api/audit/auditorias/` | Crear auditoría |
| GET | `/api/audit/auditorias/{id}/` | Detalle (incluye equipo, hallazgos, actas) |
| PUT | `/api/audit/auditorias/{id}/` | Actualizar auditoría |
| PATCH | `/api/audit/auditorias/{id}/` | Actualización parcial |
| DELETE | `/api/audit/auditorias/{id}/` | Eliminar auditoría |

#### Acciones de Ciclo de Vida

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/audit/auditorias/{id}/cambiar-fase/` | Cambiar fase con validación |
| GET | `/api/audit/auditorias/{id}/equipo/` | Listar equipo auditor |
| POST | `/api/audit/auditorias/{id}/equipo/` | Agregar miembro al equipo |
| DELETE | `/api/audit/auditorias/{id}/equipo/{miembro_id}/` | Eliminar miembro |
| GET | `/api/audit/auditorias/{id}/actas/` | Listar actas de la auditoría |
| POST | `/api/audit/auditorias/{id}/actas/` | Crear acta vinculada |

#### Estadísticas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/audit/auditorias/resumen/` | Resumen general |
| GET | `/api/audit/auditorias/proximas/` | Próximas (default 30 días) |
| GET | `/api/audit/auditorias/proximas/?dias=60` | Próximas (N días) |
| GET | `/api/audit/auditorias/por-fase/` | Conteo agrupado por fase |

#### Campos de respuesta - Listado

```json
{
    "auditoria_id": 1,
    "auditoria_nombre": "Auditoría Interna Calidad 2026",
    "clasificacion": "INTERNA",
    "clasificacion_display": "Interna",
    "auditoria_tipo": 1,
    "tipo_nombre": "Auditoría de Calidad",
    "auditoria_entidad": null,
    "entidad_nombre": "",
    "auditoria_proceso": null,
    "proceso_nombre": "",
    "sede": null,
    "sede_nombre": "",
    "fase": "PROGRAMADA",
    "fase_display": "Programada",
    "auditoria_estado": true,
    "fecha_programada": "2026-03-15",
    "auditor_lider": null,
    "auditor_lider_nombre": "",
    "esta_activa": true,
    "total_hallazgos": 0,
    "dias_para_ejecucion": 23,
    "fecha_creacion": "2026-02-20T10:00:00Z",
    "fecha_actualizacion": "2026-02-20T10:00:00Z"
}
```

#### Campos de respuesta - Detalle (adicionales)

```json
{
    "...campos del listado...",
    "auditoria_detalle": "Alcance: procesos de calidad",
    "norma_referencia": "ISO 9001:2015",
    "auditoria_fecha_notificacion": null,
    "fecha_inicio_ejecucion": null,
    "auditoria_fecha_auditoria": null,
    "fecha_informe": null,
    "fecha_cierre": null,
    "auditoria_responsable": "",
    "conclusion": "",
    "recomendaciones": "",
    "auditoria_relacionada": null,
    "creado_por": 1,
    "equipo_auditor": [],
    "hallazgos_auditoria": [],
    "actas": [],
    "duracion_dias": null,
    "total_no_conformidades": 0,
    "transiciones_permitidas": ["NOTIFICADA", "CANCELADA"]
}
```

> **Nota**: El campo de hallazgos en el detalle se llama `hallazgos_auditoria` (no `hallazgos`). El campo `transiciones_permitidas` muestra las fases a las que se puede avanzar.

#### Campos requeridos para crear

```json
{
    "auditoria_nombre": "Auditoría Interna Calidad 2026"
}
```

**Campos opcionales**: `auditoria_detalle`, `clasificacion`, `auditoria_tipo`, `auditoria_entidad`, `auditoria_proceso`, `sede`, `norma_referencia`, `fase`, `fecha_programada`, `auditor_lider`, `auditoria_responsable`

#### Filtros disponibles

| Parámetro | Valores |
|-----------|---------|
| `?fase=` | PROGRAMADA, NOTIFICADA, EN_EJECUCION, INFORME, SEGUIMIENTO, CERRADA, CANCELADA |
| `?clasificacion=` | INTERNA, EXTERNA |
| `?auditoria_tipo=` | ID |
| `?auditoria_entidad=` | ID |
| `?auditoria_proceso=` | ID |
| `?sede=` | ID |
| `?auditoria_estado=` | true, false |
| `?auditor_lider=` | ID |
| `?search=` | Buscar en auditoria_nombre, auditoria_detalle, norma_referencia |
| `?ordering=` | fecha_creacion, fecha_programada, fase, clasificacion |

#### Respuesta de Resumen

```json
{
    "total": 15,
    "activas": 10,
    "programada": 3,
    "notificada": 2,
    "en_ejecucion": 3,
    "informe": 1,
    "seguimiento": 1,
    "cerrada": 4,
    "cancelada": 1,
    "internas": 10,
    "externas": 5,
    "con_hallazgos": 8
}
```

---

## Ciclo de Vida de Auditoría

### Fases

| Fase | Display | Descripción |
|------|---------|-------------|
| `PROGRAMADA` | Programada | Auditoría planificada |
| `NOTIFICADA` | Notificada | Equipo y auditados informados |
| `EN_EJECUCION` | En Ejecución | Revisión documental y en sitio |
| `INFORME` | Informe | Elaboración del informe final |
| `SEGUIMIENTO` | Seguimiento | Verificación de acciones correctivas |
| `CERRADA` | Cerrada | Auditoría finalizada |
| `CANCELADA` | Cancelada | Auditoría cancelada |

### Transiciones Permitidas

```
PROGRAMADA → NOTIFICADA, CANCELADA
NOTIFICADA → EN_EJECUCION, CANCELADA
EN_EJECUCION → INFORME
INFORME → SEGUIMIENTO, CERRADA
SEGUIMIENTO → CERRADA
CERRADA → (sin transiciones)
CANCELADA → (sin transiciones)
```

> **Importante**: `CANCELADA` solo es accesible desde `PROGRAMADA` y `NOTIFICADA`. Desde `EN_EJECUCION` en adelante, el flujo debe completarse.

### Diagrama de Flujo

```
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌─────────┐    ┌─────────────┐    ┌─────────┐
│PROGRAMADA│───→│NOTIFICADA│───→│EN_EJECUCION│───→│ INFORME │───→│SEGUIMIENTO  │───→│ CERRADA │
└──────────┘    └──────────┘    └────────────┘    └─────────┘    └─────────────┘    └─────────┘
     │               │                                  │
     │               │                                  │
     ↓               ↓                                  ↓
┌──────────┐                                       ┌─────────┐
│CANCELADA │                                       │ CERRADA │
└──────────┘                                       └─────────┘
```

### Cambiar Fase

```http
POST /api/audit/auditorias/1/cambiar-fase/
Authorization: Bearer eyJ...
Content-Type: application/json

{
    "nueva_fase": "NOTIFICADA"
}
```

**Respuesta (200 OK)**: Retorna el objeto completo de la auditoría (AuditoriaDetailSerializer):

```json
{
    "auditoria_id": 1,
    "auditoria_nombre": "Auditoría Interna Calidad 2026",
    "fase": "NOTIFICADA",
    "fase_display": "Notificada",
    "transiciones_permitidas": ["EN_EJECUCION", "CANCELADA"],
    "...demás campos del detalle..."
}
```

**Error - Transición no permitida (400)**:
```json
{
    "nueva_fase": ["Transición no permitida de CERRADA a PROGRAMADA."]
}
```

### Equipo Auditor

#### Listar equipo

```http
GET /api/audit/auditorias/1/equipo/
```

```json
[
    {
        "id": 1,
        "auditoria": 1,
        "usuario": 1,
        "usuario_nombre": "Admin User",
        "rol": "LIDER",
        "rol_display": "Auditor Líder",
        "area_responsable": "Calidad"
    }
]
```

#### Agregar miembro

```http
POST /api/audit/auditorias/1/equipo/
Content-Type: application/json

{
    "usuario": 1,
    "rol": "LIDER",
    "area_responsable": "Calidad"
}
```

Roles disponibles: `LIDER`, `AUDITOR`, `OBSERVADOR`, `EXPERTO`

#### Eliminar miembro

```http
DELETE /api/audit/auditorias/1/equipo/5/
```

**Respuesta**: `204 No Content`

---

## Hallazgos de Auditoría

### 15.1 HallazgoAuditoria

**Descripción**: Hallazgo identificado durante una auditoría. Se integra opcionalmente con el módulo de mejoras.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `auditoria` | FK(Auditoria) | Sí | Auditoría donde se identificó |
| `numero` | CharField(30) | Sí | Número del hallazgo |
| `tipo` | Choice | Sí | NC_MAYOR, NC_MENOR, OBSERVACION, OPORTUNIDAD, FORTALEZA |
| `criterio_norma` | CharField(200) | No | Numeral de norma incumplido |
| `descripcion` | TextField | Sí | Descripción del hallazgo |
| `evidencia_objetiva` | TextField | No | Evidencia objetiva |
| `proceso_afectado` | FK(Process) | No | Proceso afectado |
| `responsable_accion` | FK(User) | No | Responsable de la acción correctiva |
| `estado` | Choice | No | Default: IDENTIFICADO |
| `fecha_limite_accion` | DateField | No | Fecha límite para acción correctiva |
| `fecha_verificacion` | DateField | No | Fecha de verificación |
| `hallazgo_mejora` | FK(mejoras.Hallazgo) | No | Hallazgo en módulo de mejoras |
| `plan_mejora` | FK(mejoras.PlanMejora) | No | Plan de mejora vinculado |
| `fecha_creacion` | DateTime | Auto | Creación |
| `fecha_actualizacion` | DateTime | Auto | Última actualización |

### Tipos de Hallazgo de Auditoría

| Valor | Display |
|-------|---------|
| `NC_MAYOR` | No Conformidad Mayor |
| `NC_MENOR` | No Conformidad Menor |
| `OBSERVACION` | Observación |
| `OPORTUNIDAD` | Oportunidad de Mejora |
| `FORTALEZA` | Fortaleza |

### Estados de Hallazgo de Auditoría

| Valor | Display |
|-------|---------|
| `IDENTIFICADO` | Identificado |
| `PLAN_ACCION` | Con Plan de Acción |
| `EN_SEGUIMIENTO` | En Seguimiento |
| `VERIFICADO` | Verificado |
| `CERRADO` | Cerrado |

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/audit/hallazgos/` | Listar todos los hallazgos |
| POST | `/api/audit/hallazgos/` | Crear hallazgo |
| GET | `/api/audit/hallazgos/{id}/` | Detalle |
| PUT/PATCH | `/api/audit/hallazgos/{id}/` | Actualizar |
| DELETE | `/api/audit/hallazgos/{id}/` | Eliminar |

#### Crear hallazgo de auditoría

```json
{
    "auditoria": 1,
    "numero": "H-001",
    "tipo": "NC_MAYOR",
    "descripcion": "No se evidencian registros de capacitación",
    "criterio_norma": "4.4.2",
    "evidencia_objetiva": "Se revisaron carpetas sin documentación",
    "estado": "IDENTIFICADO"
}
```

#### Filtros disponibles

| Parámetro | Valores |
|-----------|---------|
| `?auditoria=` | ID |
| `?tipo=` | NC_MAYOR, NC_MENOR, OBSERVACION, OPORTUNIDAD, FORTALEZA |
| `?estado=` | IDENTIFICADO, PLAN_ACCION, EN_SEGUIMIENTO, VERIFICADO, CERRADO |
| `?responsable_accion=` | ID |
| `?proceso_afectado=` | ID |
| `?search=` | Buscar en numero, descripcion, criterio_norma, evidencia_objetiva |

---

## Actas y Programas

### 16.1 ActaReunion

**Descripción**: Actas de reuniones del proceso de auditoría.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `auditoria` | FK(Auditoria) | Sí | Auditoría asociada |
| `tipo_acta` | Choice | Sí | APERTURA, CIERRE, SEGUIMIENTO |
| `fecha` | DateField | Sí | Fecha de la reunión |
| `lugar` | CharField(200) | No | Lugar de la reunión |
| `asistentes` | TextField | No | Lista de asistentes |
| `temas_tratados` | TextField | No | Temas tratados |
| `compromisos` | TextField | No | Compromisos adquiridos |
| `observaciones` | TextField | No | Observaciones generales |
| `fecha_creacion` | DateTime | Auto | Creación |

#### Endpoints de Actas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/audit/actas/` | Listar todas las actas |
| POST | `/api/audit/actas/` | Crear acta |
| GET | `/api/audit/actas/{id}/` | Detalle acta |
| PUT/PATCH | `/api/audit/actas/{id}/` | Actualizar |
| DELETE | `/api/audit/actas/{id}/` | Eliminar |
| GET | `/api/audit/auditorias/{id}/actas/` | Actas de una auditoría |
| POST | `/api/audit/auditorias/{id}/actas/` | Crear acta vía auditoría |

#### Crear acta

```json
{
    "auditoria": 1,
    "tipo_acta": "APERTURA",
    "fecha": "2026-03-15",
    "lugar": "Sala de reuniones principal",
    "asistentes": "Dr. García, Lic. Pérez, Ing. López",
    "temas_tratados": "Apertura del proceso de auditoría interna",
    "compromisos": "Enviar documentación antes del viernes",
    "observaciones": "Se estableció cronograma de revisión"
}
```

---

### 16.2 ProgramaAuditoria

**Descripción**: Programa anual o semestral de auditorías.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `nombre` | CharField(200) | Sí | Nombre del programa |
| `periodo` | CharField(20) | Sí | Periodo (ej: "2026", "2026-S1") |
| `descripcion` | TextField | No | Descripción |
| `estado` | Choice | No | Default: BORRADOR. Opciones: BORRADOR, APROBADO, EN_EJECUCION, COMPLETADO |
| `responsable` | FK(User) | No | Responsable del programa |
| `fecha_aprobacion` | DateField | No | Fecha de aprobación |
| `auditorias` | M2M(Auditoria) | No | Auditorías incluidas |

#### Endpoints de Programas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/audit/programas/` | Listar programas |
| POST | `/api/audit/programas/` | Crear programa |
| GET | `/api/audit/programas/{id}/` | Detalle (incluye auditorías) |
| PUT/PATCH | `/api/audit/programas/{id}/` | Actualizar |
| DELETE | `/api/audit/programas/{id}/` | Eliminar |

#### Crear programa

```json
{
    "nombre": "Programa de Auditorías 2026",
    "periodo": "2026",
    "descripcion": "Programa anual de auditorías internas de calidad",
    "estado": "BORRADOR"
}
```

---

## Enumeraciones Completas - Referencia Rápida

### Habilitación

| Modelo | Campo | Valores |
|--------|-------|---------|
| DatosPrestador | clase_prestador | IPS, PROF, PH, PJ |
| DatosPrestador | estado_habilitacion | HABILITADA, EN_PROCESO, SUSPENDIDA, NO_HABILITADA, CANCELADA |
| ServicioSede | modalidad | INTRAMURAL, AMBULATORIA, TELEMEDICINA, URGENCIAS, AMBULANCIA |
| ServicioSede | complejidad | BAJA, MEDIA, ALTA |
| ServicioSede | estado_habilitacion | HABILITADO, EN_PROCESO, SUSPENDIDO, NO_HABILITADO, CANCELADO |
| Autoevaluacion | estado | BORRADOR, EN_CURSO, COMPLETADA, REVISADA, VALIDADA |
| Cumplimiento | cumple | CUMPLE, NO_CUMPLE, PARCIALMENTE, NO_APLICA |

### Mejoras

| Modelo | Campo | Valores |
|--------|-------|---------|
| PlanMejora | origen_tipo | HABILITACION, AUDITORIA, INDICADOR |
| PlanMejora | estado | PENDIENTE, EN_CURSO, COMPLETADO, VENCIDO |
| PlanMejora | prioridad | BAJA, MEDIA, ALTA, URGENTE |
| Hallazgo | tipo | FORTALEZA, OPORTUNIDAD_MEJORA, NO_CONFORMIDAD, HALLAZGO |
| Hallazgo | severidad | BAJA, MEDIA, ALTA, CRÍTICA |
| Hallazgo | estado | ABIERTO, EN_SEGUIMIENTO, CERRADO |
| Hallazgo | origen_tipo | HABILITACION, AUDITORIA, INDICADOR |
| SoportePlan | tipo_soporte | EVIDENCIA, ACTA, INFORME, FOTOGRAFIA, PLAN_ACCION, OTRO |

### Auditoría

| Modelo | Campo | Valores |
|--------|-------|---------|
| Auditoria | clasificacion | INTERNA, EXTERNA |
| Auditoria | fase | PROGRAMADA, NOTIFICADA, EN_EJECUCION, INFORME, SEGUIMIENTO, CERRADA, CANCELADA |
| EntidadAuditoria | tipo_entidad | CERTIFICADORA, ACREDITADORA, ENTE_CONTROL, INTERNA, OTRA |
| MiembroEquipo | rol | LIDER, AUDITOR, OBSERVADOR, EXPERTO |
| HallazgoAuditoria | tipo | NC_MAYOR, NC_MENOR, OBSERVACION, OPORTUNIDAD, FORTALEZA |
| HallazgoAuditoria | estado | IDENTIFICADO, PLAN_ACCION, EN_SEGUIMIENTO, VERIFICADO, CERRADO |
| ActaReunion | tipo_acta | APERTURA, CIERRE, SEGUIMIENTO |
| ProgramaAuditoria | estado | BORRADOR, APROBADO, EN_EJECUCION, COMPLETADO |

---

## Historial de Cambios

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-02-18 | Documentación inicial de habilitación |
| 2.0 | 2026-02-20 | Añadidos módulos de Mejoras y Auditoría |
| 3.0 | 2026-02-20 | Corrección completa: campos, endpoints, enumeraciones, ejemplos alineados con el código fuente real. Corregidos nombres de campos (tipo vs tipo_hallazgo, numero_plan, etc.), URLs (proximos-vencer, equipo/{id}), formatos de respuesta, campos requeridos, y transiciones de fase |
