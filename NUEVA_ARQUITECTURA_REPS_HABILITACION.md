# Nueva Arquitectura - Habilitacion REPS

## Vision
La arquitectura se organiza en tres capas funcionales:
1. Dominio transaccional de habilitacion y autoevaluacion.
2. Dominio regulatorio REPS extendido (capacidad, medidas, sanciones, novedades).
3. Motor documental de verificacion para Anexo 2 con evidencia auditable.

## Mapa de componentes
- habilitacion.models
  - DatosPrestador
  - ServicioSede
  - Autoevaluacion
  - Cumplimiento
  - CapacidadInstalada
  - MedidaSeguridadServicio
  - SancionServicio
  - NovedadREPS
  - RequisitoDocumental
  - ChecklistVerificacion
  - ChecklistItem
  - EvidenciaChecklist
- habilitacion.serializers
  - Serializers CRUD para todos los recursos anteriores.
- habilitacion.views
  - ViewSets CRUD y acciones de resumen/avance.
- habilitacion.urls
  - Endpoints versionados bajo /api/habilitacion/.
- processes
  - Repositorio de documentos institucionales y versionamiento.
- mejoras
  - Ciclo de mejora y hallazgos conectado con cumplimiento.
- normativity
  - Catalogo maestro de estandares y criterios.

## Relaciones clave
- DatosPrestador 1..N ServicioSede
- DatosPrestador 1..N NovedadREPS
- ServicioSede 1..N CapacidadInstalada
- ServicioSede 1..N MedidaSeguridadServicio
- ServicioSede 1..N SancionServicio
- NovedadREPS 1..N ChecklistVerificacion
- ChecklistVerificacion 1..N ChecklistItem
- ChecklistItem 1..N EvidenciaChecklist
- Autoevaluacion + ServicioSede + Criterio -> Cumplimiento
- Cumplimiento <-> Documento (M2M) para evidencia funcional

## Endpoints nuevos incorporados
- /api/habilitacion/capacidades/
- /api/habilitacion/medidas-seguridad/
- /api/habilitacion/sanciones/
- /api/habilitacion/novedades-reps/
- /api/habilitacion/requisitos-documentales/
- /api/habilitacion/checklists-verificacion/
- /api/habilitacion/checklist-items/
- /api/habilitacion/evidencias-checklist/

## Flujo principal de negocio
1. Prestador crea/actualiza novedad REPS.
2. Sistema asocia checklist documental segun tipo de tramite.
3. Verificador diligencia items y registra cumplimiento.
4. Prestador/verificador carga evidencias por item.
5. API calcula avance y cierre de checklist.
6. Estado de novedad evoluciona hasta aplicada en REPS.

## Endurecimiento por subtipo (Marzo 2026)
- Seleccion de requisitos por combinacion de tipos de tramite:
  - PRESTADOR -> INSCRIPCION.
  - APERTURA_MODALIDAD -> NOVEDAD + VISITA_CERTIFICACION.
  - REACTIVACION -> NOVEDAD + VISITA_REACTIVACION.
  - requiere_visita_previa=true -> agrega VISITA_PREVIA.
- Filtro de familia documental por subtipo de novedad (prefijos de codigo):
  - CAMBIO_CONTACTO -> NOV-BAS + NOV-CON.
  - CIERRE_MODALIDAD -> NOV-BAS + NOV-CM.
  - CAMBIO_HORARIO -> NOV-BAS + NOV-HOR.
  - CAMBIO_COMPLEJIDAD -> NOV-BAS + NOV-CC.
  - TRASLADO_SERVICIO -> NOV-BAS + NOV-TS.
  - OTRA -> NOV-BAS.

## Cobertura de regresion API (Marzo 2026)
- Se agregan pruebas de regresion para:
  - Creacion de novedad REPS.
  - Creacion de checklist, autogeneracion de items y endpoint de avance.
  - Actualizacion de checklist item con verificador automatico.
  - Cargue de evidencias (multipart) y rechazo de extensiones no permitidas.
  - Endpoints de cumplimiento: con_plan_mejora y mejoras_vencidas.

## Consideraciones de cumplimiento
- Trazabilidad completa por timestamps y usuario en recursos criticos.
- Soportes con validacion de extension y almacenamiento segregado por checklist.
- Catalogo de requisitos activo/inactivo para versionado normativo.

## Gobernanza y evolucion
- Mantener seeds de RequisitoDocumental por version normativa.
- Incorporar reglas de validacion por subtipo de novedad (visita previa, documentos obligatorios).
- Crear reportes de auditoria por estado de novedad y brechas documentales.
