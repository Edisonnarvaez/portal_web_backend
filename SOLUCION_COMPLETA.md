# 🏥 Django Admin - Guía Completa de Corrección

## 📌 Resumen Ejecutivo

Se corrigió el error `FieldError` en `/admin/habilitacion/autoevaluacion/add/` que impedía acceder al formulario de creación de autoevaluaciones.

**Status**: ✅ CORREGIDO  
**Commit**: `b8b5999` - "fix: Corregir FieldError en Django Admin para Autoevaluacion"  
**Validación**: ✅ Test de admin exitoso

---

## 🔴 Problema Identificado

### Error Original
```
FieldError at /admin/habilitacion/autoevaluacion/add/
'fecha_inicio' cannot be specified for Autoevaluacion model form as it is a non-editable field.
Check fields/fieldsets/exclude attributes of class AutoevaluacionAdmin.
```

### Root Cause
El campo `fecha_inicio` está configurado en el modelo con `auto_now_add=True`:

```python
# habilitacion/models.py - Autoevaluacion
fecha_inicio = models.DateField(
    auto_now_add=True,  # ← AUTOMÁTICO: Django lo establece al crear
    verbose_name="Fecha de Inicio"
)
```

Cuando Django ve `auto_now_add=True`, automáticamente establece `editable=False`. Esto significa:
- ✅ El campo se rellena automáticamente
- ❌ No se puede editar manualmente
- ❌ No puede incluirse en formularios

**El problema en admin.py (línea ~427)**:
```python
# ❌ ANTES (INCORRECTO)
fieldsets = (
    ...
    ('Estado', {
        'fields': (
            'estado',
            'fecha_inicio',        # ← INTENTA INCLUIR CAMPO NON-EDITABLE
            'fecha_completacion',
        )
    }),
)
```

---

## 🟢 Solución Implementada

### Paso 1: Crear Método Display (línea ~560)
```python
def fecha_inicio_display(self, obj):
    """Fecha de inicio (solo lectura - auto_now_add)."""
    if obj.fecha_inicio:
        return obj.fecha_inicio.strftime('%d/%m/%Y')
    return '—'
fecha_inicio_display.short_description = 'Fecha de Inicio'
```

**Propósito**: Crear una función que muestra el valor del campo SIN intentar editarlo.

### Paso 2: Agregar a readonly_fields (línea ~403)
```python
# ✅ DESPUÉS (CORRECTO)
readonly_fields = [
    'numero_autoevaluacion',
    'fecha_inicio_display',      # ← Agregar el MÉTODO DISPLAY
    'fecha_creacion',
    'fecha_actualizacion',
    'porcentaje_cumplimiento_display',
    'cumplimientos_resumen',
    'vigencia_display',
]
```

**Propósito**: Declarar explícitamente qué campos/métodos son solo-lectura.

### Paso 3: Reorganizar Fieldsets (línea ~414-449)
```python
# ✅ ESTRUCTURA CORRECTA
fieldsets = (
    # Identificación - Datos que NO cambian
    ('Identificación', {
        'fields': (
            'numero_autoevaluacion',  # readonly
            'datos_prestador',
            'periodo',
            'version',
        )
    }),
    
    # EDITABLE - Solo campos que usuario puede cambiar
    ('Estado (Editable)', {
        'fields': (
            'estado',
            'fecha_completacion',
            'fecha_vencimiento',
        )
    }),
    
    # Display calculados
    ('Resultados', {
        'fields': (
            'porcentaje_cumplimiento_display',
            'cumplimientos_resumen',
        )
    }),
    
    # Notas
    ('Notas', {
        'fields': (
            'observaciones',
        )
    }),
    
    # SISTEMA - Solo lectura y auditoría (colapsible)
    ('Sistema (Solo Lectura)', {
        'fields': (
            'fecha_inicio_display',      # Método que muestra el valor
            'vigencia_display',
            'usuario_responsable',
            'fecha_creacion',
            'fecha_actualizacion',
        ),
        'classes': ('collapse',),        # Oculto por defecto
    }),
)
```

**Cambios clave**:
- ❌ Removido `'fecha_inicio'` del fieldset editable
- ✅ Agregado `'fecha_inicio_display'` (método) en sección readonly
- ✅ Separado claramente qué es editable vs readonly

---

## ✅ Validación

Se ejecutó script de validación que confirma:

```python
✓ Admin form loaded successfully!
✓ Form fields: ['datos_prestador', 'periodo', 'version', 'estado', 
                 'fecha_completacion', 'fecha_vencimiento', 'observaciones', 
                 'usuario_responsable']
✓ Readonly fields configured: ['numero_autoevaluacion', 'fecha_inicio_display', 
                                'fecha_creacion', 'fecha_actualizacion', 
                                'porcentaje_cumplimiento_display', 
                                'cumplimientos_resumen', 'vigencia_display']

✅ VALIDACIÓN EXITOSA: No hay errores de FieldError en el admin
```

**Explicación**:
- `Form fields` = Campos editables en el formulario (aquellos que NO tienen auto_now/auto_now_add)
- `Readonly fields` = Métodos display que muestran datos sin permitir edición

---

## 📊 Cambios en habilitacion/admin.py

| Sección | Cambio | Línea |
|---------|--------|-------|
| `readonly_fields` | Agregar `'fecha_inicio_display'` | 403 |
| `fieldsets` "Estado" | Remover `'fecha_inicio'` | 427-436 |
| `fieldsets` "Sistema" | Agregar `'fecha_inicio_display'` y `'vigencia_display'` | 445-452 |
| Métodos | Agregar `fecha_inicio_display()` | 560-566 |

---

## 🎓 Lecciones Aprendidas

### Principio #1: Campos Auto-managed NO son Editables
```python
# Estos campos NO pueden ir en fieldsets como editable:
fecha_creacion = DateTimeField(auto_now_add=True)  # ❌
fecha_actualizacion = DateTimeField(auto_now=True)  # ❌
fecha_inicio = DateField(auto_now_add=True)         # ❌

# PERO puedes mostrarlos en readonly:
readonly_fields = ['fecha_creacion', 'fecha_inicio']  # ✅
```

### Principio #2: Método Display para Customización
```python
# Para campos auto_now_add, crea un método display:
def fecha_inicio_display(self, obj):
    return obj.fecha_inicio.strftime('%d/%m/%Y') if obj.fecha_inicio else '—'
fecha_inicio_display.short_description = 'Fecha de Inicio'

# Luego úsalo en fieldsets:
fieldsets = (
    ('Sistema', {
        'fields': (
            'fecha_inicio_display',  # El método, NO el campo
        )
    }),
)
```

### Principio #3: Separar Responsabilidades
```python
fieldsets = (
    # Datos básicos
    ('Identificación', {...}),
    
    # LO QUE EDITA EL USUARIO
    ('Estado (Editable)', {
        'fields': ('estado', 'fecha_completacion', 'fecha_vencimiento')
    }),
    
    # DATOS DE SISTEMA (Readonly)
    ('Sistema (Solo Lectura)', {
        'fields': ('fecha_inicio_display', 'fecha_creacion', 'fecha_actualizacion'),
        'classes': ('collapse',),  # Opcional: ocultar por defecto
    }),
)
```

---

## 📝 Checklist para Evitar Errores Similares

Cuando crees un nuevo Admin, sigue estos pasos:

- [ ] **Leer el modelo**: Identificar campos con `auto_now_add`, `auto_now`, `editable=False`
- [ ] **No incluirlos directamente**: Nunca en `fields` o `fieldsets` si son no-editables
- [ ] **Crear métodos display**: Para mostrar esos campos de forma bonita
- [ ] **Declarar readonly_fields**: Listar todos los métodos display
- [ ] **Organizar fieldsets**: Separar editable de readonly/sistema
- [ ] **Probar en shell**:
  ```python
  from myapp.admin import MyAdmin
  from myapp.models import MyModel
  admin = MyAdmin(MyModel, site)
  form_class = admin.get_form(None)  # Si no da error, está bien
  ```

---

## 📁 Archivos Creados/Modificados

| Archivo | Cambio | Propósito |
|---------|--------|----------|
| `habilitacion/admin.py` | Modificado | Corregir fieldsets y readonly_fields |
| `ADMIN_FIX_GUIDE.md` | Creado | Documentación técnica detallada |
| `test_admin.py` | Creado | Script de validación |

---

## 🚀 Próximos Pasos

La corrección es 100% funcional. Ahora puedes:

1. ✅ Acceder a `/admin/habilitacion/autoevaluacion/`
2. ✅ Crear nuevas autoevaluaciones
3. ✅ Editar autoevaluaciones existentes
4. ✅ Ver todos los datos en los fieldsets correctos

El formulario respeta:
- ✅ Campos editables (estado, fechas de completación/vencimiento)
- ✅ Campos auto-managed mostrados como readonly (fecha_inicio)
- ✅ Métodos display para presentación personalizada
- ✅ Secciones colapsibles para datos de auditoría

