# Portal Web Backend

Backend Django para gestión de usuarios, empresas, habilitación, auditorías, mejoras, soportes, indicadores y documentos de proceso.

## Estado Real del Proyecto

- Arquitectura: monolito Django
- API: Django REST Framework (ViewSets + APIViews)
- Auth: JWT + flujos 2FA en users
- DB por defecto: SQLite
- Cache por defecto: LocMemCache
- Estáticos: WhiteNoise
- Servidor local alterno: Waitress

## Stack Tecnológico (Verificado)

Dependencias principales en requirements.txt:

- Django 5.2.2
- djangorestframework 3.16.0
- djangorestframework_simplejwt 5.5.0
- django-filter 25.2
- django-cors-headers 4.7.0
- python-dotenv 1.1.0
- waitress 3.0.2
- whitenoise 6.9.0
- pyotp 2.9.0
- psycopg2-binary 2.9.10 (disponible para usar PostgreSQL, no activo por defecto)

## Estructura Principal

```text
portal_web_backend/
├── backend/
├── users/
├── companies/
├── processes/
├── main/
├── indicators/
├── normativity/
├── habilitacion/
├── soportes/
├── mejoras/
├── audit/
├── architecture.md
├── ENDPOINTS_API.md
├── requirements.txt
├── manage.py
└── run_waitress.py
```

## Instalación

### 1) Crear y activar entorno virtual

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3) Configurar .env

Variables mínimas sugeridas:

```env
DJANGO_SECRET_KEY=tu_clave
FRONTEND_URL=http://localhost:5173
EMAIL_HOST_USER=tu_correo
EMAIL_HOST_PASSWORD=tu_password_app
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### 4) Migrar base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5) (Opcional) Cargar catálogos

```bash
python cargar_estandares.py
python manage.py cargar_catalogo_soportes
```

### 6) Ejecutar servidor

Desarrollo:

```bash
python manage.py runserver
```

Waitress:

```bash
python run_waitress.py
```

## Configuración de Datos

### Base actual por defecto

- SQLite en db.sqlite3

### PostgreSQL

- Existe configuración de ejemplo comentada en backend/settings.py
- psycopg2-binary ya esta en requirements

## API y Endpoints

### Endpoints globales

- POST /api/token/
- POST /api/token/refresh/

### Prefijos por app

- /api/users/
- /api/companies/
- /api/processes/
- /api/main/
- /api/indicators/
- /api/normativity/
- /api/habilitacion/
- /api/soportes/
- /api/mejoras/
- /api/audit/

Inventario completo y actualizado:

- ENDPOINTS_API.md

## Módulos Funcionales

### users

- Login
- Verify OTP
- Enable/verify/toggle 2FA
- Password reset request/confirm
- Change password
- Current user
- Roles y listado de usuarios

### companies

- CRUD de empresas, departamentos, sedes, tipos de proceso, procesos, regiones y municipios

### processes

- CRUD de documentos
- Preview y download de archivo

### main

- CRUD de funcionarios, contenidos, eventos, felicitaciones, reconocimientos
- Consultas de cumpleaños y reconocimientos publicados/no publicados

### indicators

- CRUD de indicadores y resultados
- Endpoint detailed para resultados

### normativity

- CRUD de estándares, criterios y documentos normativos
- Endpoints de consulta: todos, criterios por estándar, mandatorios, por complejidad, con evidencia

### habilitacion

- CRUD de prestadores, servicios, autoevaluaciones, cumplimientos y componentes complementarios
- Endpoints de negocio para vencimientos, resúmenes, validaciones, duplicados y avance de checklist

### soportes

- CRUD de categorías, tipos de documento y soportes documentales

### mejoras

- CRUD de planes de mejora y hallazgos
- Consultas de vencidos, próximos a vencer, resumen y por origen
- Upload/list/delete de soportes por plan

### audit

- CRUD de auditorías, entidades, tipos, hallazgos, actas y programas
- Cambio de fase
- Gestión de equipo auditor
- Resúmenes y estadísticas

## Seguridad

- JWT como autenticación por defecto de DRF
- 2FA disponible en el modulo users
- CORS con origenes definidos en settings
- CSRF trusted origins basado en FRONTEND_URL

## Archivos Estáticos y Media

- STATIC_ROOT: staticfiles/
- MEDIA_ROOT: media/

## Testing

Ejecución básica:

```bash
python manage.py test
```

Por app (ejemplo):

```bash
python manage.py test users
python manage.py test habilitacion
python manage.py test audit
python manage.py test mejoras
```

## Deployment

- Desarrollo: runserver
- Ejecución con Waitress: run_waitress.py
- Archivo web.config disponible para escenario IIS

## Límites y Observaciones Importantes

Revisión estricta del estado actual:

- No hay arquitectura de microservicios; la aplicación es monolítica
- Celery no está configurado/activo
- Redis no está configurado como caché activa
- SQLite es la base activa por defecto

## Documentación Relacionada

- architecture.md
- ENDPOINTS_API.md
- documentos.md
- Portal_Habilitacion_API_completo.postman_collection.json
