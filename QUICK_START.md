╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                      ⚡ QUICK START GUIDE                                  ║
║                   Portal Web Backend - Habilitación                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

## 🚀 INICIAR EN 5 MINUTOS

### 1️⃣ Activar Entorno Virtual
```powershell
cd D:\portal_web_backend
.\venv\Scripts\Activate.ps1
```

### 2️⃣ Iniciar Servidor
```powershell
python manage.py runserver 8000
```

### 3️⃣ Acceder al Admin
```
URL: http://127.0.0.1:8000/admin/
Usuario: admin
Contraseña: (la que configuraste)
```

### 4️⃣ Explorar Datos
```
Admin → Habilitación → Autoevaluaciones
        → Cumplimientos
        → Datos de Prestadores
```

═══════════════════════════════════════════════════════════════════════════════

## 📋 TAREAS COMUNES

### Crear Nueva Autoevaluación
1. Admin → Habilitación → Autoevaluaciones → Agregar
2. Seleccionar DatosPrestador
3. El número se genera automáticamente
4. Guardar

### Agregar Cumplimientos
1. Admin → Habilitación → Cumplimientos → Agregar
2. Para cada criterio:
   - Seleccionar Autoevaluación
   - Seleccionar Criterio
   - Marcar Resultado (CUMPLE, NO_CUMPLE, etc.)
   - Guardar

### Cargar Datos de Ejemplo
```powershell
python manage.py create_sample_data
```

### Ver Todos los Estándares
```powershell
python manage.py shell
>>> from normativity.models import Estandar
>>> for e in Estandar.objects.all():
...     print(f"{e.codigo} - {e.nombre}")
```

═══════════════════════════════════════════════════════════════════════════════

## 🐛 ERRORES COMUNES & SOLUCIONES

### "No module named 'django'"
```powershell
# Solución: Activar venv
.\venv\Scripts\Activate.ps1
```

### "'Headquarters' object has no attribute 'nombre'"
```python
# ❌ INCORRECTO
obj.headquarters.nombre

# ✅ CORRECTO
obj.headquarters.name
```

### "Cannot delete DatosPrestador"
```python
# Hay Autoevaluaciones o Cumplimientos relacionados
# Solución: Eliminarlas primero
```

### "Unapplied migrations"
```powershell
python manage.py migrate
```

═══════════════════════════════════════════════════════════════════════════════

## 📊 CAMPOS CLAVE PARA RECORDAR

### Headquarters (La Sede)
- `name` ← Nombre (ej: "Sede Principal") **IMPORTANTE**
- `habilitationCode` ← Código único (ej: "SEDE-001")
- `departament` ← Departamento
- `city` ← Ciudad

### DatosPrestador
- `headquarters` ← FK a Headquarters (OneToOne) **IMPORTANTE**
- `codigo_reps` ← Código REPS (ej: "9009876543-001")
- `estado_habilitacion` ← HABILITADA, EN_PROCESO, etc.

### Autoevaluación
- `numero_autoevaluacion` ← Se genera automáticamente
- `datos_prestador` ← FK a DatosPrestador
- `periodo` ← Año (2024, 2025)

### Cumplimiento
- `autoevaluacion` ← FK a Autoevaluación
- `criterio` ← FK a Criterio
- `cumple` ← CUMPLE, NO_CUMPLE, PARCIALMENTE, NO_APLICA

═══════════════════════════════════════════════════════════════════════════════

## 📚 DOCUMENTACIÓN

| Archivo | Para Qué |
|---------|----------|
| ESTADO_ACTUAL.md | Ver estado actual y próximos pasos |
| ARQUITECTURA_HABILITACION.md | Entender la arquitectura |
| CUMPLIMIENTO_QUICK_GUIDE.txt | Guía rápida de cumplimientos |
| SESION_FINALIZADA.md | Resumen de sesión actual |

═══════════════════════════════════════════════════════════════════════════════

## 🔗 URLS ÚTILES

```
Admin:             http://127.0.0.1:8000/admin/
Habilitación:      http://127.0.0.1:8000/admin/habilitacion/
Autoevaluaciones:  http://127.0.0.1:8000/admin/habilitacion/autoevaluacion/
Cumplimientos:     http://127.0.0.1:8000/admin/habilitacion/cumplimiento/
Prestadores:       http://127.0.0.1:8000/admin/habilitacion/datosprestador/
```

═══════════════════════════════════════════════════════════════════════════════

## 💾 COMANDOS ÚTILES

### Ver datos en shell
```powershell
python manage.py shell
>>> from habilitacion.models import DatosPrestador
>>> DatosPrestador.objects.all()
```

### Crear datos de ejemplo
```powershell
python manage.py create_sample_data
```

### Hacer migraciones
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Crear superusuario
```powershell
python manage.py createsuperuser
```

═══════════════════════════════════════════════════════════════════════════════

## ✅ CHECKLIST ANTES DE USAR

- [ ] Venv activado
- [ ] Servidor corriendo (puerto 8000)
- [ ] Puedes acceder a http://127.0.0.1:8000/admin/
- [ ] Datos de ejemplo cargados
- [ ] Sin errores en el servidor

═══════════════════════════════════════════════════════════════════════════════

## 🎯 PRÓXIMO PASO

**Crear APIs REST**

```powershell
pip install djangorestframework
# Luego crear serializers y viewsets
```

Ver ESTADO_ACTUAL.md para más detalles.

═══════════════════════════════════════════════════════════════════════════════

**¿Necesitas ayuda?** 
Revisar ESTADO_ACTUAL.md - Sección "TROUBLESHOOTING"
