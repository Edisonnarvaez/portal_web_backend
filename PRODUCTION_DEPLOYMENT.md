# 🚀 GUÍA DE DEPLOYMENT A PRODUCCIÓN

## Resumen Ejecutivo

El Portal Web Backend está **LISTO PARA PRODUCCIÓN**. Sistema completo con todos los estándares de Resolución 3100/2019 cargados automáticamente.

---

## ✓ Pre-requisitos

### Tecnologías Requeridas
```bash
- Python 3.10+
- Django 5.2.2
- PostgreSQL (recomendado para producción)
- Git 2.0+
```

### Dependencias Python
```bash
pip install -r requirements.txt
```

---

## 📋 PASO 1: Clonar y Configurar Repositorio

```bash
# Clonar
git clone <repository-url>
cd portal_web_backend

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🗂️ PASO 2: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# .env
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recomendado)
DATABASE_ENGINE=postgresql
DATABASE_NAME=portal_habilitacion
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email (para notificaciones)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True

# CORS (si aplica)
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 💾 PASO 3: Crear y Migrar Base de Datos

```bash
# Crear base de datos PostgreSQL
createdb portal_habilitacion

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
# Seguir prompts para ingresar usuario y contraseña
```

---

## 🎯 PASO 4: Cargar Datos Iniciales (Fixtures)

### OPCIÓN A: Mediante Django Shell (Recomendado)

```bash
python manage.py shell
```

Luego ejecutar dentro del shell:
```python
exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())
```

**Salida esperada:**
```
✓ CARGANDO ESTÁNDARES DE RESOLUCIÓN 3100/2019
  ✓ 7 estándares creados (TH, INF, DOT, PO, RS, GI, SA)

✓ CARGANDO CRITERIOS (21 CRITERIOS TOTALES)
  ✓ 21 criterios cargados (3 por estándar)

✓ CARGANDO DOCUMENTOS NORMATIVOS
  ✓ 4 documentos normativos cargados

✓ CARGA COMPLETADA EXITOSAMENTE
✓ Total de 32 registros cargados
```

### OPCIÓN B: Ejecutar como Script Directo

```bash
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings'); import django; django.setup(); exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())"
```

---

## 🧪 PASO 5: Verificar Datos Cargados

```bash
# Ver en Django Shell
python manage.py shell
```

```python
from normativity.models import Estandar, Criterio, DocumentoNormativo

# Verificar conteos
print(f"Estándares: {Estandar.objects.count()}")           # Debe ser 7
print(f"Criterios: {Criterio.objects.count()}")             # Debe ser 21
print(f"Documentos: {DocumentoNormativo.objects.count()}")  # Debe ser 4+

# Ver detalle de un estándar
estandar = Estandar.objects.get(codigo='TH')
print(f"Estándar: {estandar.nombre}")
print(f"Criterios: {estandar.criterios.count()}")  # Debe ser 3
```

---

## 🌐 PASO 6: Recolectar Static Files

```bash
python manage.py collectstatic --noinput
```

---

## 🚀 PASO 7: Ejecutar en Producción

### Opción A: Usando Gunicorn (Recomendado)

```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar
gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --log-level info
```

### Opción B: Usando Waitress

```bash
python run_waitress.py
```

### Opción C: Usando Django Development Server (NO RECOMENDADO para producción)

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🔐 PASO 8: Configurar Nginx (Reverse Proxy)

Crear `/etc/nginx/sites-available/portal_habilitacion`:

```nginx
upstream django_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Static files
    location /static/ {
        alias /path/to/portal_web_backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /path/to/portal_web_backend/media/;
        expires 7d;
    }

    # Proxy a Django
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Activar configuración:
```bash
sudo ln -s /etc/nginx/sites-available/portal_habilitacion /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 PASO 9: Certificado SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx

sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renew
sudo certbot renew --dry-run
```

---

## 📊 PASO 10: Acceder al Sistema

### Admin Interface
```
https://yourdomain.com/admin/
Usuario: (creado en paso 3)
Contraseña: (creado en paso 3)
```

### APIs REST
```
GET  https://yourdomain.com/api/normativity/estandares/
GET  https://yourdomain.com/api/normativity/criterios/
GET  https://yourdomain.com/api/habilitacion/autoevaluaciones/
```

### Frontend (si aplica)
```
https://yourdomain.com/
```

---

## 📋 Datos Cargados Automáticamente

### 7 Estándares de Resolución 3100/2019

| Código | Nombre | Criterios | Complejidad |
|--------|--------|-----------|------------|
| **TH** | Talento Humano | 3 | Alta |
| **INF** | Infraestructura Física | 3 | Alta |
| **DOT** | Dotación y Medicamentos | 3 | Alta |
| **PO** | Procesos Organizacionales | 3 | Media |
| **RS** | Relacionamiento | 3 | Media |
| **GI** | Garantía de Calidad | 3 | Media |
| **SA** | Seguridad del Paciente | 3 | Alta |

**Total: 7 Estándares + 21 Criterios**

---

## ✓ Verificación de Sistema

Ejecutar en producción:

```bash
python manage.py check --deploy
```

Salida esperada:
```
System check identified no issues (0 silenced).
```

Si hay advertencias, abordar según las recomendaciones.

---

## 🔄 Actualizaciones Futuras

### Cargar nuevos estándares o criterios

1. Editar `normativity/fixtures_loader.py`
2. Agregar nuevos datos en `estandares_data` o `criterios_por_estandar`
3. Ejecutar script nuevamente (idempotente, no duplica)

```bash
python manage.py shell
exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())
```

---

## 🆘 Troubleshooting

### Error: "Database connection refused"
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Iniciar si está detenido
sudo systemctl start postgresql
```

### Error: "Permission denied on static files"
```bash
# Dar permisos
chmod -R 755 staticfiles/
sudo chown -R www-data:www-data staticfiles/
```

### Error: "ModuleNotFoundError"
```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt

# O en virtual environment
deactivate
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Fixtures duplicados en ejecuciones múltiples
```bash
# El script usa get_or_create(), por lo que:
# - Primera ejecución: CREA registros (⊕)
# - Segunda ejecución: ENCUENTRA registros (✓) sin duplicar
```

---

## 📞 Soporte

Para más información:
- Documentación Django: https://docs.djangoproject.com/
- Resolución 3100: https://www.minsalud.gov.co/
- Email: support@yourdomain.com

---

## ✓ Checklist de Deployment

- [ ] Repositorio clonado y actualizado
- [ ] Virtual environment activado
- [ ] Dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Base de datos creada
- [ ] Migraciones aplicadas
- [ ] Superusuario creado
- [ ] Fixtures cargados (32 registros)
- [ ] Static files recolectados
- [ ] Sistema iniciado sin errores
- [ ] Admin accesible y funcional
- [ ] APIs REST respondiendo correctamente
- [ ] Certificado SSL activo
- [ ] Nginx configurado y corriendo
- [ ] Monitoreo activado

---

**✓ Sistema Lista para Producción**

*Última actualización: 2025-12-12*
