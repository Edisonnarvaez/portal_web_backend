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
                PROVIDERS[Providers Module]
                INVOICING[Invoicing Module]
                INDICATORS[Indicators Module]
                AUDIT[Audit Module]
                PROCESSES[Processes Module]
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
    API_GATEWAY --> PROVIDERS
    API_GATEWAY --> INVOICING
    API_GATEWAY --> INDICATORS
    API_GATEWAY --> AUDIT
    API_GATEWAY --> PROCESSES
    
    COMPANIES --> DB
    PROVIDERS --> DB
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
            PROVIDER_VIEWS[Provider Views]
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
            PROVIDER_MODEL[Provider Models]
            INVOICE_MODEL[Invoice Models]
            INDICATOR_MODEL[Indicator Models]
        end
        
        subgraph "Serializers"
            USER_SERIAL[User Serializers]
            COMPANY_SERIAL[Company Serializers]
            PROVIDER_SERIAL[Provider Serializers]
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
    REST_API --> PROVIDER_VIEWS
    REST_API --> INVOICE_VIEWS
    REST_API --> INDICATOR_VIEWS
    
    USER_VIEWS --> AUTH_SERVICE
    PROVIDER_VIEWS --> EMAIL_SERVICE
    INVOICE_VIEWS --> VALIDATION_SERVICE
    INDICATOR_VIEWS --> REPORT_SERVICE
    
    USER_VIEWS --> USER_SERIAL
    COMPANY_VIEWS --> COMPANY_SERIAL
    PROVIDER_VIEWS --> PROVIDER_SERIAL
    INVOICE_VIEWS --> INVOICE_SERIAL
    
    USER_SERIAL --> USER_MODEL
    COMPANY_SERIAL --> COMPANY_MODEL
    PROVIDER_SERIAL --> PROVIDER_MODEL
    INVOICE_SERIAL --> INVOICE_MODEL
    
    USER_MODEL --> DATABASE
    COMPANY_MODEL --> DATABASE
    PROVIDER_MODEL --> DATABASE
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
    
    Terceros ||--o{ Factura : creates
    Pais ||--o{ Departamento : contains
    Departamento ||--o{ Municipio : contains
    Terceros }o--|| Municipio : located_in
    
    Factura ||--o{ FacturaDetalle : contains
    Factura }o--|| EstadoFactura : has
    Factura }o--|| CentroCostos : assigned_to
    Factura }o--|| CentroOperaciones : belongs_to
    Factura }o--o| CausalDevolucion : may_have
    
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
    
    Terceros {
        int tercero_id PK
        string tercero_nombre
        string tercero_documento
        string tercero_telefono
        email tercero_email
        string tercero_direccion
    }
```

---

## 🔄 Flujo de Procesos de Negocio

### Flujo de Gestión de Facturas Electrónicas

```mermaid
stateDiagram-v2
    [*] --> Recepcion : Factura Recibida
    
    Recepcion --> Etapa1 : Validar FE
    Etapa1 : Gestionar Factura Electrónica
    
    Etapa1 --> Etapa2 : FE Validada
    Etapa1 --> Rechazada : FE Inválida
    
    Etapa2 : Pendiente de Revisión
    Etapa2 --> Etapa3 : Revisión Aprobada
    Etapa2 --> Rechazada : Revisión Rechazada
    
    Etapa3 : Pendiente Reconocimiento Contable
    Etapa3 --> Etapa4 : Reconocimiento Aprobado
    Etapa3 --> Rechazada : Reconocimiento Rechazado
    
    Etapa4 : Revisión de Impuestos
    Etapa4 --> Etapa5 : Impuestos Aprobados
    Etapa4 --> Rechazada : Impuestos Rechazados
    
    Etapa5 : Revisión Contraloría
    Etapa5 --> Etapa6 : Contraloría Aprobada
    Etapa5 --> Rechazada : Contraloría Rechazada
    
    Etapa6 : Pendiente de Pago
    Etapa6 --> Pagada : Pago Procesado
    Etapa6 --> Rechazada : Pago Rechazado
    
    Rechazada --> [*] : Proceso Terminado
    Pagada --> [*] : Proceso Completado
```

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
        TERCERO[tercero/]
        PROVIDERS[gestionProveedores/]
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
    DJANGO --> TERCERO
    DJANGO --> PROVIDERS
    DJANGO --> INDICATORS
    DJANGO --> PROCESSES
    DJANGO --> MAIN
    DJANGO --> AUDIT

    DRF --> USERS
    DRF --> COMPANIES
    DRF --> TERCERO
    DRF --> PROVIDERS
    DRF --> INDICATORS
    DRF --> PROCESSES

    JWT --> USERS
    JWT --> PROVIDERS
    JWT --> INDICATORS

    USERS --> COMPANIES
    PROVIDERS --> TERCERO
    PROVIDERS --> COMPANIES
    INDICATORS --> COMPANIES
    AUDIT --> COMPANIES
    PROCESSES --> COMPANIES

    EMAIL --> USERS
    EMAIL --> PROVIDERS
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

## 🚀 Patrones de Arquitectura Implementados

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

## 🛠️ Tecnologías y Herramientas

### Stack Tecnológico Completo

| Capa | Tecnología | Propósito |
|------|------------|-----------|
| **Backend Framework** | Django 5.2.2 | Framework web principal |
| **API Framework** | Django REST Framework | API REST |
| **Database** | PostgreSQL/SQLite | Base de datos relacional |
| **Cache** | Redis | Cache y sesiones |
| **Authentication** | JWT | Autenticación stateless |
| **Task Queue** | Celery | Tareas asíncronas |
| **Web Server** | Nginx + Waitress | Servidor web y WSGI |
| **Monitoring** | Sentry | Monitoreo de errores |
| **Documentation** | DRF-Spectacular | Documentación API |
| **Testing** | Pytest | Testing framework |
| **Code Quality** | Black, Flake8 | Formateo y linting |

### Configuración de Entornos

```python
# settings/base.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Custom apps
    'users',
    'companies',
    'gestionProveedores',
    'tercero',
    'indicators',
    'processes',
    'main',
]

# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'conn_max_age': 600,
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
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

## 🔮 Roadmap de Arquitectura

### Fase 1: Consolidación (Q1 2025)
- [ ] Completar módulo de auditoría
- [ ] Implementar testing completo
- [ ] Optimizar consultas de base de datos
- [ ] Documentar APIs con OpenAPI

### Fase 2: Escalabilidad (Q2 2025)
- [ ] Migrar a PostgreSQL en producción
- [ ] Implementar Redis para caching
- [ ] Configurar Celery para tareas asíncronas
- [ ] Implementar monitoring con Sentry

### Fase 3: Optimización (Q3 2025)
- [ ] Implementar CDN para archivos estáticos
- [ ] Optimizar performance de APIs
- [ ] Implementar circuit breakers
- [ ] Configurar auto-scaling

### Fase 4: Avanzada (Q4 2025)
- [ ] Implementar Event Sourcing para auditoría
- [ ] Migrar a arquitectura de microservicios
- [ ] Implementar GraphQL API
- [ ] Machine Learning para predicciones

---

*Documento actualizado: Octubre 2025*  
*Próxima revisión: Enero 2026*