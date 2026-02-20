# Portal Web Backend

## Descripción del Proyecto

Portal Web Backend es un sistema de gestión integral desarrollado en Django que proporciona una API REST completa para la gestión de proveedores, facturación electrónica, auditorías, indicadores y procesos organizacionales. El sistema está diseñado para empresas que requieren un control detallado de sus operaciones comerciales y administrativas.

### Características Principales

- 🏢 **Gestión de Empresas y Sedes**: Control completo de información corporativa
- 🏥 **Habilitación de Servicios de Salud (SUH)**: Sistema completo para cumplimiento de Resolución 3100/2019
- � **Planes de Mejora y Hallazgos**: App transversal de mejoras con ciclo PHVA, soportes adjuntos y trazabilidad por origen
- 📋 **Sistema de Auditoría**: Ciclo de vida completo (PROGRAMADA → CERRADA), equipo auditor, hallazgos, actas y programas
- 📈 **Indicadores de Gestión**: Sistema de métricas y reportes
- 👥 **Gestión de Usuarios**: Sistema de autenticación JWT con roles y permisos
- 🔒 **Autenticación 2FA**: Seguridad adicional con autenticación de dos factores
- 📧 **Notificaciones por Email**: Sistema automatizado de notificaciones
- 📁 **Upload de Archivos**: Soportes PDF, Word, PNG, Excel con validación y nombres únicos

## Tecnologías Utilizadas

### Backend
- **Django 5.2.2**: Framework web principal
- **Django REST Framework 3.16.0**: API REST
- **django-filter 25.2**: Filtrado avanzado en APIs
- **JWT Authentication**: Autenticación mediante tokens
- **SQLite/PostgreSQL**: Base de datos (configurable)
- **Waitress**: Servidor WSGI para producción

### Infraestructura
- **WhiteNoise**: Servir archivos estáticos
- **CORS Headers**: Configuración de CORS para frontend
- **python-dotenv**: Gestión de variables de entorno

## Estructura del Proyecto

```
portal_web_backend/
├── backend/                    # Configuración principal de Django
├── users/                      # Gestión de usuarios y autenticación
├── companies/                  # Gestión de empresas y departamentos
├── indicators/                 # Sistema de indicadores y métricas
├── processes/                  # Gestión de procesos y documentos
├── main/                       # Funcionalidades principales
├── normativity/                # Master data - Estándares y Criterios (Resolución 3100)
├── habilitacion/               # Habilitación de Servicios de Salud (SUH)
│   ├── models.py               # DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento
│   ├── serializers.py          # Serializers con integración mejoras
│   ├── views.py                # ViewSets con acciones personalizadas
│   └── urls.py                 # Rutas API
├── mejoras/                    # Planes de Mejora y Hallazgos (transversal)
│   ├── models.py               # PlanMejora, Hallazgo, SoportePlan
│   ├── serializers.py          # List/Detail/CreateUpdate + SoportePlan
│   ├── views.py                # ViewSets con soportes, estadísticas
│   ├── admin.py                # Admin con inlines
│   └── urls.py                 # planes-mejora/, hallazgos/
├── audit/                      # Sistema de Auditoría (ciclo de vida completo)
│   ├── models/                 # Auditoria, MiembroEquipo, HallazgoAuditoria, Acta, Programa
│   ├── serializers/            # List/Detail/CreateUpdate por entidad
│   ├── views/                  # ViewSets con cambiar-fase, equipo, actas
│   └── urls.py                 # auditorias/, hallazgos/, actas/, programas/, tipos/, entidades/
├── media/                      # Archivos multimedia
│   ├── SoportesPlanes/         # Soportes de planes de mejora
│   ├── documentos/             # Documentos de procesos
│   └── profile_pics/           # Fotos de perfil
├── staticfiles/                # Archivos estáticos
├── documentos.md               # 📖 Guía completa para frontend
├── architecture.md             # 🏗️ Arquitectura técnica del sistema
├── readme.md                   # Este archivo
├── requirements.txt            # Dependencias del proyecto
├── manage.py                   # Gestor de Django
├── Portal_Habilitacion_API_completo.postman_collection.json # Postman Collection
└── run_waitress.py            # Script para iniciar servidor Waitress
```

## Instalación y Configuración

### Requisitos Previos
- Python 3.12.10 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Edisonnarvaez/portal_web_backend.git
cd portal_web_backend
```

2. **Crear entorno virtual**
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python -m venv env
source env/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Instalar django-filter (si no está en requirements)**
```bash
pip install django-filter
```

5. **Configurar variables de entorno**
Crear archivo `.env` en la raíz del proyecto:
```env
DJANGO_SECRET_KEY=tu_clave_secreta_aqui
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_de_aplicacion
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

5. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Cargar datos de estándares (Resolución 3100)**
```bash
python cargar_estandares.py
```

7. **Crear superusuario (opcional)**
```bash
python manage.py createsuperuser
```

8. **Ejecutar el servidor**
```bash
# Desarrollo
python manage.py runserver

# Producción con Waitress
python run_waitress.py
```

El servidor estará disponible en:
- **Desarrollo**: `http://127.0.0.1:8000`
- **Producción**: `http://127.0.0.1:8081`

## Configuración de Base de Datos

### SQLite (Por defecto)
El proyecto viene configurado para usar SQLite por defecto, ideal para desarrollo.

### PostgreSQL (Producción recomendada)
Para usar PostgreSQL, descomenta y configura las siguientes líneas en `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}
```

Agregar a tu `.env`:
```env
POSTGRES_DB=nombre_base_datos
POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Módulos del Sistema

### 1. Gestión de Usuarios (`users/`)
- Autenticación JWT
- Roles y permisos
- Autenticación de dos factores (2FA)
- Recuperación de contraseña por email
- Perfiles de usuario

### 2. Gestión de Empresas (`companies/`)
- Información de empresas
- Departamentos organizacionales
- Sedes y sucursales
- Tipos de procesos
- Procesos empresariales

### 3. Indicadores (`indicators/`)
- Creación de indicadores
- Resultados y métricas
- Reportes por sede

### 4. Procesos (`processes/`)
- Gestión de documentos
- Subida de archivos
- Control de procesos

### 5. Sistema de Normativity (`normativity/`)
- Estándares de Resolución 3100/2019
- 7 Estándares: Talento Humano, Infraestructura, Dotación, Procesos, Recurso Sanguíneo, Gestión Integral, Seguridad
- 21 Criterios de evaluación (3 por estándar)
- Documentos normativos de referencia
- **Endpoints**: `/api/normativity/estandares/`, `/api/normativity/criterios/`, `/api/normativity/documentos/`

### 6. Habilitación de Servicios (`habilitacion/`)

**Módulo Completo de Habilitación de Servicios Unificados (SUH)**

Sistema completo para gestión de habilitación de Instituciones Prestadoras de Servicios (IPS) y prestadores individuales según Resolución 3100/2019 de Colombia.

#### **Modelos Principales**:

1. **DatosPrestador** - Información de habilitación
   - Código REPS único
   - Clase de prestador (IPS, PROF, PH, PJ)
   - Estado de habilitación (HABILITADA, EN_PROCESO, SUSPENDIDA, NO_HABILITADA, CANCELADA)
   - Fechas de inscripción, renovación y vencimiento
   - Información de seguros (aseguradora, póliza, vigencia)
   - Relación OneToOne con Headquarters (Sede)

2. **ServicioSede** - Servicios de salud por sede
   - Código del servicio (asignado por REPS)
   - Nombre y descripción del servicio
   - Modalidad (INTRAMURAL, AMBULATORIA, TELEMEDICINA, URGENCIAS, AMBULANCIA)
   - Complejidad (BAJA, MEDIA, ALTA)
   - Estado y fechas de habilitación
   - Vencimiento de habilitación por modalidad

3. **Autoevaluación** - Evaluación anual de cumplimiento
   - Período fiscal (2024-2028)
   - Versión del documento (para renovaciones)
   - Estados (BORRADOR, EN_CURSO, COMPLETADA, REVISADA, VALIDADA)
   - Porcentaje de cumplimiento calculado
   - Responsable de evaluación
   - Observaciones y notas

4. **Cumplimiento** - Evaluación de criterios específicos
   - Resultado (CUMPLE, NO_CUMPLE, PARCIALMENTE, NO_APLICA)
   - Hallazgos y observaciones detalladas
   - Planes de mejora con responsables
   - Fechas comprometidas de mejora
   - Documentos de evidencia adjuntos
   - Relación pivote: Autoevaluacion + ServicioSede + Criterio

#### **Endpoints API Completos**:

**Prestadores - DatosPrestador**
```
GET    /api/habilitacion/prestadores/              # Listar con paginación
POST   /api/habilitacion/prestadores/              # Crear nuevo
GET    /api/habilitacion/prestadores/{id}/         # Detalle completo
PUT    /api/habilitacion/prestadores/{id}/         # Actualizar completo
PATCH  /api/habilitacion/prestadores/{id}/         # Actualizar parcial
DELETE /api/habilitacion/prestadores/{id}/         # Eliminar

# Acciones personalizadas
GET    /api/habilitacion/prestadores/proximos_a_vencer/
GET    /api/habilitacion/prestadores/vencidas/
GET    /api/habilitacion/prestadores/{id}/servicios/
GET    /api/habilitacion/prestadores/{id}/autoevaluaciones/
POST   /api/habilitacion/prestadores/{id}/iniciar_renovacion/
```

**Servicios - ServicioSede**
```
GET    /api/habilitacion/servicios/                # Listar con filtros
POST   /api/habilitacion/servicios/                # Crear
GET    /api/habilitacion/servicios/{id}/           # Detalle
PUT    /api/habilitacion/servicios/{id}/           # Actualizar
PATCH  /api/habilitacion/servicios/{id}/           # Parcial
DELETE /api/habilitacion/servicios/{id}/           # Eliminar

# Acciones personalizadas
GET    /api/habilitacion/servicios/proximos_a_vencer/
GET    /api/habilitacion/servicios/por_complejidad/?complejidad=ALTA
GET    /api/habilitacion/servicios/{id}/cumplimientos/
```

**Autoevaluaciones**
```
GET    /api/habilitacion/autoevaluaciones/         # Listar
POST   /api/habilitacion/autoevaluaciones/         # Crear
GET    /api/habilitacion/autoevaluaciones/{id}/    # Detalle
PUT    /api/habilitacion/autoevaluaciones/{id}/    # Actualizar
PATCH  /api/habilitacion/autoevaluaciones/{id}/    # Parcial
DELETE /api/habilitacion/autoevaluaciones/{id}/    # Eliminar

# Acciones personalizadas
GET    /api/habilitacion/autoevaluaciones/por_completar/
GET    /api/habilitacion/autoevaluaciones/{id}/resumen/
POST   /api/habilitacion/autoevaluaciones/{id}/validar/
POST   /api/habilitacion/autoevaluaciones/{id}/duplicar/
```

**Cumplimientos de Criterios**
```
GET    /api/habilitacion/cumplimientos/            # Listar
POST   /api/habilitacion/cumplimientos/            # Crear evaluación
GET    /api/habilitacion/cumplimientos/{id}/       # Detalle
PUT    /api/habilitacion/cumplimientos/{id}/       # Actualizar
PATCH  /api/habilitacion/cumplimientos/{id}/       # Parcial
DELETE /api/habilitacion/cumplimientos/{id}/       # Eliminar

# Acciones personalizadas
GET    /api/habilitacion/cumplimientos/sin_cumplir/
GET    /api/habilitacion/cumplimientos/con_plan_mejora/
GET    /api/habilitacion/cumplimientos/mejoras_vencidas/
```

#### **Características Avanzadas**:

- **Vencimientos y Alertas**: Cálculo automático de días para vencimiento
- **Estado de Cumplimiento**: Seguimiento visual del % de cumplimiento por autoevaluación
- **Integración con Mejoras**: Contadores de planes y hallazgos vinculados en serializers de Cumplimiento y Autoevaluación
- **Documentación**: Adjunción de evidencia en cumplimientos
- **Duplicación**: Copiar autoevaluaciones para períodos siguientes
- **Validación**: Workflow de validación de autoevaluaciones
- **Reportes**: Resumen estadístico de cumplimiento por período

### 7. Planes de Mejora (`mejoras/`)

**Módulo Transversal de Planes de Mejora y Hallazgos**

Sistema centralizado que recibe hallazgos y planes de mejora tanto del módulo de habilitación como del módulo de auditorías.

#### **Modelos Principales**:

1. **PlanMejora** - Plan de mejora con seguimiento completo
   - Número de plan único (`numero_plan`)
   - Origen: `HABILITACION`, `AUDITORIA`, `INDICADOR`
   - Estados: `PENDIENTE` → `EN_CURSO` → `COMPLETADO` (o `VENCIDO`)
   - FKs condicionales: `autoevaluacion`, `auditoria`, `resultado_indicador`, `cumplimiento`, `criterio`
   - Responsable, fechas de inicio/vencimiento, porcentaje de avance
   - Manager personalizado: `vencidos()`, `proximos_a_vencer()`, `por_estado()`, `activos()`

2. **Hallazgo** - Hallazgos asociados a planes de mejora
   - Tipo: `FORTALEZA`, `OPORTUNIDAD_MEJORA`, `NO_CONFORMIDAD`, `HALLAZGO`
   - Severidad: `BAJA`, `MEDIA`, `ALTA`, `CRÍTICA`
   - Estado: `ABIERTO`, `EN_SEGUIMIENTO`, `CERRADO`
   - Relación con PlanMejora, autoevaluacion, auditoria, criterio

3. **SoportePlan** - Archivos adjuntos a planes de mejora
   - Tipos: `EVIDENCIA`, `ACTA`, `INFORME`, `FOTOGRAFIA`, `PLAN_ACCION`, `OTRO`
   - Formatos permitidos: PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, JPEG
   - Tamaño máximo: 10 MB por archivo
   - Almacenamiento: `media/SoportesPlanes/` con nombres únicos (UUID)
   - Metadata: nombre original, tamaño en bytes, subido por

#### **Endpoints API**:

```
# Planes de Mejora
GET    /api/mejoras/planes-mejora/                    # Listar con filtros
POST   /api/mejoras/planes-mejora/                    # Crear plan
GET    /api/mejoras/planes-mejora/{id}/               # Detalle
PUT    /api/mejoras/planes-mejora/{id}/               # Actualizar
PATCH  /api/mejoras/planes-mejora/{id}/               # Parcial
DELETE /api/mejoras/planes-mejora/{id}/               # Eliminar
GET    /api/mejoras/planes-mejora/vencidos/           # Planes vencidos
GET    /api/mejoras/planes-mejora/proximos-vencer/    # Próximos a vencer
GET    /api/mejoras/planes-mejora/resumen/            # Estadísticas generales
GET    /api/mejoras/planes-mejora/por-origen/         # Agrupados por origen
GET    /api/mejoras/planes-mejora/{id}/soportes/      # Listar soportes
POST   /api/mejoras/planes-mejora/{id}/soportes/      # Subir soporte (multipart)
DELETE /api/mejoras/planes-mejora/{id}/soportes/{soporte_id}/ # Eliminar soporte

# Hallazgos
GET    /api/mejoras/hallazgos/                        # Listar con filtros
POST   /api/mejoras/hallazgos/                        # Crear hallazgo
GET    /api/mejoras/hallazgos/{id}/                   # Detalle
PUT    /api/mejoras/hallazgos/{id}/                   # Actualizar
PATCH  /api/mejoras/hallazgos/{id}/                   # Parcial
DELETE /api/mejoras/hallazgos/{id}/                   # Eliminar
GET    /api/mejoras/hallazgos/estadisticas/           # Estadísticas
GET    /api/mejoras/hallazgos/por-origen/             # Agrupados por origen
GET    /api/mejoras/hallazgos/sin-plan/               # Sin plan asignado
```

### 8. Auditorías (`audit/`)

**Módulo de Ciclo de Vida Completo de Auditorías**

Sistema de gestión de auditorías internas y externas con fases controladas, equipos auditores, hallazgos con trazabilidad y programas de auditoría.

#### **Modelos Principales**:

1. **Auditoria** - Ciclo de vida completo
   - Fases: `PROGRAMADA` → `NOTIFICADA` → `EN_EJECUCION` → `INFORME` → `SEGUIMIENTO` → `CERRADA` (o `CANCELADA`)
   - Clasificación: `INTERNA`, `EXTERNA`
   - Tipo y entidad auditora (catálogos)
   - Control de transiciones con `avanzar_fase()` y `puede_avanzar_a()`
   - Fechas de cada fase, alcance, objetivo, criterios

2. **MiembroEquipoAuditor** - Equipo de auditoría
   - Roles: `LIDER`, `AUDITOR`, `OBSERVADOR`, `EXPERTO`

3. **HallazgoAuditoria** - Hallazgos con trazabilidad a mejoras
   - Tipos: `NC_MAYOR`, `NC_MENOR`, `OBSERVACION`, `OPORTUNIDAD`, `FORTALEZA`
   - FKs opcionales a `mejoras.Hallazgo` y `mejoras.PlanMejora`
   - Evidencia objetiva, criterio de norma, proceso afectado

4. **ActaReunion** - Actas de apertura, cierre y seguimiento

5. **ProgramaAuditoria** - Programa anual con avance calculado
   - Estados: `BORRADOR`, `APROBADO`, `EN_EJECUCION`, `COMPLETADO`
   - M2M con auditorías, avance porcentual automático

#### **Endpoints API**:

```
# Catálogos
GET/POST        /api/audit/tipos/                    # Tipos de auditoría
GET/POST        /api/audit/entidades/                # Entidades auditoras

# Auditorías
GET    /api/audit/auditorias/                        # Listar con filtros
POST   /api/audit/auditorias/                        # Crear
GET    /api/audit/auditorias/{id}/                   # Detalle
PUT    /api/audit/auditorias/{id}/                   # Actualizar
POST   /api/audit/auditorias/{id}/cambiar-fase/      # Transición de fase
GET    /api/audit/auditorias/{id}/equipo/            # Ver equipo
POST   /api/audit/auditorias/{id}/equipo/            # Agregar miembro
DELETE /api/audit/auditorias/{id}/eliminar-miembro/  # Quitar miembro
GET    /api/audit/auditorias/{id}/actas/             # Actas de la auditoría
POST   /api/audit/auditorias/{id}/actas/             # Crear acta
GET    /api/audit/auditorias/resumen/                # Estadísticas generales
GET    /api/audit/auditorias/proximas/               # Próximas auditorías
GET    /api/audit/auditorias/por-fase/               # Conteo por fase

# Hallazgos de Auditoría
GET/POST        /api/audit/hallazgos/                # CRUD hallazgos
GET    /api/audit/hallazgos/vencidos/                # Con acciones vencidas
GET    /api/audit/hallazgos/estadisticas/            # Estadísticas

# Actas y Programas
GET/POST        /api/audit/actas/                    # CRUD actas
GET/POST        /api/audit/programas/                # CRUD programas
```

## API REST Endpoints

### Autenticación
```
POST /api/token/                    # Obtener token JWT
POST /api/token/refresh/            # Refrescar token
```

### Usuarios
```
POST /api/users/register/           # Registro de usuario
POST /api/users/login/              # Inicio de sesión
POST /api/users/logout/             # Cerrar sesión
POST /api/users/reset-password/     # Restablecer contraseña
```

### Empresas
```
GET    /api/companies/companies/    # Listar empresas
POST   /api/companies/companies/    # Crear empresa
GET    /api/companies/departments/  # Listar departamentos
```

### Indicadores
```
GET    /api/indicators/indicators/  # Listar indicadores
POST   /api/indicators/results/     # Crear resultado
```

### Normativity (Estándares Resolución 3100)
```
GET    /api/normativity/estandares/           # Listar estándares
GET    /api/normativity/estandares/{codigo}/  # Detalle estándar
GET    /api/normativity/estandares/todos/     # Acción: todos los estándares
GET    /api/normativity/criterios/            # Listar criterios
GET    /api/normativity/criterios/mandatorios/ # Acción: criterios obligatorios
GET    /api/normativity/documentos/           # Listar documentos normativos
```

### Habilitación de Servicios (SUH)
```
# Prestadores
GET    /api/habilitacion/prestadores/                 # Listar
POST   /api/habilitacion/prestadores/                 # Crear
GET    /api/habilitacion/prestadores/{id}/            # Detalle
GET    /api/habilitacion/prestadores/proximos_a_vencer/ # Próximos a vencer
GET    /api/habilitacion/prestadores/{id}/servicios/  # Servicios del prestador

# Servicios por Sede
GET    /api/habilitacion/servicios/              # Listar
POST   /api/habilitacion/servicios/              # Crear
GET    /api/habilitacion/servicios/proximos_a_vencer/ # Próximos a vencer

# Autoevaluaciones
GET    /api/habilitacion/autoevaluaciones/                # Listar
POST   /api/habilitacion/autoevaluaciones/                # Crear
GET    /api/habilitacion/autoevaluaciones/{id}/resumen/   # Resumen completo
POST   /api/habilitacion/autoevaluaciones/{id}/validar/   # Validar evaluación
POST   /api/habilitacion/autoevaluaciones/{id}/duplicar/  # Duplicar para nuevo período

# Cumplimientos (Criterios Evaluados)
GET    /api/habilitacion/cumplimientos/              # Listar
POST   /api/habilitacion/cumplimientos/              # Crear
GET    /api/habilitacion/cumplimientos/sin_cumplir/  # No conformidades
GET    /api/habilitacion/cumplimientos/con_plan_mejora/ # Con plan de mejora
GET    /api/habilitacion/cumplimientos/mejoras_vencidas/ # Mejoras vencidas
```

### Planes de Mejora
```
GET    /api/mejoras/planes-mejora/                    # Listar
POST   /api/mejoras/planes-mejora/                    # Crear
GET    /api/mejoras/planes-mejora/{id}/               # Detalle
GET    /api/mejoras/planes-mejora/vencidos/           # Vencidos
GET    /api/mejoras/planes-mejora/proximos-vencer/    # Próximos a vencer
GET    /api/mejoras/planes-mejora/resumen/            # Estadísticas
GET    /api/mejoras/planes-mejora/por-origen/         # Por origen
GET    /api/mejoras/planes-mejora/{id}/soportes/      # Listar soportes
POST   /api/mejoras/planes-mejora/{id}/soportes/      # Subir soporte (multipart)
DELETE /api/mejoras/planes-mejora/{id}/soportes/{soporte_id}/ # Eliminar soporte
GET    /api/mejoras/hallazgos/                        # Listar hallazgos
POST   /api/mejoras/hallazgos/                        # Crear hallazgo
GET    /api/mejoras/hallazgos/estadisticas/           # Estadísticas
GET    /api/mejoras/hallazgos/sin-plan/               # Sin plan asignado
```

### Auditorías
```
GET/POST   /api/audit/tipos/                         # Tipos de auditoría
GET/POST   /api/audit/entidades/                     # Entidades auditoras
GET    /api/audit/auditorias/                        # Listar
POST   /api/audit/auditorias/                        # Crear
GET    /api/audit/auditorias/{id}/                   # Detalle
POST   /api/audit/auditorias/{id}/cambiar-fase/      # Transición de fase
GET    /api/audit/auditorias/{id}/equipo/            # Ver equipo
POST   /api/audit/auditorias/{id}/equipo/            # Agregar miembro
GET    /api/audit/auditorias/{id}/actas/             # Actas
GET    /api/audit/auditorias/resumen/                # Estadísticas
GET    /api/audit/auditorias/proximas/               # Próximas
GET    /api/audit/auditorias/por-fase/               # Por fase
GET/POST   /api/audit/hallazgos/                     # CRUD hallazgos
GET/POST   /api/audit/actas/                         # CRUD actas
GET/POST   /api/audit/programas/                     # CRUD programas
```

## Documentación y Recursos

### Documentación del Proyecto

1. **documentos.md** - Guía Completa para Frontend
   - Arquitectura de modelos detallada
   - Especificación de todos los endpoints
   - Ejemplos de requests/responses en JSON
   - Pantallas recomendadas a desarrollar
   - Validaciones y reglas de negocio
   - Stack técnico recomendado
   - Información sobre autenticación JWT

2. **architecture.md** - Arquitectura Técnica del Sistema
   - Diagramas de arquitectura de alto nivel
   - Arquitectura de capas
   - Modelo de datos detallado
   - Flujos de procesos de negocio
   - Descripción de módulos y dependencias
   - Estrategias de escalabilidad y performance
   - Decisiones de arquitectura (ADRs)

3. **Portal_Habilitacion_API_completo.postman_collection.json**
   - Colección de Postman con 40+ ejemplos
   - Todos los endpoints documentados
   - Variables preconfiguradas
   - Ejemplos de requests y responses
   - Ambiente de desarrollo y producción

### Acceso a Documentación

```bash
# Ver documentación del módulo de habilitación
cat documentos.md

# Ver arquitectura técnica
cat architecture.md

# Importar en Postman
Portal_Habilitacion_API_completo.postman_collection.json
```

### Estándares y Criterios (Resolución 3100/2019)

La base de datos incluye los 7 estándares y 21 criterios de evaluación:

1. **Talento Humano (TH)** - 3 criterios
2. **Infraestructura Física (INF)** - 3 criterios
3. **Dotación, Medicamentos e Insumos (DOT)** - 3 criterios
4. **Procesos Organizacionales (PO)** - 3 criterios
5. **Recurso Sanguíneo e Hemoterapia (RS)** - 3 criterios
6. **Gestión Integral del Servicio (GI)** - 3 criterios
7. **Seguridad del Paciente y Ambiente (SA)** - 3 criterios

Acceso a través de:
```
GET /api/normativity/estandares/
GET /api/normativity/criterios/
GET /api/normativity/criterios/mandatorios/
```

### Estructura de Respuestas API

#### Listado (GET)
```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "codigo": "SA", "nombre": "Seguridad", ... }
  ]
}
```

#### Detalle (GET ID)
```json
{
  "id": 1,
  "codigo": "SA",
  "nombre": "Seguridad",
  "version_resolucion": "3100/2019",
  "criterios": [ ... ]
}
```

#### Creación (POST)
```json
{
  "id": 1,
  "codigo_reps": "110001234567",
  "clase_prestador": "IPS",
  "estado_habilitacion": "EN_PROCESO",
  ...
}
```

El proyecto está configurado para trabajar con frontend en:
- `http://localhost:5173` (Vite/React)
- `http://localhost:5174`
- Dominios de producción configurados

## Configuración de Email

El sistema utiliza Gmail SMTP para envío de correos:
- Autenticación de dos factores
- Recuperación de contraseña
- Notificaciones del sistema

## Deployment

### Desarrollo
```bash
python manage.py runserver
```

### Producción con Waitress
```bash
python run_waitress.py
```

### Configuración IIS (Windows Server)
El proyecto incluye `web.config` para deployment en IIS.

## Seguridad

- **JWT Authentication**: Tokens seguros con tiempo de expiración
- **2FA**: Autenticación de dos factores por email
- **CORS**: Configuración restrictiva de orígenes
- **Validación de datos**: Serializers con validación completa
- **Middleware de seguridad**: Protección contra ataques comunes

## Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Test específico por app
python manage.py test normativity         # Tests del módulo de estándares
python manage.py test habilitacion        # Tests del módulo de habilitación
python manage.py test users               # Tests de usuarios
python manage.py test audit               # Tests de auditoría
python manage.py test mejoras             # Tests del módulo de mejoras

# Test específico de una clase
python manage.py test normativity.tests.EstandarAPITests
python manage.py test habilitacion.tests.DatosPrestadorAPITests

# Test integral de endpoints (54 endpoints)
python test_all_endpoints.py

# Con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Genera reporte HTML en htmlcov/
```

### Cobertura de Tests Esperada
- **normativity**: 21 test methods, 6 test classes
- **habilitacion**: 28 test methods, 8 test classes
- **mejoras**: Planes de mejora, hallazgos, soportes (upload/delete)
- **audit**: Auditorías, ciclo de vida, equipos, hallazgos, actas, programas
- **test_all_endpoints.py**: 54 tests integrales cubriendo todos los endpoints
- **Total**: 100+ test methods cubriendo modelos, serializers y API endpoints

## Comandos Git Útiles

```bash
# Hacer commit
git add .
git commit -m "Descripción del cambio"
git push

# Ver estado
git status

# Cambiar de rama
git checkout nombreRama

# Actualizar requirements
pip freeze > requirements.txt
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto es propiedad privada. Todos los derechos reservados.

## Soporte

Para soporte técnico, contactar al equipo de desarrollo:
- **Backend Lead**: Edison Narváez
- **Project Manager**: Equipo de Desarrollo
- **Repository**: https://github.com/Edisonnarvaez/portal_web_backend

## Recursos Adicionales

- 📖 [documentos.md](documentos.md) - Guía Completa para Desarrollo Frontend
- 🏗️ [architecture.md](architecture.md) - Arquitectura Técnica del Sistema
- 📮 [Portal_Habilitacion_API_completo.postman_collection.json](Portal_Habilitacion_API_completo.postman_collection.json) - Postman Collection

## Versión del Sistema

- **Versión**: 2.0.0
- **Última Actualización**: Febrero 2026
- **Django**: 5.2.2
- **Python**: 3.12.10+

## Estado del Proyecto

🚀 **En Desarrollo Activo**

- ✅ Sistema de autenticación completo (JWT + 2FA)
- ✅ Gestión de empresas y usuarios
- ✅ Sistema de indicadores
- ✅ **Módulo Normativity** (7 estándares + 21 criterios Res. 3100/2019)
- ✅ **Módulo Habilitación**:
  - ✅ Gestión de Prestadores (DatosPrestador)
  - ✅ Gestión de Servicios por Sede (ServicioSede)
  - ✅ Autoevaluaciones Anuales (Autoevaluacion)
  - ✅ Evaluación de Cumplimientos (Cumplimiento)
  - ✅ Integración con módulo de Mejoras (contadores, resúmenes)
  - ✅ Alertas de Vencimiento
  - ✅ Reportes y Estadísticas
- ✅ **Módulo Mejoras** (transversal):
  - ✅ Planes de Mejora con ciclo de estados
  - ✅ Hallazgos con severidad y clasificación
  - ✅ Soportes/Adjuntos (PDF, Word, Excel, PNG) hasta 10 MB
  - ✅ Vinculación con Habilitación y Auditorías
  - ✅ Estadísticas y reportes por origen
- ✅ **Módulo Auditorías** (ciclo de vida completo):
  - ✅ 7 fases controladas con transiciones validadas
  - ✅ Equipos auditores con roles
  - ✅ Hallazgos con trazabilidad a mejoras
  - ✅ Actas de reunión (apertura, cierre, seguimiento)
  - ✅ Programas de auditoría con avance calculado
  - ✅ Catálogos de tipos y entidades
- ✅ **Suite de Tests** (100+ test methods, 54 endpoints verificados)
- ✅ **Documentación Completa**:
  - ✅ Architecture.md (Diagramas y flujos)
  - ✅ README.md (Este archivo)
  - ✅ documentos.md v2.0 (Guía frontend completa)
  - ✅ Postman Collection (40+ ejemplos)
- 🔄 Optimización de performance
- 📋 Integración con APIs externas (gobierno)

---

**Desarrollado con ❤️ para la optimización de procesos empresariales**
