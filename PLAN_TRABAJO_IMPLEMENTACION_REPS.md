# Plan de Trabajo - Implementacion REPS y Cumplimiento Normativo

## Objetivo General
Cerrar brechas funcionales y tecnicas para alinear el backend con lineamientos de habilitacion (Resolucion 3100/2019, lineamientos de verificacion 2021 y Anexo 2), priorizando estabilidad, trazabilidad documental y cobertura de dominios REPS.

## Alcance
- Apps objetivo: habilitacion, mejoras, normativity.
- Integracion soporte documental: app processes.
- Entregables de codigo: modelos, serializers, views, urls, migraciones y documento de arquitectura.

## Estado de Ejecucion (Marzo 2026)
- Bloque A: completado y estabilizado.
- Bloque B: completado con APIs CRUD expuestas y operativas.
- Bloque C: completado funcionalmente y en fortalecimiento de cobertura normativa y pruebas API.
- Auditoria tecnica rapida: ejecutada, con hallazgos menores y acciones correctivas aplicadas.

## Bloque A - Correcciones Criticas de Codigo Actual
### Actividades
1. Corregir errores de runtime en vistas de habilitacion.
2. Corregir filtros y busquedas con rutas ORM incorrectas.
3. Homologar estados de documentos para evitar inconsistencia de evidencias.
4. Corregir endpoints de documentos con metodos mal anidados.

### Criterios de aceptacion
- No errores de compilacion en archivos intervenidos.
- Endpoints de documento y evidencias accesibles.
- Consulta de prestadores funcional por busqueda.

### Estado
- Implementado en esta iteracion.

## Bloque B - Modelo de Datos REPS Extendido
### Actividades
1. Agregar entidad de capacidad instalada por servicio.
2. Agregar entidad de medidas de seguridad por servicio.
3. Agregar entidad de sanciones por servicio.
4. Agregar entidad de novedades REPS para prestador/sede/servicio/capacidad.
5. Exponer APIs CRUD con filtros y ordenamiento.

### Criterios de aceptacion
- Modelos persistidos con migracion.
- Endpoints registrados en router de habilitacion.
- Relacionamiento con servicio/prestador validado por FK.

### Estado
- Implementado en esta iteracion.

## Bloque C - Motor Documental de Verificacion (Anexo 2)
### Actividades
1. Crear catalogo de requisitos documentales por tipo de tramite/visita.
2. Crear checklist de verificacion por novedad.
3. Crear items por requisito con resultado de verificacion.
4. Crear evidencias adjuntas por item con cargue de archivos.
5. Exponer APIs CRUD y endpoint de avance de checklist.

### Criterios de aceptacion
- Modelo trazable de requisito -> item -> evidencia.
- Upload de soportes habilitado por API.
- Estado y avance de checklist consultables.

### Estado
- Implementado y endurecido en esta iteracion.
- Se agrego seleccion de requisitos por combinacion de tipo/subtipo de novedad.
- Se amplio el seed documental hacia una matriz extendida por grupos regulatorios.

## Bloque D - Endurecimiento Reglas de Negocio por Subtipo
### Actividades
1. Mapear subtipos de novedad a reglas documentales especificas.
2. Permitir combinacion de tramites cuando aplique (NOVEDAD + visita).
3. Limitar requisitos de NOVEDAD por prefijos para subtipos especificos.
4. Mantener compatibilidad sin cambios de esquema para no romper migraciones.

### Criterios de aceptacion
- APERTURA_MODALIDAD incluye base NOVEDAD y VISITA_CERTIFICACION.
- REACTIVACION incluye base NOVEDAD y VISITA_REACTIVACION.
- requiere_visita_previa agrega VISITA_PREVIA sin perder base NOVEDAD.
- CAMBIO_CONTACTO/CIERRE/CAMBIO_HORARIO/CAMBIO_COMPLEJIDAD/TRASLADO filtran requisitos de novedad por familia.

### Estado
- Implementado.

## Bloque E - Regresion API de Endpoints Nuevos
### Actividades
1. Probar creacion de novedad REPS.
2. Probar creacion de checklist y avance.
3. Probar actualizacion de checklist item con verificador automatico.
4. Probar cargue de evidencias y validacion de extensiones.
5. Probar endpoints de mejoras en cumplimiento (con_plan_mejora y mejoras_vencidas).

### Criterios de aceptacion
- Todas las pruebas API nuevas en verde en ejecucion local.
- Validacion de extensiones rechaza archivos no permitidos.
- Endpoints de mejoras siguen respondiendo correctamente.

### Estado
- En ejecucion y validacion.

## Bloque F - Auditoria Tecnica Rapida de Consistencia
### Hallazgos
1. Se detectaron cambios amplios en varios modulos (habilitacion y processes) que requerian validacion de no-regresion.
2. Se confirmo ausencia de errores estaticos en archivos clave tras cambios.
3. Se detecto oportunidad de limpieza menor en imports dentro de clase en processes/views.

### Acciones
1. Ejecutar check de Django y pruebas focalizadas de regresion.
2. Consolidar pruebas de endpoints nuevos para evitar regresiones futuras.
3. Registrar observaciones de consistencia y mantener seguimiento de deuda tecnica menor.

## Orden de Ejecucion Aplicado
1. Estabilizacion tecnica (Bloque A).
2. Expansion del dominio REPS (Bloque B).
3. Motor documental y trazabilidad (Bloque C).
4. Validacion tecnica y migraciones.

## Riesgos y mitigaciones
- Riesgo: crecimiento de complejidad del dominio.
  - Mitigacion: separar modelos por subdominio y exponer endpoints por recurso.
- Riesgo: inconsistencias de catalogo normativo.
  - Mitigacion: mantener catalogo de requisitos versionable y activo/inactivo.
- Riesgo: carga documental heterogenea.
  - Mitigacion: validacion de extensiones y ruta de almacenamiento estructurada.

## Siguientes hitos recomendados
1. Completar consolidacion 1:1 final contra matriz oficial validada por negocio/juridico.
2. Añadir pruebas de integracion cruzada con app mejoras (planes y hallazgos) para escenarios mixtos.
3. Implementar reporte de brechas documentales por novedad y subtipo.
4. Normalizar observaciones de estilo/estructura en archivos no criticos (deuda tecnica menor).
