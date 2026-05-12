# Bitácora de Correcciones — Phase-0

Rama: `feature/phase-0`
Objetivo: Corregir bugs identificados en apps companies, habilitacion, soportes, mejoras y audit.

---

## 1. Companies

### 1.1 Modelos

**Archivo:** `companies/models/parameters.py`

- **`Region`**: agregado `class Meta` con `verbose_name`, `verbose_name_plural`, `ordering`.
- **`Municipality`**: 
  - Agregado `class Meta` con `verbose_name`, `verbose_name_plural`, `ordering`, `unique_together = [["region", "code"]]`.
  - Cambiado `on_delete=models.CASCADE` → `on_delete=models.PROTECT` en FK `region`.
  - Cambiado `related_name='Departamento'` → `related_name='municipalities'`.

**Archivo:** `companies/models/company.py`

- Cambiado `on_delete=models.CASCADE` → `on_delete=models.PROTECT` en FK `region`.
- Cambiado `on_delete=models.CASCADE` → `on_delete=models.PROTECT` en FK `municipality`.
- Cambiado `related_name='departamentos'` → `related_name='companies'` en FK `region`.
- Cambiado `related_name='municipios'` → `related_name='companies'` en FK `municipality`.

### 1.2 Vistas

**Archivo:** `companies/views/process_view.py`

- Eliminado método `create()` duplicado (el segundo sobreescribía al primero).
- Eliminados métodos redundantes `list()`, `retrieve()`, `create()`, `update()`, `destroy()` que `ModelViewSet` ya implementa.
- Limpiados imports no utilizados.

**Archivo:** `companies/views/process_type_view.py**

- Mismos cambios que `process_view.py`.

**Archivo:** `companies/views/company_view.py`

- Eliminados métodos redundantes `get_queryset()`, `list()`, `retrieve()`, `create()`, `update()`, `destroy()`.
- Agregado endpoint `deactivate` (simétrico a `activate` existente).
- Limpiados imports no utilizados.

**Archivo:** `companies/views/headquarters_view.py`

- Eliminados métodos redundantes.
- Limpiados imports.

**Archivo:** `companies/views/departament_view.py` (renombrado a `department_view.py`)

- Eliminados métodos redundantes.
- Limpiados imports.
- Renombrado archivo: `departament_view.py` → `department_view.py` (ortografía correcta).
- Actualizado import en `views/__init__.py`.

### 1.3 Archivos huérfanos eliminados

- `companies/admin soprtes`
- `companies/url soportes`
- `companies/views/soportes`
- `companies/serializers/soportes`

### 1.4 Migración

- `companies/migrations/0003_alter_municipality_options_alter_region_options_and_more.py`

---

## 2. Habilitación

### 2.1 Modelos

**`capacidadInstalada.py`**: `servicio_sede` FK: `CASCADE` → `PROTECT`.

**`medidaSeguridadServicio.py`**: `servicio_sede` FK: `CASCADE` → `PROTECT`.

**`sancionServicio.py`**: `servicio_sede` FK: `CASCADE` → `PROTECT`.

**`novedadREPS.py`**: `datos_prestador` FK: `CASCADE` → `PROTECT`.

**`checklistVerificacion.py`**: `novedad` FK: `CASCADE` → `PROTECT`.

**`cumplimiento.py`**: Eliminadas funciones duplicadas y muertas (`checklist_upload_path`, `validate_checklist_extension`, `ALLOWED_CHECKLIST_EXTENSIONS`) que ya existían en `checklistItem.py`. Limpiados imports no utilizados (`os`, `uuid`, `ValidationError`).

Se mantuvo `CASCADE` en:
- `EvidenciaChecklist.checklist_item` (relación padre-hijo directa)
- `ChecklistItem.checklist` (relación padre-hijo directa)

### 2.2 Migración

- `habilitacion/migrations/0003_alter_capacidadinstalada_servicio_sede_and_more.py`

---

## 3. Soportes

### 3.1 Modelos

**`SoporteDocumental`**:
- `prestador` FK: `CASCADE` → `PROTECT`
- `empresa` FK: `CASCADE` → `PROTECT`
- `sede` FK: `CASCADE` → `PROTECT`
- `servicio` FK: `CASCADE` → `PROTECT`

**`SoporteRequerido`**:
- `prestador` FK: `CASCADE` → `PROTECT`
- `empresa` FK: `CASCADE` → `PROTECT`
- `sede` FK: `CASCADE` → `PROTECT`
- `servicio` FK: `CASCADE` → `PROTECT`
- `tipo_documento` FK: `CASCADE` → `PROTECT`

### 3.2 Migración

- `soportes/migrations/0002_alter_soportedocumental_empresa_and_more.py`

---

## 4. Mejoras

### 4.1 Modelos

**`PlanMejora`**:
- `cumplimiento` FK: `CASCADE` → `PROTECT`
- `autoevaluacion` FK: `CASCADE` → `PROTECT`
- `auditoria` FK: `CASCADE` → `PROTECT`
- `resultado_indicador` FK: `CASCADE` → `PROTECT`

**`Hallazgo`**:
- `autoevaluacion` FK: `CASCADE` → `PROTECT`
- `datos_prestador` FK: `CASCADE` → `PROTECT`
- `auditoria` FK: `CASCADE` → `PROTECT`
- `resultado_indicador` FK: `CASCADE` → `PROTECT`

Se mantuvo `CASCADE` en `SoportePlan.plan_mejora` (relación padre-hijo).

### 4.2 Migración

- `mejoras/migrations/0003_alter_hallazgo_auditoria_and_more.py`

---

## 5. Audit

### 5.1 Modelos

**`MiembroEquipoAuditor`**:
- `usuario` FK: `CASCADE` → `SET_NULL` (si se elimina un usuario, se preserva el registro histórico del miembro del equipo).

### 5.2 Migración

- `audit/migrations/0003_alter_miembroequipoauditor_usuario.py`

---

## Resumen de cambios

| App | Archivos modificados | Migraciones generadas |
|------|----------------------|----------------------|
| companies | 10 | 1 |
| habilitacion | 6 | 1 |
| soportes | 1 | 1 |
| mejoras | 1 | 1 |
| audit | 1 | 1 |
| **Total** | **19** | **5** |

## Verificación

- `python manage.py check` → 0 errores (solo warnings de seguridad de Django esperados en desarrollo).
- Todos los endpoints API responden (200/401).
- Migraciones aplicadas en orden en base SQLite.
