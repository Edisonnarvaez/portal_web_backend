# Documentación Frontend - Módulo de Habilitación

Fecha: 2026-02-18  
Versión: 1.0  
Aplicación: Portal Web Backend - Habilitación de Servicios de Salud

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura de Modelos](#arquitectura-de-modelos)
3. [Endpoints de API](#endpoints-de-api)
4. [Autenticación y Autorización](#autenticación-y-autorización)
5. [Flujos Principales](#flujos-principales)
6. [Estados y Enumeraciones](#estados-y-enumeraciones)
7. [Ejemplos de Requests/Responses](#ejemplos-de-requestsresponses)
8. [Pantallas Recomendadas](#pantallas-recomendadas)
9. [Relaciones entre Entidades](#relaciones-entre-entidades)

---

## Introducción

El módulo de **Habilitación** es el corazón del Portal Web Backend. Permite gestionar la habilitación de servicios de salud siguiendo la **Resolución 3100 de 2019** de Colombia.

### Conceptos Clave

- **DatosPrestador**: Información de habilitación de una Institución Prestadora de Servicios (IPS) o prestador individual
- **ServicioSede**: Servicios de salud específicos habilitados en una sede
- **Autoevaluación**: Evaluación anual mandatory contra criterios de calidad
- **Cumplimiento**: Registro detallado de cumplimiento de un criterio específico
- **Criterio**: Requísito de la Resolución 3100 que debe cumplirse

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
- ForeignKey → `Company` (app companies)
- ForeignKey → `User` (usuario responsable)
- ForeignKey ← `Autoevaluacion` (múltiples)
- ForeignKey ← `ServicioSede` (múltiples, a través de Headquarters)

**Campos Principales**:

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | Identificador único |
| `codigo_reps` | CharField(20) | Sí | Código REPS único de la Superintendencia |
| `clase_prestador` | Choice | Sí | IPS, PROF, PH, PJ |
| `estado_habilitacion` | Choice | Sí | HABILITADA, EN_PROCESO, SUSPENDIDA, NO_HABILITADA, CANCELADA |
| `fecha_inscripcion` | DateField | No | Fecha de inscripción en REPS |
| `fecha_renovacion` | DateField | No | Fecha de última renovación |
| `fecha_vencimiento_habilitacion` | DateField | No | Cuándo expira la habilitación |
| `aseguradora_pep` | CharField(255) | No | Nombre de aseguradora responsabilidad civil |
| `numero_poliza` | CharField(50) | No | Número de póliza |
| `vigencia_poliza` | DateField | No | Hasta cuándo es válida la póliza |
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

**Campos Principales**:

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | ID único |
| `codigo_servicio` | CharField(20) | Sí | Código asignado por REPS |
| `nombre_servicio` | CharField(255) | Sí | Nombre descriptivo (ej: Cirugía General) |
| `descripcion` | TextField | No | Descripción detallada |
| `modalidad` | Choice | Sí | INTRAMURAL, AMBULATORIA, TELEMEDICINA, URGENCIAS, AMBULANCIA |
| `complejidad` | Choice | Sí | BAJA, MEDIA, ALTA |
| `estado_habilitacion` | Choice | Sí | HABILITADO, EN_PROCESO, SUSPENDIDO, NO_HABILITADO, CANCELADO |
| `fecha_habilitacion` | DateField | No | Cuándo se habilitó |
| `fecha_vencimiento` | DateField | No | Cuándo vence |

**Métodos Útiles**:
- `dias_para_vencimiento()`: Días restantes
- `esta_vencido()`: Boolean

**Tabla en BD**: `habilitacion_serviciosede`

---

### 3. Autoevaluación

**Descripción**: Evaluación anual mandatory de la IPS contra criterios de la Resolución 3100.

**Relaciones**:
- ForeignKey → `DatosPrestador`
- ForeignKey → `User` (usuario responsable)
- ForeignKey ← `Cumplimiento` (múltiples)

**Campos Principales**:

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | ID único |
| `numero_autoevaluacion` | CharField(50) | Auto | Ej: AUT-REPS123-2025 |
| `periodo` | Integer | Sí | Año fiscal (2024, 2025, 2026, etc.) |
| `version` | Integer | Sí | Versión del documento (para duplicados) |
| `estado` | Choice | Sí | BORRADOR, EN_CURSO, COMPLETADA, REVISADA, VALIDADA |
| `fecha_inicio` | DateField | Auto | Cuándo comenzó |
| `fecha_completacion` | DateField | No | Cuándo terminó |
| `fecha_vencimiento` | DateField | Sí | Fecha máxima de validez |
| `observaciones` | TextField | No | Notas adicionales |

**Métodos Útiles**:
- `porcentaje_cumplimiento()`: % de criterios cumplidos
- `esta_vigente()`: Boolean si aún es válida

**Tabla en BD**: `habilitacion_autoevaluacion`

---

### 4. Cumplimiento

**Descripción**: Registro detallado de cumplimiento de un criterio en una autoevaluación específica.

**Relaciones**:
- ForeignKey → `Autoevaluacion`
- ForeignKey → `ServicioSede`
- ForeignKey → `Criterio` (app normativity)
- ForeignKey → `User` (responsable mejora)
- ManyToMany → `Documento` (evidencia)

**Campos Principales**:

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `id` | Integer | Sí (PK) | ID único |
| `cumple` | Choice | Sí | CUMPLE, NO_CUMPLE, PARCIALMENTE, NO_APLICA |
| `hallazgo` | TextField | No | Qué se encontró en la evaluación |
| `plan_mejora` | TextField | No | Plan de acción para mejorar |
| `responsable_mejora` | ForeignKey | No | Quién es responsable |
| `fecha_compromiso` | DateField | No | Fecha límite para mejorar |

**Métodos Útiles**:
- `tiene_plan_mejora()`: Boolean si hay mejora pendiente
- `mejora_vencida()`: Boolean si ya pasó la fecha

**Tabla en BD**: `habilitacion_cumplimiento`

---

## Endpoints de API

### AutoPrestador - Datos de Habilitación

#### **Listar Todos los Prestadores**
```
GET /api/habilitacion/prestadores/
```

**Query Parameters**:
- `page` (int): Número de página (default: 1, 20 items/página)
- `search` (string): Buscar por código_reps o nombre company
- `estado_habilitacion` (choice): Filtrar por estado
- `clase_prestador` (choice): Filtrar por clase
- `ordering` (string): Ordenar por campo

**Response**: 
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/habilitacion/prestadores/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "codigo_reps": "REPS001",
      "company_name": "Clínica San José",
      "clase_prestador": "IPS",
      "estado_habilitacion": "HABILITADA",
      "estado_display": "Habilitada",
      "fecha_vencimiento_habilitacion": "2025-12-31",
      "proxima_vencer": true,
      "dias_vencimiento": 45
    }
  ]
}
```

---

#### **Crear Nuevo Prestador**
```
POST /api/habilitacion/prestadores/
```

**Body Requerido**:
```json
{
  "codigo_reps": "REPS002",
  "company_id": 5,
  "clase_prestador": "IPS",
  "estado_habilitacion": "EN_PROCESO",
  "fecha_inscripcion": "2024-01-15",
  "aseguradora_pep": "ACE Seguros",
  "numero_poliza": "POL-2024-0001",
  "vigencia_poliza": "2025-01-15"
}
```

**Response** (201 Created):
```json
{
  "id": 12,
  "codigo_reps": "REPS002",
  "company_id": 5,
  "company_detail": {
    "id": 5,
    "name": "Clínica San José",
    "nit": "900123456"
  },
  "clase_prestador": "IPS",
  "clase_prestador_display": "Institución Prestadora de Servicios",
  "estado_habilitacion": "EN_PROCESO",
  "estado_display": "En Proceso",
  "fecha_inscripcion": "2024-01-15",
  "fecha_renovacion": null,
  "fecha_vencimiento_habilitacion": null,
  "dias_vencimiento": null,
  "proxima_vencer": false,
  "vencida": false,
  "aseguradora_pep": "ACE Seguros",
  "numero_poliza": "POL-2024-0001",
  "vigencia_poliza": "2025-01-15",
  "autoevaluaciones_count": 0,
  "fecha_creacion": "2026-02-18T10:30:00Z",
  "fecha_actualizacion": "2026-02-18T10:30:00Z"
}
```

---

#### **Obtener Detalle de Prestador**
```
GET /api/habilitacion/prestadores/{id}/
```

**Response** (200 OK):
```json
{
  "id": 1,
  "codigo_reps": "REPS001",
  "company_id": 3,
  "company_detail": {
    "id": 3,
    "name": "Clínica San José",
    "nit": "900123456"
  },
  "clase_prestador": "IPS",
  "clase_prestador_display": "Institución Prestadora de Servicios",
  "estado_habilitacion": "HABILITADA",
  "estado_display": "Habilitada",
  "fecha_inscripcion": "2023-01-15",
  "fecha_renovacion": "2024-06-20",
  "fecha_vencimiento_habilitacion": "2025-12-31",
  "dias_vencimiento": 45,
  "proxima_vencer": true,
  "vencida": false,
  "aseguradora_pep": "ACE Seguros",
  "numero_poliza": "POL-2024-0001",
  "vigencia_poliza": "2025-12-31",
  "autoevaluaciones_count": 2,
  "fecha_creacion": "2023-01-15T08:00:00Z",
  "fecha_actualizacion": "2026-02-18T10:30:00Z"
}
```

---

#### **Actualizar Prestador**
```
PUT /api/habilitacion/prestadores/{id}/
```

Enviar todos los campos. Para actualización parcial:

```
PATCH /api/habilitacion/prestadores/{id}/
```

Enviar solo los campos a actualizar.

---

#### **Eliminar Prestador**
```
DELETE /api/habilitacion/prestadores/{id}/
```

**Response** (204 No Content)

---

#### **Prestadores Próximos a Vencer**
```
GET /api/habilitacion/prestadores/proximos_a_vencer/
```

Retorna prestadores con habilitación venciendo en próximos 90 días.

---

#### **Prestadores Vencidos**
```
GET /api/habilitacion/prestadores/vencidas/
```

Retorna prestadores con habilitación ya vencida.

---

#### **Servicios de un Prestador**
```
GET /api/habilitacion/prestadores/{id}/servicios/
```

Retorna todos los servicios habilitados de ese prestador.

---

#### **Autoevaluaciones de un Prestador**
```
GET /api/habilitacion/prestadores/{id}/autoevaluaciones/
```

Retorna historial de autoevaluaciones.

---

#### **Iniciar Renovación**
```
POST /api/habilitacion/prestadores/{id}/iniciar_renovacion/
```

Cambia estado a EN_PROCESO. Solo permite si falta ≤180 días para vencimiento.

---

### Servicios por Sede

#### **Listar Todos los Servicios**
```
GET /api/habilitacion/servicios/
```

**Query Parameters**:
- `sede` (int): Filtrar por ID de sede
- `modalidad` (choice): INTRAMURAL, AMBULATORIA, TELEMEDICINA, URGENCIAS, AMBULANCIA
- `complejidad` (choice): BAJA, MEDIA, ALTA
- `estado_habilitacion` (choice)
- `search` (string): Buscar por código o nombre

**Response**:
```json
{
  "count": 120,
  "results": [
    {
      "id": 45,
      "codigo_servicio": "SRV-001",
      "nombre_servicio": "Cirugía General",
      "sede_nombre": "Sede Hospital Centro",
      "modalidad": "INTRAMURAL",
      "modalidad_display": "Intramural",
      "complejidad": "ALTA",
      "complejidad_display": "Alta",
      "estado_habilitacion": "HABILITADO",
      "estado_display": "Habilitado",
      "fecha_vencimiento": "2025-06-30",
      "vencido": false
    }
  ]
}
```

---

#### **Crear Nuevo Servicio**
```
POST /api/habilitacion/servicios/
```

**Body**:
```json
{
  "codigo_servicio": "SRV-045",
  "nombre_servicio": "Cardiología",
  "descripcion": "Servicio de diagnóstico y tratamiento de enfermedades cardiovasculares",
  "sede_id": 3,
  "modalidad": "AMBULATORIA",
  "complejidad": "ALTA",
  "estado_habilitacion": "EN_PROCESO",
  "fecha_habilitacion": "2026-02-18",
  "fecha_vencimiento": "2027-02-18"
}
```

---

#### **Servicios Próximos a Vencer**
```
GET /api/habilitacion/servicios/proximos_a_vencer/
```

Servicios venciendo en próximos 90 días.

---

#### **Filtrar por Complejidad**
```
GET /api/habilitacion/servicios/por_complejidad/?complejidad=ALTA
```

---

#### **Cumplimientos de un Servicio**
```
GET /api/habilitacion/servicios/{id}/cumplimientos/
```

Retorna cumplimientos evaluados del servicio en autoevaluaciones.

**Query Parameters**:
- `autoevaluacion_id` (int): Filtrar por autoevaluación específica

---

### Autoevaluaciones

#### **Listar Autoevaluaciones**
```
GET /api/habilitacion/autoevaluaciones/
```

**Query Parameters**:
- `datos_prestador` (int): Filtrar por prestador
- `periodo` (int): Filtrar por año
- `estado` (choice): Filtrar por estado

**Response**:
```json
{
  "count": 25,
  "results": [
    {
      "id": 10,
      "numero_autoevaluacion": "AUT-REPS001-2025",
      "prestador_codigo": "REPS001",
      "periodo": 2025,
      "version": 1,
      "estado": "COMPLETADA",
      "estado_display": "Completada",
      "fecha_inicio": "2026-01-15",
      "fecha_completacion": "2026-02-10",
      "porcentaje_cumplimiento": 87.5
    }
  ]
}
```

---

#### **Crear Autoevaluación**
```
POST /api/habilitacion/autoevaluaciones/
```

**Body**:
```json
{
  "datos_prestador_id": 1,
  "periodo": 2026,
  "fecha_vencimiento": "2027-02-18",
  "observaciones": "Evaluación 2026"
}
```

---

#### **Detalle de Autoevaluación**
```
GET /api/habilitacion/autoevaluaciones/{id}/
```

Incluye resumen de cumplimientos.

**Response**:
```json
{
  "id": 10,
  "numero_autoevaluacion": "AUT-REPS001-2025",
  "datos_prestador_id": 1,
  "datos_prestador_detail": {
    "id": 1,
    "codigo_reps": "REPS001",
    "company_name": "Clínica San José"
  },
  "periodo": 2025,
  "version": 1,
  "estado": "COMPLETADA",
  "estado_display": "Completada",
  "fecha_inicio": "2026-01-15",
  "fecha_completacion": "2026-02-10",
  "fecha_vencimiento": "2027-02-10",
  "vigente": true,
  "usuario_responsable_detail": {
    "id": 2,
    "username": "auditor1",
    "email": "auditor@hospital.com"
  },
  "observaciones": "Evaluación exitosa",
  "porcentaje_cumplimiento": 87.5,
  "total_cumplimientos": 80,
  "cumplimientos_data": {
    "total": 80,
    "cumple": 70,
    "no_cumple": 5,
    "parcialmente": 3,
    "no_aplica": 2
  },
  "fecha_creacion": "2026-01-15T09:00:00Z",
  "fecha_actualizacion": "2026-02-10T15:30:00Z"
}
```

---

#### **Autoevaluaciones Por Completar**
```
GET /api/habilitacion/autoevaluaciones/por_completar/
```

Estados: BORRADOR o EN_CURSO.

---

#### **Resumen Estadístico**
```
GET /api/habilitacion/autoevaluaciones/{id}/resumen/
```

Retorna estadísticas completas.

**Response**:
```json
{
  "numero_autoevaluacion": "AUT-REPS001-2025",
  "periodo": 2025,
  "estado": "Completada",
  "total_cumplimientos": 80,
  "resumen_por_resultado": {
    "cumple": 70,
    "no_cumple": 5,
    "parcialmente": 3,
    "no_aplica": 2
  },
  "porcentaje_cumplimiento": 87.5,
  "pendientes_mejora": 5,
  "mejoras_vencidas": 1
}
```

---

#### **Validar Autoevaluación**
```
POST /api/habilitacion/autoevaluaciones/{id}/validar/
```

Cambia estado a VALIDADA.

**Response** (200 OK): Detalle actualizado.

---

#### **Duplicar Autoevaluación**
```
POST /api/habilitacion/autoevaluaciones/{id}/duplicar/
```

Crea nueva versión para próximo período.

**Response** (201 Created): Nueva autoevaluación.

---

### Cumplimientos

#### **Listar Cumplimientos**
```
GET /api/habilitacion/cumplimientos/
```

**Query Parameters**:
- `autoevaluacion` (int)
- `servicio_sede` (int)
- `criterio` (int)
- `cumple` (choice)
- `search` (string)

**Response**:
```json
{
  "count": 1200,
  "results": [
    {
      "id": 520,
      "criterio_codigo": "1.1",
      "criterio_nombre": "Talento Humano - Requisitos Generales",
      "servicio_nombre": "Cirugía General",
      "cumple": "CUMPLE",
      "cumple_display": "Cumple",
      "tiene_plan_mejora": false,
      "fecha_compromiso": null
    }
  ]
}
```

---

#### **Crear Cumplimiento**
```
POST /api/habilitacion/cumplimientos/
```

**Body**:
```json
{
  "autoevaluacion_id": 10,
  "servicio_sede_id": 45,
  "criterio_id": 12,
  "cumple": "PARCIALMENTE",
  "hallazgo": "Se encuentra personal certificado pero falta de protocolos actualizados",
  "plan_mejora": "Actualizar protocolos en próximos 30 días",
  "responsable_mejora": 3,
  "fecha_compromiso": "2026-03-30"
}
```

---

#### **Detalle de Cumplimiento**
```
GET /api/habilitacion/cumplimientos/{id}/
```

---

#### **Cumplimientos sin Cumplir**
```
GET /api/habilitacion/cumplimientos/sin_cumplir/
```

Criterios NO_CUMPLE.

---

#### **Cumplimientos con Plan de Mejora**
```
GET /api/habilitacion/cumplimientos/con_plan_mejora/
```

---

#### **Mejoras Vencidas**
```
GET /api/habilitacion/cumplimientos/mejoras_vencidas/
```

Planes de mejora con fecha comprometida pasada.

---

## Autenticación y Autorización

### **JWT Token**

Todos los endpoints requieren autenticación JWT.

#### **Obtener Token**
```
POST /api/token/
Content-Type: application/json

{
  "username": "usuario@hospital.com",
  "password": "miPassword123"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **Usar Token**
```
GET /api/habilitacion/prestadores/
Authorization: Bearer <ACCESS_TOKEN>
```

#### **Refrescar Token**
```
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "<REFRESH_TOKEN>"
}
```

**Response**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### **Permisos**

- Solo usuarios autenticados (`IsAuthenticated`)
- Los responsables crean registros con su usuario automático

---

## Flujos Principales

### **Flujo 1: Registrar Nueva IPS/Prestador**

```
1. Crear DatosPrestador
   POST /api/habilitacion/prestadores/
   - codigo_reps (único)
   - company_id
   - clase_prestador
   - estado_habilitacion (iniciar en EN_PROCESO)

2. Registrar Servicios de la IPS
   POST /api/habilitacion/servicios/ (múltiples)
   - Para cada modalidad + tipo
   - Por cada sede

3. Crear Autoevaluación Inicial
   POST /api/habilitacion/autoevaluaciones/
   - periodo (año fiscal)
   - fecha_vencimiento

4. Evaluar Cumplimientos
   POST /api/habilitacion/cumplimientos/ (múltiples)
   - Para cada criterio + servicio
   - Marcar CUMPLE, NO_CUMPLE, PARCIALMENTE, NO_APLICA
```

---

### **Flujo 2: Completar Autoevaluación Anual**

```
1. Obtener Autoevaluación activa
   GET /api/habilitacion/autoevaluaciones/{id}/

2. Listar todos los Criterios necesarios
   GET /api/normativity/criterios/ (desde app normativity)

3. Para cada servicio + criterio:
   POST /api/habilitacion/cumplimientos/
   - Evaluar cumplimiento
   - Adjuntar evidencia (documentos)
   - Si NO_CUMPLE → crear plan mejora

4. Validar Autoevaluación
   POST /api/habilitacion/autoevaluaciones/{id}/validar/

5. Monitorear Mejoras
   GET /api/habilitacion/cumplimientos/mejoras_vencidas/
```

---

### **Flujo 3: Renovar Habilitación**

```
1. Verificar próximo a vencer
   GET /api/habilitacion/prestadores/proximos_a_vencer/

2. Iniciar renovación
   POST /api/habilitacion/prestadores/{id}/iniciar_renovacion/
   (Cambia a EN_PROCESO)

3. Completar nueva autoevaluación
   (Mismo proceso que Flujo 2, nuevo período)

4. Actualizar datos de habilitación
   PATCH /api/habilitacion/prestadores/{id}/
   - fecha_vencimiento_habilitacion: nueva fecha
   - estado_habilitacion: HABILITADA
   - fecha_renovacion: hoy

5. Duplicar autoevaluación para próximo año (recomendado)
   POST /api/habilitacion/autoevaluaciones/{id}/duplicar/
```

---

### **Flujo 4: Monitorear Estado General**

```
1. Dashboard - Resumen Ejecutivo:
   GET /api/habilitacion/prestadores/proximos_a_vencer/
   GET /api/habilitacion/prestadores/vencidas/
   GET /api/habilitacion/servicios/proximos_a_vencer/

2. Detalles por Prestador:
   GET /api/habilitacion/prestadores/{id}/
   GET /api/habilitacion/prestadores/{id}/autoevaluaciones/
   GET /api/habilitacion/prestadores/{id}/servicios/

3. Analítica de Cumplimiento:
   GET /api/habilitacion/autoevaluaciones/{id}/resumen/
   GET /api/habilitacion/cumplimientos/con_plan_mejora/
   GET /api/habilitacion/cumplimientos/mejoras_vencidas/
```

---

## Estados y Enumeraciones

### **Estado de Habilitación (DatosPrestador)**

| Código | Nombre | Descripción |
|--------|--------|-------------|
| `HABILITADA` | Habilitada | Prestador activo, puede prestar servicios |
| `EN_PROCESO` | En Proceso | Trámite de habilitación en marcha |
| `SUSPENDIDA` | Suspendida | Prestador bloqueado temporalmente |
| `NO_HABILITADA` | No Habilitada | Solicitud rechazada |
| `CANCELADA` | Cancelada | Prestador retirado del registro |

---

### **Clase de Prestador**

| Código | Nombre | Descripción |
|--------|--------|-------------|
| `IPS` | Institución Prestadora | Hospital, clínica |
| `PROF` | Profesional | Médico independiente |
| `PH` | Persona Humana | Profesional autónomo |
| `PJ` | Persona Jurídica | Empresa proveedora |

---

### **Modalidad de Servicio**

| Código | Nombre |
|--------|--------|
| `INTRAMURAL` | Internación, hospitalización |
| `AMBULATORIA` | Consulta externa |
| `TELEMEDICINA` | Atención remota |
| `URGENCIAS` | Servicio de emergencias |
| `AMBULANCIA` | Transporte sanitario |

---

### **Complejidad**

| Código | Nombre |
|--------|--------|
| `BAJA` | Servicios simples |
| `MEDIA` | Servicios moderados |
| `ALTA` | Servicios especializados |

---

### **Estado de Habilitación (ServicioSede)**

| Código | Nombre |
|--------|--------|
| `HABILITADO` | Servicio activo |
| `EN_PROCESO` | En trámite |
| `SUSPENDIDO` | Bloqueado |
| `NO_HABILITADO` | Rechazado |
| `CANCELADO` | Retirado |

---

### **Estado de Autoevaluación**

| Código | Nombre | Descripción |
|--------|--------|-------------|
| `BORRADOR` | Borrador | No iniciada |
| `EN_CURSO` | En Curso | Evaluación activa |
| `COMPLETADA` | Completada | Evaluación terminada |
| `REVISADA` | Revisada | Por auditor |
| `VALIDADA` | Validada | Oficialmente aceptada |

---

### **Resultado de Cumplimiento**

| Código | Nombre | Descripción |
|--------|--------|-------------|
| `CUMPLE` | Cumple | 100% conforme |
| `NO_CUMPLE` | No Cumple | No conforme |
| `PARCIALMENTE` | Parcialmente | Parcialmente conforme |
| `NO_APLICA` | No Aplica | Criterio no aplicable |

---

## Ejemplos de Requests/Responses

### **Ejemplo 1: Crear Prestador Completo**

```bash
curl -X POST http://localhost:8000/api/habilitacion/prestadores/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_reps": "REPS-CLIN-2024-001",
    "company_id": 5,
    "clase_prestador": "IPS",
    "estado_habilitacion": "EN_PROCESO",
    "fecha_inscripcion": "2024-02-15",
    "aseguradora_pep": "Seguros Bolivar",
    "numero_poliza": "POL-2024-1234567",
    "vigencia_poliza": "2025-02-15"
  }'
```

**Response (201)**:
```json
{
  "id": 15,
  "codigo_reps": "REPS-CLIN-2024-001",
  "company_id": 5,
  "company_detail": {
    "id": 5,
    "name": "Clínica del Norte",
    "nit": "901234567-8"
  },
  "clase_prestador": "IPS",
  "clase_prestador_display": "Institución Prestadora de Servicios",
  "estado_habilitacion": "EN_PROCESO",
  "estado_display": "En Proceso",
  "fecha_inscripcion": "2024-02-15",
  "fecha_renovacion": null,
  "fecha_vencimiento_habilitacion": null,
  "dias_vencimiento": null,
  "proxima_vencer": false,
  "vencida": false,
  "aseguradora_pep": "Seguros Bolivar",
  "numero_poliza": "POL-2024-1234567",
  "vigencia_poliza": "2025-02-15",
  "autoevaluaciones_count": 0,
  "fecha_creacion": "2026-02-18T14:30:45.123456Z",
  "fecha_actualizacion": "2026-02-18T14:30:45.123456Z"
}
```

---

### **Ejemplo 2: Evaluar Cumplimiento con Plan Mejora**

```bash
curl -X POST http://localhost:8000/api/habilitacion/cumplimientos/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "autoevaluacion_id": 10,
    "servicio_sede_id": 45,
    "criterio_id": 23,
    "cumple": "NO_CUMPLE",
    "hallazgo": "Personal sin certificación en Reanimación Cardiopulmonar (RCP) actual",
    "plan_mejora": "Programar entrenamiento obligatorio RCP para todos los médicos antes del 30 de Marzo de 2026",
    "responsable_mejora": 8,
    "fecha_compromiso": "2026-03-30"
  }'
```

**Response (201)**:
```json
{
  "id": 5234,
  "autoevaluacion_id": 10,
  "autoevaluacion_detail": {
    "id": 10,
    "numero": "AUT-REPS001-2025",
    "periodo": 2025
  },
  "servicio_sede_id": 45,
  "servicio_sede_detail": {
    "id": 45,
    "codigo": "SRV-001",
    "nombre": "Cirugía General"
  },
  "criterio_id": 23,
  "criterio_detail": {
    "id": 23,
    "codigo": "1.3",
    "nombre": "Competencias y Certificación del Talento Humano",
    "complejidad": "ALTA"
  },
  "cumple": "NO_CUMPLE",
  "cumple_display": "No Cumple",
  "hallazgo": "Personal sin certificación en Reanimación Cardiopulmonar (RCP) actual",
  "plan_mejora": "Programar entrenamiento obligatorio RCP para todos los médicos antes del 30 de Marzo de 2026",
  "responsable_mejora_detail": {
    "id": 8,
    "username": "jefe_talento_humano",
    "email": "jth@hospital.com"
  },
  "fecha_compromiso": "2026-03-30",
  "tiene_plan_mejora": true,
  "mejora_vencida": false,
  "documentos_evidencia_list": [],
  "fecha_creacion": "2026-02-18T15:45:20.123456Z",
  "fecha_actualizacion": "2026-02-18T15:45:20.123456Z"
}
```

---

### **Ejemplo 3: Validar Autoevaluación**

```bash
curl -X POST http://localhost:8000/api/habilitacion/autoevaluaciones/10/validar/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200)**:
```json
{
  "id": 10,
  "numero_autoevaluacion": "AUT-REPS001-2025",
  "datos_prestador_id": 1,
  "datos_prestador_detail": {
    "id": 1,
    "codigo_reps": "REPS001",
    "company_name": "Clínica San José"
  },
  "periodo": 2025,
  "version": 1,
  "estado": "VALIDADA",
  "estado_display": "Validada",
  "fecha_inicio": "2026-01-15",
  "fecha_completacion": "2026-02-18",
  "fecha_vencimiento": "2027-02-18",
  "vigente": true,
  "usuario_responsable_detail": {
    "id": 2,
    "username": "auditor1",
    "email": "auditor@hospital.com"
  },
  "observaciones": "Evaluación exitosa sin observaciones mayores",
  "porcentaje_cumplimiento": 89.5,
  "total_cumplimientos": 80,
  "cumplimientos_data": {
    "total": 80,
    "cumple": 72,
    "no_cumple": 3,
    "parcialmente": 4,
    "no_aplica": 1
  },
  "fecha_creacion": "2026-01-15T09:00:00Z",
  "fecha_actualizacion": "2026-02-18T16:30:45.123456Z"
}
```

---

### **Ejemplo 4: Listar Mejoras Vencidas**

```bash
curl -X GET "http://localhost:8000/api/habilitacion/cumplimientos/mejoras_vencidas/" \
  -H "Authorization: Bearer <TOKEN>"
```

**Response (200)**:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5201,
      "criterio_codigo": "2.1",
      "criterio_nombre": "Infraestructura Física - Señalización",
      "servicio_nombre": "Urgencias",
      "cumple": "NO_CUMPLE",
      "cumple_display": "No Cumple",
      "tiene_plan_mejora": true,
      "fecha_compromiso": "2026-01-30"
    },
    {
      "id": 5234,
      "criterio_codigo": "1.3",
      "criterio_nombre": "Competencias y Certificación",
      "servicio_nombre": "Cirugía General",
      "cumple": "NO_CUMPLE",
      "cumple_display": "No Cumple",
      "tiene_plan_mejora": true,
      "fecha_compromiso": "2026-02-10"
    }
  ]
}
```

---

## Pantallas Recomendadas

### **1. Dashboard Principal**

**Objetivo**: Resumen ejecutivo de habilitaciones

**Componentes**:
- Tarjetas de resumen:
  - Total de IPS habilitadas
  - Total próximas a vencer (0-90 días)
  - Total vencidas
  - Porcentaje promedio de cumplimiento

- Gráficos:
  - Línea temporal: Cumplimiento por período
  - Torta: Distribución por estado (HABILITADA, EN_PROCESO, etc.)
  - Mapa de estados: Por modalidad / complejidad

- Tabla de monitoreo:
  - Prestadores próximos a vencer
  - Últimas autoevaluaciones completadas

**Endpoints**:
```
GET /api/habilitacion/prestadores/proximos_a_vencer/
GET /api/habilitacion/prestadores/vencidas/
GET /api/habilitacion/servicios/proximos_a_vencer/
GET /api/habilitacion/autoevaluaciones/por_completar/
```

---

### **2. Gestión de Prestadores**

**Objetivo**: CRUD y monitoreo de IPS/Prestadores

**Secciones**:
- **Listado**:
  - Tabla con búsqueda avanzada
  - Filtros: estado, clase, vencimiento
  - Acciones: Ver detalle, Editar, Renovar, Eliminar

- **Formulario de Creación/Edición**:
  - Datos principales: REPS, clase, empresa
  - Información de habilitación: fechas, estado
  - Seguros: aseguradora, póliza, vigencia
  
- **Detalle**:
  - Card de información general
  - Indicadores: días para vencer, estado actual
  - Tab de Servicios habilitados
  - Tab de Autoevaluaciones (historial)
  - Acciones: Renovar, Crear autoevaluación
  - Documentos asociados

**Endpoints**:
```
GET /api/habilitacion/prestadores/
POST /api/habilitacion/prestadores/
GET /api/habilitacion/prestadores/{id}/
PUT/PATCH /api/habilitacion/prestadores/{id}/
GET /api/habilitacion/prestadores/{id}/servicios/
GET /api/habilitacion/prestadores/{id}/autoevaluaciones/
POST /api/habilitacion/prestadores/{id}/iniciar_renovacion/
```

---

### **3. Gestión de Servicios**

**Objetivo**: Gestión de servicios habilitados por sede

**Secciones**:
- **Listado**:
  - Tabla: Código, nombre, sede, modalidad, complejidad, estado
  - Filtros multidimensionales
  - Indicador visual: vencimiento cercano

- **Creación**:
  - Seleccionar sede
  - Información del servicio
  - Modalidad y complejidad
  - Fechas de habilitación

- **Detalle**:
  - Información del servicio
  - Cumplimientos asociados
  - Historial de cambios

**Endpoints**:
```
GET /api/habilitacion/servicios/
POST /api/habilitacion/servicios/
GET /api/habilitacion/servicios/{id}/
PUT/PATCH /api/habilitacion/servicios/{id}/
GET /api/habilitacion/servicios/{id}/cumplimientos/
GET /api/habilitacion/servicios/proximos_a_vencer/
GET /api/habilitacion/servicios/por_complejidad/
```

---

### **4. Evaluaciones (Autoevaluaciones)**

**Objetivo**: Completar y monitorear evaluaciones anuales

**Secciones**:
- **Listado**:
  - Estado de evaluaciones actuales
  - Tabla: Prestador, período, versión, porcentaje completitud
  - Filtros: por prestador, estado, período

- **Creación**:
  - Seleccionar prestador
  - Período (año)
  - Fecha de vencimiento
  - Cargar desde anterior (botón "Duplicar")

- **Editor de Evaluación**:
  - Encabezado: Información general
  - Vista de progreso: % completitud
  - Tabla de criterios:
    - Criterio (código + nombre)
    - Servicio aplicable
    - Estado de cumplimiento (CUMPLE, NO_CUMPLE, PARCIALMENTE, NO_APLICA)
    - Hallazgo (textarea expandible)
    - Plan mejora (si NO_CUMPLE)
    - Responsable de mejora
    - Fecha compromiso
  - Evidencia adjunta (documentos)
  - Botones: Guardar borrador, Marcar completada, Validar

- **Resumen**:
  - Card con porcentaje cumplimiento
  - Breakdown: Cumple, No cumple, Parcialmente, No aplica
  - Gráfico de distribución
  - Lista de planes de mejora pendientes
  - Mejoras vencidas (highlighted)

**Endpoints**:
```
GET /api/habilitacion/autoevaluaciones/
POST /api/habilitacion/autoevaluaciones/
GET /api/habilitacion/autoevaluaciones/{id}/
PUT/PATCH /api/habilitacion/autoevaluaciones/{id}/
GET /api/habilitacion/autoevaluaciones/{id}/resumen/
POST /api/habilitacion/autoevaluaciones/{id}/validar/
POST /api/habilitacion/autoevaluaciones/{id}/duplicar/
GET /api/habilitacion/autoevaluaciones/por_completar/
GET /api/normativity/criterios/ (para cargar criterios)
```

---

### **5. Registro de Cumplimientos**

**Objetivo**: Detallar cumplimiento de criterios específicos

**Secciones**:
- **Listado Rápido**:
  - Vista tipo timeline de cumplimientos
  - Estados: Sin completar, Completado, Con mejora
  - Filtros: Por evaluación, por servicio, por estado

- **Detalle de Cumplimiento**:
  - Información del criterio (desde normativity)
  - Evaluación: Resultado (dropdown)
  - Hallazgo: Textarea con observaciones
  - Plan de Mejora: Si NO_CUMPLE:
    - Descripción del plan
    - Responsable (asignación)
    - Fecha compromiso
  - Evidencia: Lista de documentos adjuntos
  - Historial de cambios

- **Panel de Excepciones**:
  - Cumplimientos sin cumplir
  - Mejoras vencidas (CRITICAL)
  - Planes de mejora pendientes

**Endpoints**:
```
GET /api/habilitacion/cumplimientos/
POST /api/habilitacion/cumplimientos/
GET /api/habilitacion/cumplimientos/{id}/
PUT/PATCH /api/habilitacion/cumplimientos/{id}/
GET /api/habilitacion/cumplimientos/sin_cumplir/
GET /api/habilitacion/cumplimientos/con_plan_mejora/
GET /api/habilitacion/cumplimientos/mejoras_vencidas/
```

---

### **6. Reportes y Analytics**

**Objetivo**: Análisis y generación de reportes

**Vistas**:
- **Reporte de Cumplimiento por Período**:
  - Seleccionar autoevaluación
  - Ver desglose por estándar
  - Gráficos de tendencia

- **Comparativa Entre Períodos**:
  - Mejora/deterioro por prestador
  - Benchmarking entre prestadores

- **Alertas**:
  - Habilitaciones próximas a vencer
  - Mejoras vencidas
  - Evaluaciones no iniciadas

**Endpoints**: Combinar múltiples GET con análisis local en frontend

---

## Relaciones entre Entidades

### **Diagrama Relacional**

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA HABILITACION                │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Company    │  (app: companies)
    │  (id, name)  │
    └────────┬─────┘
             │ 1:N
             │
    ┌────────▼──────────────┐
    │  Headquarters (Sede)   │  (app: companies)
    │  (id, company_fk,     │
    │   name, address)      │
    └────────┬───────┬──────┘
             │ 1:1   │ 1:N
             │       │
    ┌────────▼─────────────┐      ┌──────────────────┐
    │  DatosPrestador      │      │  ServicioSede    │
    │  (id, reps_code,     │◄─────┤  (id, sede_fk,  │
    │   clase, estado,     │      │   codigo,        │
    │   vencimiento, etc)  │      │   nombre, etc)   │
    └────────┬─────────────┘      └────────┬─────────┘
             │ 1:N                         │ 1:N
             │                            │
    ┌────────▼───────────────┐  ┌─────────▼──────────────┐
    │  Autoevaluacion        │  │  Cumplimiento          │
    │  (id, prestador_fk,    │  │  (id, autoevaluacion_fk,
    │   periodo, estado,     │  │   servicio_fk,         │
    │   vencimiento, etc)    │  │   criterio_fk,         │
    └────────┬───────────────┘  │   resultado,           │
             │ 1:N                 │   plan_mejora, etc)    │
             │                    └────────┬────────────────┘
             │                             │ N:1
             └──────────────────┬──────────┘
                                │
                         ┌──────▼──────┐
                         │  Criterio   │  (app: normativity)
                         │ (id, codigo,│
                         │  nombre)    │
                         └─────────────┘

TAMBIÉN:
- Cumplimiento → Documento (M:N) para archivos de evidencia
- Cumplimiento → User (N:1) responsable de mejora
- Autoevaluacion → User (N:1) responsable/auditor
- DatosPrestador → User (N:1) creador/responsable
```

---

### **Claves Relacionales**

| De | Hacia | Tipo | Campo FK | Relación |
|---|---|------|----------|----------|
| DatosPrestador | Headquarters | 1:1 | headquarters_id | OneToOneField |
| DatosPrestador | Company | Implícito | por Headquarters | Vía Headquarters |
| DatosPrestador | User | N:1 | usuario_responsable_id | ForeignKey |
| ServicioSede | Headquarters | N:1 | sede_id | ForeignKey |
| Autoevaluacion | DatosPrestador | N:1 | datos_prestador_id | ForeignKey |
| Autoevaluacion | User | N:1 | usuario_responsable_id | ForeignKey |
| Cumplimiento | Autoevaluacion | N:1 | autoevaluacion_id | ForeignKey |
| Cumplimiento | ServicioSede | N:1 | servicio_sede_id | ForeignKey |
| Cumplimiento | Criterio | N:1 | criterio_id | ForeignKey |
| Cumplimiento | User | N:1 | responsable_mejora_id | ForeignKey |
| Cumplimiento | Documento | N:M | documentos_evidencia | ManyToManyField |

---

## Información Adicional para Desarrollo Frontend

### **Patrones de Paginación**

Todos los endpoints de listado usan paginación con 20 elementos por página:

```
GET /api/habilitacion/prestadores/?page=1
GET /api/habilitacion/prestadores/?page=2
```

**Response**:
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/habilitacion/prestadores/?page=2",
  "previous": null,
  "results": [...]
}
```

---

### **Búsqueda y Filtrado**

**Búsqueda** (search):
```
GET /api/habilitacion/prestadores/?search=REPS
```

**Filtrado** (filterset_fields):
```
GET /api/habilitacion/prestadores/?estado_habilitacion=HABILITADA&clase_prestador=IPS
```

**Ordenamiento**:
```
GET /api/habilitacion/prestadores/?ordering=-fecha_vencimiento_habilitacion
GET /api/habilitacion/prestadores/?ordering=fecha_creacion
```

---

### **Códigos de Error HTTP**

| Código | Significado | Ejemplo |
|--------|------------|---------|
| 200 | OK - Operación exitosa | GET exitoso |
| 201 | CREATED - Recurso creado | POST exitoso |
| 204 | NO CONTENT - Eliminado | DELETE exitoso |
| 400 | BAD REQUEST - Datos inválidos | Validación fallida |
| 401 | UNAUTHORIZED - Falta token | Sin JWT |
| 403 | FORBIDDEN - Sin permisos | Usuario no autorizado |
| 404 | NOT FOUND - No existe | ID no encontrado |
| 409 | CONFLICT - Violación única | código_reps duplicado |
| 500 | SERVER ERROR | Error interno servidor |

---

### **Validaciones Importantes**

**DatosPrestador**:
- `codigo_reps`: Único, mín 5 caracteres
- `fecha_vencimiento_habilitacion`: Debe ser mayor que hoy
- `clase_prestador`: Debe ser una de las opciones válidas

**ServicioSede**:
- `codigo_servicio` + `sede_id`: Combinación única
- `fecha_vencimiento`: Debe ser mayor que `fecha_habilitacion`

**Autoevaluacion**:
- `datos_prestador` + `periodo` + `version`: Son únicos juntos
- `fecha_vencimiento`: Obligatoria

**Cumplimiento**:
- `autoevaluacion` + `servicio_sede` + `criterio`: Combinación única
- Si `cumple` = "NO_CUMPLE": Requiere `plan_mejora` y `fecha_compromiso`

---

### **Campos Calculados (Solo Lectura)**

En los serializers se incluyen campos calculados que NO se envían en PUT/POST:

- `dias_vencimiento`: Días para vencimiento
- `proxima_vencer`: Boolean si vence en 90 días
- `vencida`: Boolean si ya venció
- `porcentaje_cumplimiento`: % de cumplimiento
- `total_cumplimientos`: Número de cumplimientos
- `cumplimientos_data`: Desglose por estado
- `estado_display`: Label del estado
- `responsable_mejora_detail`: Objeto usuario simplificado

---

### **Recomendaciones de UI/UX**

1. **Fecha de Vencimiento**:
   - Verde: > 180 días
   - Amarillo: 90-180 días
   - Naranja: 30-90 días
   - Rojo: < 30 días o vencido

2. **Indicadores**:
   - Mostrar "Próxima a vencer" en rojo si está en los 90 días
   - Mostrar "Vencida" en rojo si ya pasó

3. **Acciones Contextuales**:
   - Mostrar "Renovar" (POST /iniciar_renovacion) si estado = HABILITADA y próximo a vencer
   - Mostrar "Crear Autoevaluación" si la actual está validada

4. **Validaciones en Frontend**:
   - Habilitar "Validar" autoevaluación solo si todos los cumplimientos están evaluados
   - Permitir "Duplicar" desde cualquier autoevaluación completada
   - Requerir plan mejora si resultado = NO_CUMPLE

5. **Monitoreo**:
   - Resaltar mejoras vencidas en tablas (fondo rojo)
   - Mostrar contador de tareas pendientes en navbar
   - Breadcrumbs claros: Prestador > Autoevaluación > Cumplimiento

---

### **Integraciones Externas**

El módulo habilitacion se relaciona con:

- **companies**: Para obtener sede (Headquarters) y empresa (Company)
- **normativity**: Para cargar criterios disponibles por estándar
- **processes**: Para adjuntar Documentos como evidencia
- **users**: Para asignar responsables y auditores
- **audit**: Para registrar cambios importantes (opcional)

---

## Resumen de Stack Técnico Recomendado para Frontend

**Framework**: React 18+ con TypeScript

**Librerías**:
- `react-query` o `@tanstack/react-query`: Cache HTTP y sincronización
- `axios`: Cliente HTTP
- `zod` o `yup`: Validación de formularios
- `react-hook-form`: Gestión de formularios
- `tailwindcss`: Estilos
- `zustand` o `recoil`: State management
- `react-router-v6`: Navegación
- `recharts` o `chart.js`: Gráficos
- `react-table`: Tablas avanzadas
- `date-fns` o `dayjs`: Manejo de fechas
- `react-toastify` o `sonner`: Notificaciones

---

**Fin del documento**

---

## Historial de Cambios

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2026-02-18 | 1.0 | Documento inicial completo |

