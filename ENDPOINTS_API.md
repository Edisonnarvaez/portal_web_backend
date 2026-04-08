# Endpoints API - Portal Web Backend

Inventario consolidado de endpoints expuestos actualmente por el backend.
Fuente: rutas registradas en `backend/urls.py`, `*/urls.py`, routers DRF y acciones `@action` en ViewSets.

## Base URL

- Desarrollo: `http://127.0.0.1:8000`

## Endpoints Globales

- `POST /api/token/`
- `POST /api/token/refresh/`
- `GET|POST|PUT|PATCH|DELETE /admin/` (Django Admin web)

## Convencion CRUD de recursos router (DRF)

Para cada recurso registrado en router:

- `GET /api/{app}/{recurso}/`
- `POST /api/{app}/{recurso}/`
- `GET /api/{app}/{recurso}/{id}/`
- `PUT /api/{app}/{recurso}/{id}/`
- `PATCH /api/{app}/{recurso}/{id}/`
- `DELETE /api/{app}/{recurso}/{id}/`

## Users (`/api/users/`)

- `POST /api/users/login/`
- `POST /api/users/verify-otp/`
- `GET|POST /api/users/roles/`
- `GET /api/users/users/`
- `GET|PATCH /api/users/me/`
- `POST /api/users/2fa/enable/`
- `POST /api/users/2fa/verify/`
- `POST /api/users/2fa/toggle/`
- `POST /api/users/password-reset/`
- `POST /api/users/password-reset-confirm/{user_id}/{token}/`
- `POST /api/users/change-password/`

## Companies (`/api/companies/`)

Recursos CRUD:

- `companies`
- `departments`
- `headquarters`
- `process_types`
- `processes`
- `regions`
- `municipalities`

Acciones personalizadas:

- `POST /api/companies/companies/{id}/activate/`

## Processes (`/api/processes/`)

Recurso CRUD:

- `documentos`

Acciones personalizadas:

- `GET /api/processes/documentos/{id}/preview/`
- `GET /api/processes/documentos/{id}/download/`

## Main (`/api/main/`)

Recursos CRUD:

- `funcionarios`
- `contenidos`
- `eventos`
- `felicitaciones`
- `reconocimientos`

Acciones personalizadas:

- `GET /api/main/felicitaciones/cumpleanos-mes-actual/`
- `GET /api/main/felicitaciones/cumpleanos-hoy/`
- `GET /api/main/reconocimientos/publicados/`
- `GET /api/main/reconocimientos/no-publicados/`

## Indicators (`/api/indicators/`)

Recursos CRUD:

- `indicators`
- `results`

Acciones personalizadas:

- `GET /api/indicators/results/detailed/`

## Normativity (`/api/normativity/`)

Recursos CRUD:

- `estandares`
- `criterios`
- `documentos-normativos`

Acciones personalizadas:

- `GET /api/normativity/estandares/todos/`
- `GET /api/normativity/estandares/{id}/criterios/`
- `GET /api/normativity/criterios/por-complejidad/`
- `GET /api/normativity/criterios/mandatorios/`
- `GET /api/normativity/criterios/con-evidencia/`
- `GET /api/normativity/documentos-normativos/{id}/criterios/`

## Habilitacion (`/api/habilitacion/`)

Recursos CRUD:

- `prestadores`
- `servicios`
- `autoevaluaciones`
- `cumplimientos`
- `capacidades`
- `medidas-seguridad`
- `sanciones`
- `novedades-reps`
- `requisitos-documentales`
- `checklists-verificacion`
- `checklist-items`
- `evidencias-checklist`

Acciones personalizadas:

### Prestadores
- `GET /api/habilitacion/prestadores/proximos-a-vencer/`
- `GET /api/habilitacion/prestadores/vencidas/`
- `GET /api/habilitacion/prestadores/{id}/servicios/`
- `GET /api/habilitacion/prestadores/{id}/autoevaluaciones/`
- `POST /api/habilitacion/prestadores/{id}/iniciar-renovacion/`

### Servicios
- `GET /api/habilitacion/servicios/proximos-a-vencer/`
- `GET /api/habilitacion/servicios/por-complejidad/`
- `GET /api/habilitacion/servicios/{id}/cumplimientos/`

### Autoevaluaciones
- `GET /api/habilitacion/autoevaluaciones/por-completar/`
- `GET /api/habilitacion/autoevaluaciones/{id}/resumen/`
- `POST /api/habilitacion/autoevaluaciones/{id}/validar/`
- `POST /api/habilitacion/autoevaluaciones/{id}/duplicar/`

### Cumplimientos
- `GET /api/habilitacion/cumplimientos/servicios-de-autoevaluacion/`
- `GET /api/habilitacion/cumplimientos/sin-cumplir/`
- `GET /api/habilitacion/cumplimientos/con-plan-mejora/`
- `GET /api/habilitacion/cumplimientos/mejoras-vencidas/`

### Checklists
- `GET /api/habilitacion/checklists-verificacion/{id}/avance/`

## Soportes (`/api/soportes/`)

Recursos CRUD:

- `categorias`
- `tipos-documento`
- `documentos`

Acciones personalizadas:

- No hay acciones `@action` expuestas actualmente.

## Mejoras (`/api/mejoras/`)

Recursos CRUD:

- `planes-mejora`
- `hallazgos`

Acciones personalizadas:

### Planes de mejora
- `GET /api/mejoras/planes-mejora/vencidos/`
- `GET /api/mejoras/planes-mejora/proximos-vencer/`
- `GET /api/mejoras/planes-mejora/resumen/`
- `GET /api/mejoras/planes-mejora/por-origen/`
- `GET /api/mejoras/planes-mejora/{id}/soportes/`
- `POST /api/mejoras/planes-mejora/{id}/soportes/`
- `DELETE /api/mejoras/planes-mejora/{id}/soportes/{soporte_id}/`

### Hallazgos
- `GET /api/mejoras/hallazgos/estadisticas/`
- `GET /api/mejoras/hallazgos/por-origen/`
- `GET /api/mejoras/hallazgos/sin-plan/`

## Audit (`/api/audit/`)

Recursos CRUD:

- `auditorias`
- `entidades`
- `tipos`
- `hallazgos`
- `actas`
- `programas`

Acciones personalizadas:

### Auditorias
- `POST /api/audit/auditorias/{id}/cambiar-fase/`
- `GET /api/audit/auditorias/{id}/equipo/`
- `POST /api/audit/auditorias/{id}/equipo/`
- `DELETE /api/audit/auditorias/{id}/equipo/{miembro_id}/`
- `GET /api/audit/auditorias/{id}/actas/`
- `POST /api/audit/auditorias/{id}/actas/`
- `GET /api/audit/auditorias/resumen/`
- `GET /api/audit/auditorias/proximas/`
- `GET /api/audit/auditorias/por-fase/`

### Hallazgos de auditoria
- `GET /api/audit/hallazgos/vencidos/`
- `GET /api/audit/hallazgos/estadisticas/`

## Nota de mantenimiento

Cuando se agreguen nuevos ViewSets o acciones `@action`, actualizar este archivo en el mismo PR para evitar drift documental.
