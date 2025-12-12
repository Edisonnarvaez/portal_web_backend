╔══════════════════════════════════════════════════════════════════════════════╗
║             ✅ AUTOEVALUACIÓN - NOMBRES MOSTRADOS CORRECTAMENTE               ║
╚══════════════════════════════════════════════════════════════════════════════╝

## 🔴 Problema
Los nombres de autoevaluación no se estaban mostrando en el admin:

    /admin/habilitacion/autoevaluacion/
    
    Mostraba:
    - AUTOEVALUACIÓN: (en blanco)
    - PRESTADOR: (en blanco)
    - PERÍODO: 2024
    - VERSIÓN: 2
    - ESTADO: BORRADOR

## 🟢 Causa
El campo `numero_autoevaluacion` estaba vacío porque:
1. No se generaba automáticamente al crear la autoevaluación
2. Los registros existentes fueron creados sin este valor

## ✅ Solución Implementada

### Paso 1: Agregar método save() al modelo (habilitacion/models.py)

```python
def save(self, *args, **kwargs):
    """Generar automáticamente el número de autoevaluación si no existe."""
    if not self.numero_autoevaluacion:
        self.numero_autoevaluacion = f"AUT-{self.datos_prestador.codigo_reps}-{self.periodo}"
    super().save(*args, **kwargs)
```

**Beneficio**: Ahora toda autoevaluación nueva generará automáticamente su número
con formato: `AUT-CODIGO_REPS-PERIODO`

### Paso 2: Actualizar registros existentes

Se ejecutó script para llenar el campo `numero_autoevaluacion` en registros existentes:

```python
for auto in Autoevaluacion.objects.all():
    if not auto.numero_autoevaluacion:
        auto.numero_autoevaluacion = f'AUT-{auto.datos_prestador.codigo_reps}-{auto.periodo}'
        auto.save()
```

**Resultado**: 
- Autoevaluación 1: `AUT-5200101213-2024` (v1)
- Autoevaluación 2: `AUT-5200101213-2024` (v2)

## 📊 Resultado Final

Ahora en `/admin/habilitacion/autoevaluacion/` se muestra:

```
╔════════════════════════════════════════════════════════════════╗
║ AUTOEVALUACIÓN        PRESTADOR    PERÍODO  VERSIÓN  ESTADO  ║
╠════════════════════════════════════════════════════════════════╣
║ AUT-5200101213-2024   5200101213   2024     2        BORRADOR║
║ AUT-5200101213-2024   5200101213   2024     1        EN CURSO║
╚════════════════════════════════════════════════════════════════╝
```

✅ **Ahora se muestran correctamente:**
- Número de autoevaluación (ej: AUT-5200101213-2024)
- Código del prestador (ej: 5200101213)
- Período fiscal (ej: 2024)
- Versión (ej: 1, 2)
- Estado (BORRADOR, EN CURSO, COMPLETADA, etc.)

## 🎓 Cómo Funciona

1. **Cuando creas una nueva autoevaluación en el admin**:
   - Django llama a `save()`
   - Se verifica si `numero_autoevaluacion` está vacío
   - Si lo está, se genera automáticamente
   - Se guarda en la BD

2. **En el formulario de admin**:
   - El campo `numero_autoevaluacion` es `readonly`
   - Se muestra automáticamente generado
   - El usuario no lo puede editar

## 📋 Cambios Realizados

| Archivo | Cambio | Propósito |
|---------|--------|----------|
| habilitacion/models.py | Agregar método save() | Generar número automáticamente |
| BD (data migration) | Actualizar registros | Llenar campos vacíos |
| habilitacion/admin.py | Sin cambios | Ya estaba configurado correctamente |

## 🚀 Git Commit

Commit: `fef8d37`
Mensaje: "feat: Generar automáticamente numero_autoevaluacion en modelo"

## 📝 Patrón Reutilizable

Este patrón es útil para otros campos que se deben generar automáticamente:

```python
def save(self, *args, **kwargs):
    """Generar automáticamente campos si no existen."""
    if not self.campo_generado:
        self.campo_generado = self.generar_valor()
    super().save(*args, **kwargs)

def generar_valor(self):
    """Lógica para generar el valor."""
    return f"PREFIJO-{self.id}-{self.fecha.year}"
```

╔══════════════════════════════════════════════════════════════════════════════╗
║         ✅ AUTOEVALUACIONES YA MUESTRAN CORRECTAMENTE EN EL ADMIN            ║
╚══════════════════════════════════════════════════════════════════════════════╝
