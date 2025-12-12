# 🔧 Django Admin - Corrección de FieldError en Autoevaluacion

## ❌ Problema Original

**Error**: `FieldError: 'fecha_inicio' cannot be specified for Autoevaluacion model form as it is a non-editable field.`

**Ubicación**: `/admin/habilitacion/autoevaluacion/add/`

**Causa**: El campo `fecha_inicio` en el modelo tiene `auto_now_add=True`, lo que lo hace automáticamente **no-editable**. Sin embargo, estaba siendo incluido en el fieldset de formulario como si fuera editable.

```python
# En models.py
fecha_inicio = models.DateField(
    auto_now_add=True,  # ← NO EDITABLE
    verbose_name="Fecha de Inicio"
)

# En admin.py (INCORRECTO)
fieldsets = (
    ('Estado', {
        'fields': (
            'estado',
            'fecha_inicio',  # ← ERROR: No puede estar aquí
            'fecha_completacion',
        )
    }),
)
```

---

## ✅ Solución Implementada

### Paso 1: Crear Método Display para Mostrar el Campo

Se creó un método `fecha_inicio_display()` que permite mostrar el campo sin intentar editarlo:

```python
def fecha_inicio_display(self, obj):
    """Fecha de inicio (solo lectura - auto_now_add)."""
    if obj.fecha_inicio:
        return obj.fecha_inicio.strftime('%d/%m/%Y')
    return '—'
fecha_inicio_display.short_description = 'Fecha de Inicio'
```

### Paso 2: Declarar en readonly_fields

Todos los campos/métodos que son solo-lectura deben declararse:

```python
readonly_fields = [
    'numero_autoevaluacion',
    'fecha_inicio_display',      # ← Método display (NO el campo directo)
    'fecha_creacion',
    'fecha_actualizacion',
    'porcentaje_cumplimiento_display',
    'cumplimientos_resumen',
    'vigencia_display',
]
```

### Paso 3: Reorganizar Fieldsets

Separar en dos secciones: **Datos Editables** y **Datos Solo-Lectura**:

```python
fieldsets = (
    ('Identificación', {
        'fields': (
            'numero_autoevaluacion',
            'datos_prestador',
            'periodo',
            'version',
        )
    }),
    # EDITABLE - Solo campos que el usuario puede cambiar
    ('Estado (Editable)', {
        'fields': (
            'estado',
            'fecha_completacion',
            'fecha_vencimiento',
        )
    }),
    ('Resultados', {
        'fields': (
            'porcentaje_cumplimiento_display',
            'cumplimientos_resumen',
        )
    }),
    ('Notas', {
        'fields': (
            'observaciones',
        )
    }),
    # READONLY - Datos de control y auditoría (collapsible)
    ('Sistema (Solo Lectura)', {
        'fields': (
            'fecha_inicio_display',
            'vigencia_display',
            'usuario_responsable',
            'fecha_creacion',
            'fecha_actualizacion',
        ),
        'classes': ('collapse',),
    }),
)
```

---

## 📋 Cambios Realizados

| Cambio | Ubicación | Detalles |
|--------|-----------|---------|
| Agregado | `fecha_inicio_display()` | Nuevo método para mostrar readonly |
| Actualizado | `readonly_fields` | Agregado `'fecha_inicio_display'` |
| Reorganizado | `fieldsets` | Separados datos editables de readonly |
| Eliminado | De `Estado` fieldset | Campo `fecha_inicio` (no-editable) |
| Agregado | En `Sistema` fieldset | Métodos display para campos readonly |

---

## ✅ Validación

Se ejecutó test de validación que confirma:

```
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

---

## 📚 Buenas Prácticas Para Evitar Este Error

### 1. **Identificar Campos Auto-managed**
- `auto_now_add=True` → Establecido al crear, inmutable
- `auto_now=True` → Se actualiza automáticamente
- `editable=False` → Nunca editable por usuario

### 2. **Nunca Incluyas Campos Non-editable Directamente**
```python
# ❌ MAL
fieldsets = (
    ('Estado', {
        'fields': (
            'fecha_creacion',      # auto_now_add=True - ERROR
            'fecha_inicio',        # auto_now_add=True - ERROR
        )
    }),
)

# ✅ BIEN
readonly_fields = [
    'fecha_creacion_display',  # Método que muestra el valor
    'fecha_inicio_display',
]

fieldsets = (
    ('Sistema (Readonly)', {
        'fields': (
            'fecha_creacion_display',  # Usar el método, no el campo
            'fecha_inicio_display',
        )
    }),
)
```

### 3. **Organiza Fieldsets por Tipo**
```python
fieldsets = (
    # Datos básicos editables
    ('Datos Principales', {...}),
    
    # Más datos editables
    ('Configuración', {...}),
    
    # Solo lectura (opcionalmente collapsible)
    ('Sistema (Solo Lectura)', {
        'fields': (...),
        'classes': ('collapse',),  # Opcional: ocultar por defecto
    }),
)
```

### 4. **Checklist Antes de Crear un Admin**

- [ ] Revisar modelo: ¿Qué campos tienen `auto_now_add` o `auto_now`?
- [ ] Crear métodos `display()` para esos campos
- [ ] Agregar los métodos a `readonly_fields`
- [ ] En fieldsets: incluir SOLO campos editables (nunca auto_now/auto_now_add)
- [ ] Usar nombres de métodos display en fieldsets, NO nombres de campos
- [ ] Probar: `python manage.py shell` → importar Admin → verificar

---

## 🎯 Resultado Final

El formulario de admin ahora:
- ✅ Se carga sin errores
- ✅ Muestra todos los campos necesarios
- ✅ Separa claramente qué es editable vs solo-lectura
- ✅ Permite ocultar sección de auditoría (collapse)
- ✅ Respeta las restricciones del modelo (`auto_now_add`, etc.)

