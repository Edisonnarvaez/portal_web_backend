# Portal Web Backend

## Descripción del Proyecto

Portal Web Backend es un sistema de gestión integral desarrollado en Django que proporciona una API REST completa para la gestión de proveedores, facturación electrónica, auditorías, indicadores y procesos organizacionales. El sistema está diseñado para empresas que requieren un control detallado de sus operaciones comerciales y administrativas.

### Características Principales

- 🏢 **Gestión de Empresas y Sedes**: Control completo de información corporativa
- 📋 **Sistema de Auditoría**: Seguimiento y control de auditorías organizacionales
- 📈 **Indicadores de Gestión**: Sistema de métricas y reportes
- 👥 **Gestión de Usuarios**: Sistema de autenticación JWT con roles y permisos
- 🔒 **Autenticación 2FA**: Seguridad adicional con autenticación de dos factores
- 📧 **Notificaciones por Email**: Sistema automatizado de notificaciones

## Tecnologías Utilizadas

### Backend
- **Django 5.2.2**: Framework web principal
- **Django REST Framework 3.16.0**: API REST
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
├── audit/                      # Sistema de auditoría (en desarrollo)
├── media/                      # Archivos multimedia
├── staticfiles/               # Archivos estáticos
└── requirements.txt           # Dependencias del proyecto
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

4. **Configurar variables de entorno**
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

6. **Crear superusuario (opcional)**
```bash
python manage.py createsuperuser
```

7. **Ejecutar el servidor**
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

## Configuración de CORS

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
python manage.py test users
python manage.py test gestionProveedores
```

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
- **Backend Lead**: [Contacto del desarrollador]
- **Project Manager**: [Contacto del PM]
- **Repository**: https://github.com/Edisonnarvaez/portal_web_backend

## Estado del Proyecto

🚀 **En Desarrollo Activo**

- ✅ Sistema de autenticación completo
- ✅ Gestión de empresas y usuarios
- ✅ Sistema de indicadores
- 🔄 Sistema de auditoría (en desarrollo)
- 📋 Documentación API (en progreso)

---

**Desarrollado con ❤️ para la optimización de procesos empresariales**
