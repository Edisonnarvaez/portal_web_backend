# ⚡ GUÍA RÁPIDA - Fixtures Loader

## 🎯 TL;DR

**Una línea para cargar todos los estándares de Resolución 3100:**

```bash
python manage.py shell
```

Luego dentro del shell:
```python
exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())
```

---

## ✓ Qué se carga automáticamente

### 7 Estándares (Resolución 3100/2019)
- **TH** - Talento Humano (3 criterios)
- **INF** - Infraestructura Física (3 criterios)
- **DOT** - Dotación y Medicamentos (3 criterios)
- **PO** - Procesos Organizacionales (3 criterios)
- **RS** - Relacionamiento (3 criterios)
- **GI** - Garantía de Calidad (3 criterios)
- **SA** - Seguridad del Paciente (3 criterios)

### Total Cargas
- ✓ 7 Estándares
- ✓ 21 Criterios (3 por estándar)
- ✓ 4 Documentos Normativos
- ✓ **32 registros totales**

---

## 📦 Características del Script

### ✅ Idempotente
Ejecutar el script 1, 2 o 100 veces produce el mismo resultado. No duplica registros gracias a `get_or_create()`.

### ✅ Producción Ready
Incluye:
- Manejo completo de errores
- Salida formateada y clara
- Validación de datos
- Documentación integrada

### ✅ Datos Completos
Cada criterio incluye:
- Código único (1.1, 1.2, etc.)
- Nombre descriptivo
- Descripción detallada
- Nivel de complejidad (ALTA, MEDIA, BAJA)
- Flags: es_mandatorio, aplica_todos, requiere_evidencia_documental

---

## 🚀 Ejecución Directa (Sin Django Shell)

```bash
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings'); import django; django.setup(); exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())"
```

O más simple, crear un script `load_fixtures.py`:

```python
#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())
```

Luego:
```bash
python load_fixtures.py
```

---

## 📊 Verificar que se cargó correctamente

```bash
python manage.py shell
```

```python
from normativity.models import Estandar, Criterio

# Ver todos los estándares
estandares = Estandar.objects.all()
for est in estandares:
    criterios_count = est.criterios.count()
    print(f"{est.codigo} - {est.nombre}: {criterios_count} criterios")

# Ver un estándar específico
th = Estandar.objects.get(codigo='TH')
print(f"\n{th.nombre}:")
for criterio in th.criterios.all():
    print(f"  {criterio.codigo} - {criterio.nombre}")
    print(f"    Complejidad: {criterio.complejidad}")
    print(f"    Obligatorio: {criterio.es_mandatorio}")
```

---

## 🔄 Actualizar o Agregar Nuevos Criterios

1. Abrir `normativity/fixtures_loader.py`
2. Ir a sección de **CRITERIOS** (línea ~140)
3. Agregar entrada en `criterios_por_estandar`
4. Ejecutar script nuevamente

**Ejemplo:**
```python
'TH': [
    # Criterios existentes...
    {
        'codigo': '1.4',
        'nombre': 'Nuevo criterio aquí',
        'descripcion': '...',
        'complejidad': 'MEDIA',
        'es_mandatorio': True,
        'aplica_todos': True,
        'requiere_evidencia_documental': False,
    },
]
```

---

## 🆘 Solución de Problemas

### "ModuleNotFoundError: No module named 'normativity'"
```bash
# Asegurarse que está en directorio correcto
cd portal_web_backend

# Y que normativity está en INSTALLED_APPS en settings.py
grep -r "normativity" backend/settings.py
```

### "ProgrammingError: relation normativity_estandar does not exist"
```bash
# Aplicar migraciones
python manage.py migrate normativity
```

### Encoding error (caracteres especiales)
Usar encoding UTF-8:
```python
exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())
```

### Quiero vaciar todo y recargar
```bash
python manage.py shell
```

```python
from normativity.models import Estandar, Criterio, DocumentoNormativo

# CUIDADO: Esto elimina TODOS los registros
Estandar.objects.all().delete()
Criterio.objects.all().delete()
DocumentoNormativo.objects.all().delete()

# Luego ejecutar
exec(open('normativity/fixtures_loader.py', encoding='utf-8').read())
```

---

## 📁 Estructura del Archivo

```
normativity/fixtures_loader.py
├── Configuración y estilos (líneas 1-40)
├── ESTÁNDARES (7 estándares, líneas 42-80)
├── CRITERIOS (21 criterios, líneas 82-320)
├── DOCUMENTOS NORMATIVOS (4 documentos, líneas 322-360)
└── RESUMEN FINAL (líneas 362-380)
```

---

## 🎓 Notas Técnicas

### Patrón get_or_create()
El script usa `get_or_create()` para ser idempotente:

```python
estandar, created = Estandar.objects.get_or_create(
    codigo=data['codigo'],  # Clave única
    defaults={...}           # Datos por defecto
)
```

**Resultado:**
- Si existe: `created=False` (no se modifica)
- Si no existe: `created=True` (se crea)

### Códigos Únicos
- **Estándares**: Código (ej: 'TH', 'INF')
- **Criterios**: Código + Estándar (ej: '1.1' dentro de 'TH')
- **Documentos**: Número de referencia (ej: 'Res3100-2019')

---

## 📞 Contacto

Para preguntas sobre fixtures o Resolución 3100:
- Revisar `PRODUCTION_DEPLOYMENT.md` para deployment completo
- Revisar `architecture.md` para arquitectura del sistema
- Revisar `agents.md` para roles del equipo

---

**✓ Fixture Loader Completamente Funcional**
*Compatible con Django 5.2.2+*
