# Arquitectura del Sistema - Portal Web Backend

## Descripción General

Este documento describe la arquitectura completa del Portal Web Backend, incluyendo la estructura de componentes, flujo de datos, patrones de diseño y diagramas técnicos. El sistema está construido con Django siguiendo principios de arquitectura limpia y patrones de microservicios modulares.

---

## 📐 Arquitectura de Alto Nivel

### Diagrama de Arquitectura General

```mermaid
graph TB
    subgraph "Frontend Layer"
        WEB[Web Application]
        MOBILE[Mobile App]
        API_CLIENT[API Clients]
    end

    subgraph "Load Balancer & Proxy"
        LB[Load Balancer/Nginx]
    end

    subgraph "Application Layer"
        subgraph "Django Backend"
            API_GATEWAY[API Gateway]
            AUTH[Authentication Service]
            
            subgraph "Core Modules"
                USERS[Users Module]
                COMPANIES[Companies Module]
                INVOICING[Invoicing Module]
                INDICATORS[Indicators Module]
                AUDIT[Audit Module]
                PROCESSES[Processes Module]
            end
            
            subgraph "Healthcare Compliance Modules"
                NORMATIVITY[Normativity Module]
                HABILITACION[Habilitacion Module]
            end
            
            MIDDLEWARE[Django Middleware]
            SERIALIZERS[DRF Serializers]
        end
        
        TASK_QUEUE[Celery Task Queue]
        EMAIL_SERVICE[Email Service]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL Database)]
        CACHE[(Redis Cache)]
        FILE_STORAGE[File Storage]
        
        subgraph "External Services"
            SMTP[SMTP Gmail]
            GOVT_API[Government APIs]
        end
    end

    subgraph "Infrastructure"
        MONITORING[Monitoring/Sentry]
        LOGGING[Centralized Logging]
        BACKUP[Database Backup]
    end

    %% Connections
    WEB --> LB
    MOBILE --> LB
    API_CLIENT --> LB
    
    LB --> API_GATEWAY
    API_GATEWAY --> AUTH
    AUTH --> USERS
    
    API_GATEWAY --> COMPANIES
    API_GATEWAY --> INVOICING
    API_GATEWAY --> INDICATORS
    API_GATEWAY --> AUDIT
    API_GATEWAY --> PROCESSES
    
    COMPANIES --> DB
    INVOICING --> DB
    INDICATORS --> DB
    AUDIT --> DB
    PROCESSES --> DB
    USERS --> DB
    
    TASK_QUEUE --> EMAIL_SERVICE
    EMAIL_SERVICE --> SMTP
    
    API_GATEWAY --> CACHE
    COMPANIES --> CACHE
    PROVIDERS --> CACHE
    
    PROCESSES --> FILE_STORAGE
    INVOICING --> FILE_STORAGE
    
    API_GATEWAY --> MONITORING
    DB --> BACKUP
```

---

## 🏗️ Arquitectura de Capas

### Diagrama de Capas del Sistema

```mermaid
graph TB
    subgraph "Presentation Layer"
        REST_API[REST API Endpoints]
        ADMIN[Django Admin Interface]
        SWAGGER[API Documentation]
    end

    subgraph "Business Logic Layer"
        subgraph "Views & ViewSets"
            USER_VIEWS[User Views]
            COMPANY_VIEWS[Company Views]
            INVOICE_VIEWS[Invoice Views]
            INDICATOR_VIEWS[Indicator Views]
        end
        
        subgraph "Services"
            AUTH_SERVICE[Authentication Service]
            EMAIL_SERVICE[Email Service]
            VALIDATION_SERVICE[Validation Service]
            REPORT_SERVICE[Report Service]
        end
    end

    subgraph "Data Access Layer"
        subgraph "Models & ORM"
            USER_MODEL[User Models]
            COMPANY_MODEL[Company Models]
            INVOICE_MODEL[Invoice Models]
            INDICATOR_MODEL[Indicator Models]
        end
        
        subgraph "Serializers"
            USER_SERIAL[User Serializers]
            COMPANY_SERIAL[Company Serializers]
            INVOICE_SERIAL[Invoice Serializers]
        end
    end

    subgraph "Infrastructure Layer"
        DATABASE[(Database)]
        CACHE_LAYER[(Cache)]
        FILE_SYSTEM[File System]
        EXTERNAL_APIS[External APIs]
    end

    REST_API --> USER_VIEWS
    REST_API --> COMPANY_VIEWS
    REST_API --> INVOICE_VIEWS
    REST_API --> INDICATOR_VIEWS
    
    USER_VIEWS --> AUTH_SERVICE
    PROVIDER_VIEWS --> EMAIL_SERVICE
    INVOICE_VIEWS --> VALIDATION_SERVICE
    INDICATOR_VIEWS --> REPORT_SERVICE
    
    USER_VIEWS --> USER_SERIAL
    COMPANY_VIEWS --> COMPANY_SERIAL
    INVOICE_VIEWS --> INVOICE_SERIAL
    
    USER_SERIAL --> USER_MODEL
    COMPANY_SERIAL --> COMPANY_MODEL
    INVOICE_SERIAL --> INVOICE_MODEL
    
    USER_MODEL --> DATABASE
    COMPANY_MODEL --> DATABASE
    INVOICE_MODEL --> DATABASE
    INDICATOR_MODEL --> DATABASE
    
    AUTH_SERVICE --> CACHE_LAYER
    EMAIL_SERVICE --> EXTERNAL_APIS
    REPORT_SERVICE --> FILE_SYSTEM
```

---

## 💾 Modelo de Datos

### Diagrama de Entidad-Relación Principal

```mermaid
erDiagram
    User ||--o{ UserProfile : has
    User ||--o{ Role : has
    Role ||--o{ App : accesses
    
    Company ||--o{ Department : contains
    Company ||--o{ Headquarters : has
    Department ||--o{ Process : contains
    Process ||--o{ ProcessType : belongs_to
    
    Headquarters ||--o{ Result : generates
    Indicator ||--o{ Result : measures
    
    Auditoria ||--o{ SedeAuditada : audits
    Auditoria }o--|| TipoAuditoria : is_type
    Auditoria }o--|| EntidadAuditoria : performed_by
    
    User {
        int id PK
        string email
        string first_name
        string last_name
        boolean is_active
        datetime date_joined
    }
    
    Company {
        int id PK
        string name
        string nit
        string legal_representative
        string phone
        string address
        email contact_email
        date foundation_date
        boolean status
    }
    
    Factura {
        int factura_id PK
        string factura_id_factura_electronica
        date factura_fecha
        decimal factura_valor
        string factura_concepto
        string factura_etapa
        boolean factura_estado
    }
    
```

---

## 🔄 Flujo de Procesos de Negocio


### Flujo de Autenticación con 2FA

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant EmailService
    participant Database

    User->>Frontend: Ingresa credenciales
    Frontend->>Backend: POST /api/users/login/
    Backend->>Database: Validar usuario
    Database-->>Backend: Usuario válido
    
    Backend->>EmailService: Generar código 2FA
    EmailService-->>Backend: Código generado
    Backend->>Database: Guardar código temporal
    EmailService->>User: Enviar email con código
    
    Backend-->>Frontend: Respuesta: "2FA requerido"
    Frontend->>User: Mostrar formulario 2FA
    
    User->>Frontend: Ingresa código 2FA
    Frontend->>Backend: POST /api/users/verify-2fa/
    Backend->>Database: Validar código
    Database-->>Backend: Código válido
    
    Backend->>Database: Generar JWT tokens
    Database-->>Backend: Tokens generados
    Backend-->>Frontend: JWT Access + Refresh tokens
    Frontend-->>User: Acceso autorizado
```

---

## 🔧 Arquitectura de Módulos

### Diagrama de Módulos y Dependencias

```mermaid
graph TD
    subgraph "Core Django"
        DJANGO[Django Framework]
        DRF[Django REST Framework]
        JWT[JWT Authentication]
    end

    subgraph "Custom Apps"
        USERS[users/]
        COMPANIES[companies/]
        INDICATORS[indicators/]
        PROCESSES[processes/]
        MAIN[main/]
        AUDIT[audit/]
    end

    subgraph "External Dependencies"
        EMAIL[Email Backend]
        CORS[CORS Headers]
        WHITENOISE[WhiteNoise]
        WAITRESS[Waitress WSGI]
    end

    DJANGO --> USERS
    DJANGO --> COMPANIES
    DJANGO --> INDICATORS
    DJANGO --> PROCESSES
    DJANGO --> MAIN
    DJANGO --> AUDIT

    DRF --> USERS
    DRF --> COMPANIES
    DRF --> INDICATORS
    DRF --> PROCESSES

    JWT --> USERS
    JWT --> INDICATORS

    USERS --> COMPANIES
    INDICATORS --> COMPANIES
    AUDIT --> COMPANIES
    PROCESSES --> COMPANIES

    EMAIL --> USERS
    CORS --> DRF
    WHITENOISE --> DJANGO
    WAITRESS --> DJANGO
```

---

## 🌐 Arquitectura de Red y Deployment

### Diagrama de Infraestructura de Producción

```mermaid
graph TB
    subgraph "Internet"
        USERS[Users]
        MOBILE_USERS[Mobile Users]
    end

    subgraph "DMZ"
        LB[Load Balancer/Nginx]
        SSL[SSL Termination]
    end

    subgraph "Web Tier"
        WEB1[Web Server 1]
        WEB2[Web Server 2]
        STATIC[Static Files Server]
    end

    subgraph "Application Tier"
        APP1[Django App 1]
        APP2[Django App 2]
        CELERY[Celery Workers]
    end

    subgraph "Data Tier"
        PRIMARY_DB[(Primary PostgreSQL)]
        REPLICA_DB[(Read Replica)]
        REDIS[(Redis Cache)]
        FILES[File Storage]
    end

    subgraph "External Services"
        SMTP_SERVICE[Gmail SMTP]
        GOVT_SERVICES[Government APIs]
        MONITORING[Sentry/Monitoring]
    end

    USERS --> SSL
    MOBILE_USERS --> SSL
    SSL --> LB

    LB --> WEB1
    LB --> WEB2
    LB --> STATIC

    WEB1 --> APP1
    WEB2 --> APP2

    APP1 --> PRIMARY_DB
    APP2 --> PRIMARY_DB
    APP1 --> REPLICA_DB
    APP2 --> REPLICA_DB
    APP1 --> REDIS
    APP2 --> REDIS
    APP1 --> FILES
    APP2 --> FILES

    CELERY --> PRIMARY_DB
    CELERY --> SMTP_SERVICE
    CELERY --> GOVT_SERVICES

    APP1 --> MONITORING
    APP2 --> MONITORING
```

---

## 🔐 Arquitectura de Seguridad

### Diagrama de Seguridad y Autenticación

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Perimeter Security"
            FIREWALL[Firewall]
            WAF[Web Application Firewall]
            DDOS[DDoS Protection]
        end

        subgraph "Application Security"
            JWT_AUTH[JWT Authentication]
            RBAC[Role-Based Access Control]
            TWO_FA[Two-Factor Authentication]
            VALIDATION[Input Validation]
        end

        subgraph "Data Security"
            ENCRYPTION[Data Encryption at Rest]
            TLS[TLS Encryption in Transit]
            HASH[Password Hashing]
            SANITIZATION[SQL Injection Protection]
        end

        subgraph "Infrastructure Security"
            VPN[VPN Access]
            KEY_MGMT[Key Management]
            AUDIT_LOG[Security Audit Logs]
            BACKUP_ENC[Encrypted Backups]
        end
    end

    subgraph "Monitoring & Compliance"
        SEC_MONITOR[Security Monitoring]
        COMPLIANCE[Compliance Checks]
        INCIDENT[Incident Response]
    end

    FIREWALL --> WAF
    WAF --> JWT_AUTH
    JWT_AUTH --> RBAC
    RBAC --> TWO_FA

    JWT_AUTH --> ENCRYPTION
    VALIDATION --> SANITIZATION
    ENCRYPTION --> TLS

    VPN --> KEY_MGMT
    AUDIT_LOG --> SEC_MONITOR
    BACKUP_ENC --> COMPLIANCE
```

---

## 📊 Arquitectura de Datos

### Diagrama de Flujo de Datos

```mermaid
graph TD
    subgraph "Data Sources"
        USER_INPUT[User Input]
        FILE_UPLOAD[File Uploads]
        EMAIL_DATA[Email Data]
        GOVT_DATA[Government APIs]
    end

    subgraph "Data Processing"
        VALIDATION[Data Validation]
        TRANSFORMATION[Data Transformation]
        ENRICHMENT[Data Enrichment]
    end

    subgraph "Data Storage"
        TRANSACTIONAL[(Transactional DB)]
        ANALYTICAL[(Analytics DB)]
        CACHE[(Cache Layer)]
        FILES[File Storage]
    end

    subgraph "Data Access"
        API_LAYER[REST API Layer]
        REPORT_ENGINE[Report Engine]
        DASHBOARD[Dashboard Queries]
    end

    subgraph "Data Consumers"
        WEB_APP[Web Application]
        MOBILE_APP[Mobile App]
        REPORTS[Generated Reports]
        ANALYTICS[Analytics Dashboard]
    end

    USER_INPUT --> VALIDATION
    FILE_UPLOAD --> VALIDATION
    EMAIL_DATA --> VALIDATION
    GOVT_DATA --> VALIDATION

    VALIDATION --> TRANSFORMATION
    TRANSFORMATION --> ENRICHMENT

    ENRICHMENT --> TRANSACTIONAL
    ENRICHMENT --> ANALYTICAL
    ENRICHMENT --> CACHE
    FILE_UPLOAD --> FILES

    TRANSACTIONAL --> API_LAYER
    ANALYTICAL --> REPORT_ENGINE
    CACHE --> API_LAYER
    TRANSACTIONAL --> DASHBOARD

    API_LAYER --> WEB_APP
    API_LAYER --> MOBILE_APP
    REPORT_ENGINE --> REPORTS
    DASHBOARD --> ANALYTICS
```

---

## 🏥 Flujo de Habilitación de Servicios de Salud (SUH)

### Diagrama del Proceso de Habilitación

```mermaid
sequenceDiagram
    participant Prestador as Prestador<br/>Salud
    participant Sistema as Portal<br/>Habilitacion
    participant BD as Base de<br/>Datos
    participant Admin as Auditor<br/>MINSALUD

    Prestador->>Sistema: 1. Registrar como Prestador
    Sistema->>BD: Crear DatosPrestador
    BD-->>Sistema: ID Prestador creado
    
    Prestador->>Sistema: 2. Registrar Servicios por Sede
    Sistema->>BD: Crear ServicioSede (múltiples)
    BD-->>Sistema: Servicios registrados
    
    Prestador->>Sistema: 3. Autoevaluación Anual
    Sistema->>BD: Crear Autoevaluacion
    BD-->>Sistema: ID Autoevaluación
    
    Prestador->>Sistema: 4. Diligenciar Cumplimientos
    nota over Prestador,Sistema: 21 Criterios × Servicios = Cumplimientos
    Sistema->>BD: Crear Cumplimiento
    BD-->>Sistema: Evaluación registrada
    
    Prestador->>Sistema: 5. Generar Reporte
    Sistema->>BD: Calcular Porcentaje Cumplimiento
    BD-->>Sistema: Resumen preparado
    
    Prestador->>Sistema: 6. Enviar a Revisión
    Sistema->>Admin: Notificar auditor
    Admin-->>Sistema: Revisar cumplimientos
    
    Admin->>Sistema: Aceptar o Solicitar Mejoras
    Sistema->>BD: Actualizar estado habilitación
    BD-->>Prestador: Resultado de habilitación
```

### Diagrama de Relaciones de Datos - Habilitación

```mermaid
erDiagram
    Company ||--|| DatosPrestador : "OneToOne"
    Headquarters ||--o{ ServicioSede : "contains"
    DatosPrestador ||--o{ ServicioSede : "provides"
    DatosPrestador ||--o{ Autoevaluacion : "has"
    Autoevaluacion ||--o{ Cumplimiento : "contains"
    ServicioSede ||--o{ Cumplimiento : "evaluated_in"
    Criterio ||--o{ Cumplimiento : "measures"
    Estandar ||--o{ Criterio : "groups"
    
    DatosPrestador {
        int id PK
        int company_id FK "OneToOne"
        string codigo_reps "Unique"
        string clase_prestador "IPS|PROF|DROGUERIA|etc"
        string estado_habilitacion "EN_PROCESO|HABILITADA|NO_HABILITADA|VENCIDA"
        date fecha_vencimiento_habilitacion
        text observaciones
        timestamp fecha_creacion
    }
    
    ServicioSede {
        int id PK
        int sede_id FK
        string codigo_servicio "Unique together with sede"
        string nombre_servicio
        string modalidad "HOSPITALIZACION|CONSULTA|URGENCIAS"
        string complejidad "BAJA|MEDIA|ALTA"
        date fecha_vencimiento
        text observaciones
    }
    
    Autoevaluacion {
        int id PK
        int datos_prestador_id FK
        int periodo "2024, 2025, etc"
        int version "1, 2, 3 (renovaciones)"
        string estado "BORRADOR|VALIDADA|ENVIADA|APROBADA|RECHAZADA"
        date fecha_vencimiento
        int usuario_responsable_id FK
        datetime fecha_creacion
    }
    
    Cumplimiento {
        int id PK
        int autoevaluacion_id FK
        int servicio_sede_id FK
        int criterio_id FK
        string cumple "CUMPLE|NO_CUMPLE|PARCIALMENTE"
        text hallazgo
        text plan_mejora
        date fecha_compromiso
        boolean mejora_vencida
    }
    
    Criterio {
        int id PK
        string codigo_estandar FK
        string codigo "7.1, 7.2, etc"
        string nombre
        string complejidad "BAJA|MEDIA|ALTA"
        boolean requiere_evidencia
        text descripcion
    }
    
    Estandar {
        string codigo PK "TH|INF|DOT|PO|RS|GI|SA"
        string nombre "Talento Humano, etc"
        string version_resolucion "3100/2019"
        text descripcion
    }
```

### Diagrama de Relaciones de Datos - Habilitación

```mermaid
erDiagram
    Company ||--|| DatosPrestador : "habilitacion"
    Headquarters ||--o{ ServicioSede : "contains"
    DatosPrestador ||--o{ Autoevaluacion : "has"
    Autoevaluacion ||--o{ Cumplimiento : "evaluates"
    ServicioSede ||--o{ Cumplimiento : "evaluated_in"
    Criterio ||--o{ Cumplimiento : "measures"
    Estandar ||--o{ Criterio : "groups"
    User ||--o{ Cumplimiento : "responsible_for"
    Documento ||--o{ Cumplimiento : "evidences"
    
    DatosPrestador {
        int id PK
        int company_id FK "OneToOne"
        int headquarters_id FK "OneToOne"
        string codigo_reps "Unique, max 20"
        string clase_prestador "IPS|PROF|PH|PJ"
        string estado_habilitacion "HABILITADA|EN_PROCESO|SUSPENDIDA|NO_HABILITADA|CANCELADA"
        date fecha_inscripcion
        date fecha_renovacion
        date fecha_vencimiento_habilitacion
        string aseguradora_pep
        string numero_poliza
        date vigencia_poliza
        datetime fecha_creacion
        datetime fecha_actualizacion
    }
    
    ServicioSede {
        int id PK
        int sede_id FK
        string codigo_servicio "Unique with sede"
        string nombre_servicio
        text descripcion
        string modalidad "INTRAMURAL|AMBULATORIA|TELEMEDICINA|URGENCIAS|AMBULANCIA"
        string complejidad "BAJA|MEDIA|ALTA"
        string estado_habilitacion "HABILITADO|EN_PROCESO|SUSPENDIDO|NO_HABILITADO|CANCELADO"
        date fecha_habilitacion
        date fecha_vencimiento
        datetime fecha_creacion
        datetime fecha_actualizacion
    }
    
    Autoevaluacion {
        int id PK
        int datos_prestador_id FK
        int periodo "2024-2028"
        int version "1, 2, 3 (renovaciones)"
        string estado "BORRADOR|EN_CURSO|COMPLETADA|REVISADA|VALIDADA"
        date fecha_inicio
        date fecha_completacion
        date fecha_vencimiento
        int usuario_responsable_id FK
        text observaciones
        datetime fecha_creacion
        datetime fecha_actualizacion
    }
    
    Cumplimiento {
        int id PK
        int autoevaluacion_id FK
        int servicio_sede_id FK
        int criterio_id FK
        string cumple "CUMPLE|NO_CUMPLE|PARCIALMENTE|NO_APLICA"
        text hallazgo
        text plan_mejora
        int responsable_mejora_id FK
        date fecha_compromiso
        datetime fecha_creacion
        datetime fecha_actualizacion
    }
    
    Criterio {
        int id PK
        int estandar_id FK
        string codigo "1.1, 1.2, etc"
        string nombre "Nombre del criterio"
        text descripcion
        string complejidad "BAJA|MEDIA|ALTA"
        boolean requiere_evidencia
    }
    
    Estandar {
        string codigo PK "TH|INF|DOT|PO|RS|GI|SA"
        string nombre "Talento Humano, etc"
        string version_resolucion "3100/2019"
        text descripcion
        boolean estado
    }
```

### Flujo Transaccional de Habilitación

```mermaid
sequenceDiagram
    participant Prestador
    participant API
    participant DB
    participant Admin

    Prestador->>API: 1. POST Crear DatosPrestador
    API->>DB: Guardar prestador + estado EN_PROCESO
    DB-->>API: ID creado
    
    Prestador->>API: 2. POST Crear ServicioSede (múltiples)
    API->>DB: Guardar servicios por sede
    DB-->>API: IDs servicios
    
    Prestador->>API: 3. POST Crear Autoevaluacion
    API->>DB: Generar AUT-REPS-PERIODO-VERSION
    DB-->>API: ID autoevaluación
    
    Prestador->>API: 4. POST Crear Cumplimientos (21+ criterios)
    note over API,DB: Para cada combinación:<br/>Autoevaluacion + Servicio + Criterio
    API->>DB: Guardar resultado + plan mejora
    DB-->>API: ID cumplimiento
    
    Prestador->>API: 5. GET Resumen Autoevaluacion
    API->>DB: Calcular % cumplimiento
    DB-->>API: Estadísticas
    
    Prestador->>API: 6. POST Validar Autoevaluacion
    API->>DB: Cambiar estado a VALIDADA
    DB-->>API: Confirmación
    
    API->>Admin: Notificación: Nueva autoevaluación validada
    
    Admin->>API: Revisar cumplimientos y planes de mejora
    Admin->>API: POST Validación final
    API->>DB: Actualizar estado DatosPrestador
    DB-->>Prestador: Resultado de habilitación
```

### Acciones Disponibles en API - Habilitación

#### DatosPrestador Endpoints (Prestadores)

```
GET    /api/habilitacion/prestadores/
       Listar constantes todos los prestadores con paginación
       Query: page, search, estado_habilitacion, clase_prestador, ordering

POST   /api/habilitacion/prestadores/
       Crear nuevo prestador
       Body: codigo_reps, company_id, clase_prestador, estado_habilitacion, etc.

GET    /api/habilitacion/prestadores/{id}/
       Obtener detalle completo del prestador

PATCH  /api/habilitacion/prestadores/{id}/
       Actualizar información del prestador

DELETE /api/habilitacion/prestadores/{id}/
       Eliminar prestador (solo si no tiene evaluaciones)

GET    /api/habilitacion/prestadores/proximos_a_vencer/
       Prestadores con habilitación venciendo en próximos 90 días
       Response: Lista paginada con días_vencimiento

GET    /api/habilitacion/prestadores/vencidas/
       Prestadores con habilitación ya vencida
       Response: Ordenado por fecha de vencimiento

GET    /api/habilitacion/prestadores/{id}/servicios/
       Listar todos los servicios habilitados de un prestador
       Response: Lista de ServicioSede

GET    /api/habilitacion/prestadores/{id}/autoevaluaciones/
       Historial de autoevaluaciones del prestador
       Response: Lista paginada ordenada por período descendente

POST   /api/habilitacion/prestadores/{id}/iniciar_renovacion/
       Iniciar proceso de renovación de habilitación
       Validación: Solo si falta ≤180 días para vencimiento
       Response: DatosPrestador con estado = EN_PROCESO
```

#### ServicioSede Endpoints (Servicios)

```
GET    /api/habilitacion/servicios/
       Listar todos los servicios
       Filtros: sede, modalidad, complejidad, estado_habilitacion
       Búsqueda: Código o nombre del servicio

POST   /api/habilitacion/servicios/
       Crear nuevo servicio
       Body: sede_id, codigo_servicio, nombre_servicio, modalidad, complejidad

GET    /api/habilitacion/servicios/{id}/
       Obtener detalle del servicio

PATCH  /api/habilitacion/servicios/{id}/
       Actualizar información del servicio

DELETE /api/habilitacion/servicios/{id}/
       Eliminar servicio

GET    /api/habilitacion/servicios/proximos_a_vencer/
       Servicios con vencimiento próximo (0-90 días)
       Response: Lista ordenada por fecha vencimiento

GET    /api/habilitacion/servicios/por_complejidad/
       Filtrar servicios por nivel de complejidad
       Query: complejidad=BAJA|MEDIA|ALTA
       Response: Lista filtrada

GET    /api/habilitacion/servicios/{id}/cumplimientos/
       Obtener cumplimientos evaluados del servicio
       Query: autoevaluacion_id (opcional)
       Response: Lista de Cumplimiento
```

#### Autoevaluacion Endpoints (Evaluaciones)

```
GET    /api/habilitacion/autoevaluaciones/
       Listar autoevaluaciones
       Filtros: datos_prestador, periodo, estado
       Búsqueda: numero_autoevaluacion, codigo_reps

POST   /api/habilitacion/autoevaluaciones/
       Crear nueva autoevaluación
       Body: datos_prestador_id, periodo, fecha_vencimiento
       Auto: numero_autoevaluacion generado

GET    /api/habilitacion/autoevaluaciones/{id}/
       Obtener detalle completo con cumplimientos_data
       Response: Includes porcentaje_cumplimiento, resumen

PATCH  /api/habilitacion/autoevaluaciones/{id}/
       Actualizar autoevaluación (notas, observaciones)

DELETE /api/habilitacion/autoevaluaciones/{id}/
       Eliminar autoevaluación (solo BORRADOR)

GET    /api/habilitacion/autoevaluaciones/por_completar/
       Autoevaluaciones sin completar (BORRADOR, EN_CURSO)
       Response: Lista con urgencia de completación

GET    /api/habilitacion/autoevaluaciones/{id}/resumen/
       Resumen estadístico completo de la evaluación
       Response: {
         total_cumplimientos: 80,
         resumen_por_resultado: {
           cumple: 70,
           no_cumple: 5,
           parcialmente: 3,
           no_aplica: 2
         },
         porcentaje_cumplimiento: 87.5,
         pendientes_mejora: 5,
         mejoras_vencidas: 1
       }

POST   /api/habilitacion/autoevaluaciones/{id}/validar/
       Cambiar estado a VALIDADA
       Generador de fecha_completacion automática
       Response: Autoevaluación actualizada

POST   /api/habilitacion/autoevaluaciones/{id}/duplicar/
       Crear nueva versión para próximo período
       Action: Copia datos, incrementa período y versión
       Response: Nueva Autoevaluación creada (201 CREATED)
```

#### Cumplimiento Endpoints (Criterios Evaluados)

```
GET    /api/habilitacion/cumplimientos/
       Listar cumplimientos
       Filtros: autoevaluacion, servicio_sede, criterio, cumple
       Búsqueda: Código o nombre criterio

POST   /api/habilitacion/cumplimientos/
       Crear evaluación de criterio
       Body: autoevaluacion_id, servicio_sede_id, criterio_id, 
             cumple, hallazgo, plan_mejora, responsable_mejora, 
             fecha_compromiso

GET    /api/habilitacion/cumplimientos/{id}/
       Obtener detalle completo del cumplimiento
       Response: Includes criterio_detail, documentos_evidencia_list

PATCH  /api/habilitacion/cumplimientos/{id}/
       Actualizar result de cumplimiento
       Actualizar hallazgo, plan mejora, responsable

DELETE /api/habilitacion/cumplimientos/{id}/
       Eliminar cumplimiento

GET    /api/habilitacion/cumplimientos/sin_cumplir/
       Criterios NO_CUMPLE con planes de mejora
       Response: Lista ordenada por fecha_compromiso

GET    /api/habilitacion/cumplimientos/con_plan_mejora/
       Cumplimientos con plan de mejora pendiente
       Response: Lista completa de pendientes

GET    /api/habilitacion/cumplimientos/mejoras_vencidas/
       Compromisos de mejora con fecha vencida
       CRITICAL: Usar para alertas
       Response: Lista roja de prioridad máxima
```

---

### 1. Model-View-Controller (MVC)
```python
# Django implementa MTV (Model-Template-View)
# Model: Django Models (ORM)
# View: Django Views/ViewSets
# Template: Frontend (React/Vue) separado
```

### 2. Repository Pattern
```python
# Implementado a través de Django ORM
# Managers personalizados actúan como repositories
class FacturaManager(models.Manager):
    def get_by_etapa(self, etapa):
        return self.filter(factura_etapa=etapa)
```

### 3. Service Layer Pattern
```python
# Servicios de negocio separados de las vistas
class EmailService:
    def send_2fa_code(self, user, code):
        # Lógica de envío de email
        pass
```

### 4. Serializer Pattern (DTO)
```python
# Django REST Framework Serializers
class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'
```

---

## 📈 Escalabilidad y Performance

### Estrategias de Escalabilidad

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        LB[Load Balancer]
        APP1[App Instance 1]
        APP2[App Instance 2]
        APP3[App Instance N]
    end

    subgraph "Database Scaling"
        MASTER[(Master DB)]
        SLAVE1[(Read Replica 1)]
        SLAVE2[(Read Replica 2)]
    end

    subgraph "Caching Strategy"
        REDIS[(Redis Cluster)]
        CDN[Content Delivery Network]
        BROWSER[Browser Cache]
    end

    subgraph "Performance Optimization"
        CONNECTION_POOL[DB Connection Pooling]
        QUERY_OPT[Query Optimization]
        LAZY_LOAD[Lazy Loading]
        PAGINATION[API Pagination]
    end

    LB --> APP1
    LB --> APP2
    LB --> APP3

    APP1 --> MASTER
    APP2 --> SLAVE1
    APP3 --> SLAVE2

    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS

    CDN --> BROWSER
```

---

## 🔍 Monitoreo y Observabilidad

### Arquitectura de Monitoreo

```mermaid
graph TB
    subgraph "Application Metrics"
        APP_METRICS[Application Metrics]
        ERROR_TRACKING[Error Tracking]
        PERFORMANCE[Performance Monitoring]
    end

    subgraph "Infrastructure Metrics"
        SYSTEM_METRICS[System Metrics]
        DB_METRICS[Database Metrics]
        NETWORK_METRICS[Network Metrics]
    end

    subgraph "Logging"
        APP_LOGS[Application Logs]
        ACCESS_LOGS[Access Logs]
        ERROR_LOGS[Error Logs]
    end

    subgraph "Monitoring Tools"
        SENTRY[Sentry]
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        ELK[ELK Stack]
    end

    subgraph "Alerting"
        ALERTS[Alert Manager]
        NOTIFICATIONS[Notifications]
        ESCALATION[Escalation Policies]
    end

    APP_METRICS --> SENTRY
    ERROR_TRACKING --> SENTRY
    PERFORMANCE --> PROMETHEUS

    SYSTEM_METRICS --> PROMETHEUS
    DB_METRICS --> PROMETHEUS
    NETWORK_METRICS --> PROMETHEUS

    APP_LOGS --> ELK
    ACCESS_LOGS --> ELK
    ERROR_LOGS --> ELK

    PROMETHEUS --> GRAFANA
    ELK --> GRAFANA

    GRAFANA --> ALERTS
    ALERTS --> NOTIFICATIONS
    NOTIFICATIONS --> ESCALATION
```

---

---

## 📚 Stack Tecnológico Completo

| Capa | Tecnología | Propósito | Versión |
|------|------------|-----------|---------|
| **Backend Framework** | Django | Framework web principal | 5.2.2+ |
| **API Framework** | Django REST Framework | API REST | 3.16.0+ |
| **Database** | PostgreSQL / SQLite | Base de datos relacional | 15+/3+ |
| **Cache** | Redis | Cache y sesiones | 7.0+ |
| **Authentication** | django-rest-framework-simplejwt | Autenticación JWT | Integrado |
| **Task Queue** | Celery | Tareas asíncronas | 5.3+ |
| **Web Server** | Nginx + Waitress | Servidor web y WSGI | Waitress 2.1+ |
| **Monitoring** | Sentry | Monitoreo de errores | Opcional |
| **Documentation** | DRF-Spectacular | Documentación automática OpenAPI | Planeado |
| **Testing** | Pytest / unittest | Testing framework | Pytest 8.0+ |
| **Code Quality** | Black, Flake8, isort | Formateo y linting | Latest |
| **API Documentation** | Postman | Colección de ejemplos | 40+ endpoints |
| **Frontend Docs** | Markdown | Documentación técnica frontend | documentos.md |

### Configuración por Entorno

#### Desarrollo
```python
# settings/development.py
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

#### Producción
```python
# settings/production.py
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## 📋 Decisiones de Arquitectura

### Architecture Decision Records (ADR)

#### ADR-001: Elección de Django REST Framework
- **Fecha**: 2024-01-15
- **Estado**: Aceptado
- **Contexto**: Necesidad de crear API REST robusta
- **Decisión**: Usar Django REST Framework
- **Consecuencias**: 
  - ✅ Serialización automática
  - ✅ Autenticación integrada
  - ✅ Documentación automática
  - ❌ Curva de aprendizaje

#### ADR-002: Autenticación JWT vs Sessions
- **Fecha**: 2024-01-20
- **Estado**: Aceptado
- **Contexto**: API stateless para múltiples clientes
- **Decisión**: JWT con refresh tokens
- **Consecuencias**:
  - ✅ Escalabilidad horizontal
  - ✅ Soporte multi-cliente
  - ❌ Complejidad en invalidación

#### ADR-003: Estructura Modular de Apps
- **Fecha**: 2024-01-25
- **Estado**: Aceptado
- **Contexto**: Mantenibilidad y separación de responsabilidades
- **Decisión**: Apps Django por dominio de negocio
- **Consecuencias**:
  - ✅ Separación clara de responsabilidades
  - ✅ Reutilización de código
  - ✅ Testing independiente
  - ❌ Complejidad en relaciones entre apps

---

---

## 🔮 Roadmap de Arquitectura

### Fase 1: Consolidación (Q1 2025) ✅ COMPLETADO
- [x] Completar módulo de auditoría
- [x] Implementar testing completo (49+ test methods)
- [x] Optimizar consultas de base de datos con select_related/prefetch_related
- [x] Documentar APIs con serializers y docstrings
- [x] Módulo Normativity con 7 estándares + 21 criterios
- [x] Módulo Habilitación completo (DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento)
- [x] Documentación Frontend (documentos.md)
- [x] Postman Collection con 40+ ejemplos

### Fase 2: Escalabilidad (Q2 2025) 🔄 EN PROGRESO
- [ ] Migrar a PostgreSQL en producción (preparado)
- [ ] Implementar Redis para caching de consultas frecuentes
- [ ] Configurar Celery para envío de emails asincrónico
- [ ] Implementar monitoring con Sentry
- [ ] Circuit breakers para APIs externas

### Fase 3: Optimización (Q3 2025)
- [ ] Implementar CDN para archivos estáticos
- [ ] Optimización de performance de APIs (< 200ms)
- [ ] Database connection pooling
- [ ] API rate limiting y throttling
- [ ] Caching a nivel de serializers

### Fase 4: Avanzada (Q4 2025)
- [ ] Event Sourcing para auditoría completa
- [ ] Migrar a arquitectura de microservicios (opcional)
- [ ] GraphQL API complementaria
- [ ] Machine Learning para análisis de cumplimiento
- [ ] Integración con APIs del gobierno

### Fase 5: Mantenimiento y Soporte (2026+)
- [ ] Soporte a PostgreSQL production
- [ ] CI/CD pipeline completo
- [ ] Disaster recovery planning
- [ ] Performance monitoring y alerting
- [ ] Actualizaciones de seguridad regulares

---

*Documento actualizado: Octubre 2025*  
*Próxima revisión: Enero 2026*