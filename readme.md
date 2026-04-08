# Portal Web Backend

Backend Django para gestion de usuarios, estructura organizacional, habilitacion, auditorias, mejoras, soportes documentales e indicadores.

Este README esta orientado a que un ingeniero nuevo pueda:

- Entender el alcance funcional
- Levantar el proyecto localmente
- Ubicar rapido los modulos y endpoints
- Operar y depurar sin depender de contexto previo

## 1. Resumen Ejecutivo

- Arquitectura actual: monolito Django modular
- Exposicion: API REST con DRF
- Autenticacion: JWT + 2FA (users)
- Base por defecto: SQLite
- Cache por defecto: LocMemCache
- Estaticos: WhiteNoise

Documentos clave del repositorio:

- `architecture.md` (arquitectura tecnica completa)
- `ENDPOINTS_API.md` (inventario canónico de endpoints)
- `documentos.md` (detalle funcional/extenso por modulo)

## 2. Stack Tecnologico (Verificado)

- Django 5.2.2
- djangorestframework 3.16.0
- djangorestframework_simplejwt 5.5.0
- django-filter 25.2
- django-cors-headers 4.7.0
- python-dotenv 1.1.0
- waitress 3.0.2
- whitenoise 6.9.0
- pyotp 2.9.0
- psycopg2-binary 2.9.10

## 3. Estructura del Proyecto

```text
portal_web_backend/
├── backend/                # Settings, urls, asgi/wsgi
├── users/                  # Auth, 2FA, roles, perfil
├── companies/              # Empresas, sedes, procesos y geografia
├── processes/              # Documentos de proceso
├── main/                   # Contenido transversal
├── indicators/             # Indicadores y resultados
├── normativity/            # Estandares y criterios
├── habilitacion/           # Prestadores, servicios, autoevaluaciones
├── soportes/               # Catalogo y repositorio documental
├── mejoras/                # Planes de mejora y hallazgos
├── audit/                  # Auditorias, hallazgos, actas, programas
├── architecture.md
├── ENDPOINTS_API.md
├── documentos.md
├── requirements.txt
├── manage.py
└── run_waitress.py
```

## 4. Modulos Funcionales (Mapa Rapido)

### users

- Login
- Verify OTP
- 2FA enable/verify/toggle
- Password reset request/confirm
- Change password
- Current user
- Roles

### companies

- CRUD de empresas
- Departamentos
- Sedes
- Tipos de proceso
- Procesos
- Regiones/municipios

### processes

- CRUD de documentos
- Preview/download de archivo

### main

- Funcionarios
- Contenidos
- Eventos
- Felicitaciones
- Reconocimientos

### indicators

- CRUD indicadores
- CRUD resultados
- Endpoint agregado para dashboard

### normativity

- CRUD estandares
- CRUD criterios
- CRUD documentos normativos
- Endpoints de consulta especializada

### habilitacion

- Prestadores
- Servicios por sede
- Autoevaluaciones
- Cumplimientos
- Capacidades, medidas, sanciones
- Novedades REPS
- Checklists, items y evidencias

### soportes

- Categorias
- Tipos de documento
- Documentos de soporte

### mejoras

- Planes de mejora
- Hallazgos
- Soportes por plan
- Consultas resumen/estado/origen

### audit

- Auditorias y transicion de fase
- Equipo auditor
- Hallazgos de auditoria
- Actas
- Programas

## 5. API: Rutas Base

Global:

- `POST /api/token/`
- `POST /api/token/refresh/`

Apps:

- `/api/users/`
- `/api/companies/`
- `/api/processes/`
- `/api/main/`
- `/api/indicators/`
- `/api/normativity/`
- `/api/habilitacion/`
- `/api/soportes/`
- `/api/mejoras/`
- `/api/audit/`

Detalle completo de endpoints:

- `ENDPOINTS_API.md`

## 6. Quick Start Local

### 6.1 Crear entorno virtual

PowerShell (Windows):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 6.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 6.3 Configurar variables de entorno

Crear `.env` en raiz:

```env
DJANGO_SECRET_KEY=tu_clave
FRONTEND_URL=http://localhost:5173
EMAIL_HOST_USER=tu_correo
EMAIL_HOST_PASSWORD=tu_password_app
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### 6.4 Preparar base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6.5 Cargar catalogos iniciales (recomendado)

```bash
python cargar_estandares.py
python manage.py cargar_catalogo_soportes
```

### 6.6 Levantar servicio

Desarrollo:

```bash
python manage.py runserver
```

Alterno (Waitress):

```bash
python run_waitress.py
```

## 7. Configuracion y Entorno

Estado actual en settings:

- `DEBUG=True`
- `ALLOWED_HOSTS = ["localhost", "127.0.0.1"]`
- DB activa: SQLite
- CORS para origenes locales
- CSRF trusted origins por `FRONTEND_URL`
- `AUTH_USER_MODEL = users.User`

Recursos de archivos:

- `STATIC_ROOT = staticfiles/`
- `MEDIA_ROOT = media/`

## 8. Autenticacion y Seguridad

Implementado:

- JWT como autenticacion por defecto de DRF
- Flujos 2FA (users)
- Roles de usuario
- CORS + CSRF config basica

Para cada request autenticado:

- Header `Authorization: Bearer <access_token>`

## 9. Validacion y Calidad

Chequeo basico del proyecto:

```bash
python manage.py check
```

Pruebas por modulo (ejemplos):

```bash
python manage.py test users
python manage.py test habilitacion
python manage.py test audit
python manage.py test mejoras
```

## 10. Guia de Navegacion para Ingenieros

Cuando debas intervenir una funcionalidad, sigue este orden:

1. Revisar rutas del modulo en `*/urls.py`
2. Revisar viewset/apiview en `*/views.py` o `*/views/`
3. Revisar serializer asociado
4. Revisar modelo y relaciones
5. Confirmar endpoint en `ENDPOINTS_API.md`
6. Ejecutar `manage.py check` y pruebas relevantes

## 11. Operacion y Deployment

Opciones reales del repositorio:

- Desarrollo con runserver
- Ejecucion local con Waitress
- Archivo `web.config` para escenario IIS

## 12. Limitaciones Actuales (Importante)

Estado actual observado:

- No hay microservicios (monolito)
- Celery no esta configurado ni operativo
- Redis no es cache activa
- PostgreSQL no esta activo por defecto

## 13. Convenciones de Mantenimiento Documental

Cuando se cambie API o modelo:

1. Actualizar endpoint en `ENDPOINTS_API.md`
2. Ajustar impacto en `architecture.md`
3. Ajustar onboarding/operacion en este README
4. Verificar consistencia con `documentos.md`

## 14. Soporte y Referencias Internas

- `architecture.md`
- `ENDPOINTS_API.md`
- `documentos.md`
- `Portal_Habilitacion_API_completo.postman_collection.json`

---

README orientado a uso operativo real para ingenieria.
