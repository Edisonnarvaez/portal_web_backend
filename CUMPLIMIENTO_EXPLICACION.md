# 📊 ANÁLISIS COMPLETO: Cómo Funciona el CUMPLIMIENTO en Autoevaluaciones

## 🎯 Resumen Ejecutivo

El **Cumplimiento** es un registro que vincula:
- Una **Autoevaluación** (evaluación anual de una institución)
- Con un **Criterio** específico (ej: "1.1 - Disponibilidad de personal médico")
- En un **Servicio de Sede** específico (la ubicación física)

Y registra: **¿El servicio cumple o no con ese criterio?**

---

## 🏗️ Estructura de Datos (El Flujo)

```
AUTOEVALUACIÓN (AUT-5200101213-2024)
    │
    ├─ Período: 2024
    ├─ Versión: 2
    ├─ Estado: COMPLETADA
    ├─ Cumplimiento General: 85%
    │
    └─ CUMPLIMIENTOS (Relación 1 a MUCHOS)
        │
        ├─ Cumplimiento #1
        │   ├─ Criterio: 1.1 (Disponibilidad de personal médico)
        │   ├─ Servicio: Sala de Emergencias - Sede Principal
        │   ├─ Resultado: CUMPLE ✓
        │   ├─ Documento evidencia: Nómina de médicos.pdf
        │   └─ Fecha actualización: 2024-12-01
        │
        ├─ Cumplimiento #2
        │   ├─ Criterio: 1.2 (Capacitación continua)
        │   ├─ Servicio: Sala de Emergencias - Sede Principal
        │   ├─ Resultado: NO_CUMPLE ✗
        │   ├─ Hallazgo: Falta capacitación en protocolo de emergencias
        │   ├─ Plan de Mejora: Programar capacitación para enero 2025
        │   ├─ Responsable: Dr. Juan Pérez
        │   ├─ Fecha compromiso: 2025-01-31
        │   └─ Documento evidencia: Ninguno aún
        │
        ├─ Cumplimiento #3
        │   ├─ Criterio: 2.1 (Espacios adecuados)
        │   ├─ Servicio: Laboratorio - Sede Principal
        │   ├─ Resultado: PARCIALMENTE ⚠️
        │   ├─ Hallazgo: Laboratorio requiere ampliación de área
        │   ├─ Plan de Mejora: Presupuestar ampliación
        │   └─ Documento evidencia: Cotización de obras.pdf
        │
        └─ Cumplimiento #4 ... (y así sucesivamente)
```

---

## 🔑 Conceptos Clave

### 1. **¿Qué es un Cumplimiento?**

Un registro que dice: "En la evaluación 2024 de la institución XX, el Criterio YY evaluado en el Servicio ZZ tiene el siguiente resultado: CUMPLE / NO_CUMPLE / PARCIALMENTE / NO_APLICA"

### 2. **¿Cuántos Cumplimientos hay?**

Para cada Autoevaluación:
- **Criterios**: 21 (fijos de Resolución 3100)
- **Servicios de Sede**: Variable según la institución (ej: 3-5 servicios)
- **Total Cumplimientos**: 21 criterios × número de servicios

**Ejemplo:**
- Si la institución tiene 3 servicios: 21 × 3 = **63 cumplimientos**
- Si tiene 5 servicios: 21 × 5 = **105 cumplimientos**

### 3. **¿Cuál es la relación entre tablas?**

```
┌─────────────────────────────────────────────────────────┐
│ Autoevaluacion (AUT-5200101213-2024)                   │
│ ├─ id: 1                                               │
│ ├─ numero_autoevaluacion: "AUT-5200101213-2024"        │
│ ├─ periodo: 2024                                       │
│ ├─ version: 2                                          │
│ └─ estado: "COMPLETADA"                                │
└─────────────────────────────────────────────────────────┘
        │
        │ OneToMany: autoevaluacion_id
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ Cumplimiento (registra evaluación de criterio)          │
│ ├─ id: 47                                              │
│ ├─ autoevaluacion_id: 1 (FK)                           │
│ ├─ servicio_sede_id: 5 (FK)                            │
│ ├─ criterio_id: 12 (FK)                                │
│ ├─ cumple: "CUMPLE" | "NO_CUMPLE" | etc.              │
│ ├─ hallazgo: "..."                                     │
│ ├─ plan_mejora: "..."                                  │
│ └─ fecha_compromiso: 2025-01-31                        │
└─────────────────────────────────────────────────────────┘
        │
        ├─ FK: servicio_sede → ServicioSede
        ├─ FK: criterio → Criterio
        └─ M2M: documentos_evidencia → Documento
```

---

## 📋 Cómo se Crean los Cumplimientos

### Opción A: Manualmente en Admin

1. Ir a `/admin/habilitacion/autoevaluacion/`
2. Abrír una autoevaluación (ej: AUT-5200101213-2024)
3. En la sección "Cumplimientos" (si existe inline) agregar registros
4. O ir directamente a `/admin/habilitacion/cumplimiento/add/`
5. Seleccionar:
   - Autoevaluación: AUT-5200101213-2024
   - Servicio Sede: Emergencias - Sede Principal
   - Criterio: 1.1 Disponibilidad de personal médico
   - Resultado: CUMPLE
   - Documentos evidencia: (opcional)
6. Click "Save"

### Opción B: Mediante API REST

```bash
POST /api/habilitacion/cumplimientos/

{
  "autoevaluacion": 1,
  "servicio_sede": 5,
  "criterio": 12,
  "cumple": "CUMPLE",
  "hallazgo": "Personal médico disponible 24/7",
  "plan_mejora": null,
  "documentos_evidencia": [4, 5, 6]
}
```

### Opción C: Mediante Script Python

```python
from habilitacion.models import Autoevaluacion, Cumplimiento, ServicioSede
from normativity.models import Criterio

autoevaluacion = Autoevaluacion.objects.get(numero_autoevaluacion="AUT-5200101213-2024")
servicio = ServicioSede.objects.get(id=5)
criterio = Criterio.objects.get(codigo="1.1")

cumplimiento = Cumplimiento.objects.create(
    autoevaluacion=autoevaluacion,
    servicio_sede=servicio,
    criterio=criterio,
    cumple="CUMPLE",
    hallazgo="Disponible 24/7"
)
```

---

## 📊 Cómo se Visualiza en Admin

### Lista de Cumplimientos

```
┌────────────────────────────────────────────────────────────────────┐
│ /admin/habilitacion/cumplimiento/                                  │
├────────────────────────────────────────────────────────────────────┤
│ Criterio      │ Autoevaluación    │ Servicio      │ Resultado      │
├────────────────────────────────────────────────────────────────────┤
│ Est TH: 1.1   │ AUT-5200101213... │ Emergencias   │ ✓ CUMPLE       │
│ Est TH: 1.2   │ AUT-5200101213... │ Emergencias   │ ✗ NO_CUMPLE    │
│ Est TH: 1.3   │ AUT-5200101213... │ Emergencias   │ ⚠ PARCIALMENTE │
│ Est INF: 2.1  │ AUT-5200101213... │ Lab General   │ ✓ CUMPLE       │
│ Est INF: 2.2  │ AUT-5200101213... │ Lab General   │ - NO_APLICA    │
│ ...           │ ...               │ ...           │ ...            │
└────────────────────────────────────────────────────────────────────┘
```

### Detalle de Un Cumplimiento

```
┌──────────────────────────────────────────────────────────┐
│ EVALUAR: TH 1.1 - Disponibilidad de personal médico     │
├──────────────────────────────────────────────────────────┤
│ Autoevaluación: AUT-5200101213-2024                     │
│ Servicio: Emergencias - Sede Principal                  │
│ Criterio: 1.1 - Disponibilidad de personal médico       │
│                                                          │
│ ─── RESULTADO ───                                       │
│ Resultado: [▼ CUMPLE ]                                  │
│ Hallazgo: "Personal disponible 24/7, 3 médicos en ..."  │
│                                                          │
│ ─── PLAN DE MEJORA ───                                  │
│ Plan de Mejora: (vacío - no hay deficiencias)           │
│ Responsable: -(vacío)                                   │
│ Fecha Compromiso: -(vacío)                              │
│                                                          │
│ ─── DOCUMENTOS DE EVIDENCIA ───                         │
│ ✓ nomina-medicos-2024.pdf                               │
│ ✓ certificados-especialidad.pdf                         │
│                                                          │
│ ─── AUDITORÍA ───                                       │
│ Creado: 2024-12-01 14:30:00                             │
│ Actualizado: 2024-12-10 09:15:00                        │
└──────────────────────────────────────────────────────────┘
```

---

## 🔢 El Cálculo: porcentaje_cumplimiento()

```python
# En habilitacion/models.py → Autoevaluacion.porcentaje_cumplimiento()

def porcentaje_cumplimiento(self):
    """Calcular porcentaje general de cumplimiento."""
    
    # Paso 1: Contar TOTAL de cumplimientos
    total = self.cumplimientos.count()
    # Ejemplo: 63 cumplimientos (21 criterios × 3 servicios)
    
    # Paso 2: Si no hay cumplimientos, retornar 0
    if total == 0:
        return 0  # División por cero evitada
    
    # Paso 3: Contar cuántos tienen cumple=True
    cumplidos = self.cumplimientos.filter(cumple=True).count()
    # Ejemplo: 54 cumplimientos tienen cumple="CUMPLE"
    
    # Paso 4: Calcular porcentaje
    porcentaje = (cumplidos / total) * 100
    # Cálculo: (54 / 63) * 100 = 85.7%
    
    return porcentaje
```

---

## 🎯 Por Qué No Ves Cumplimiento en la Autoevaluación

### Razón #1: NO HAY CUMPLIMIENTOS CREADOS

**Situación:**
- Creaste una autoevaluación
- Pero NO creaste registros en Cumplimiento
- Por eso el porcentaje = 0%

**Solución:**
```python
# Ver cuántos cumplimientos hay
from habilitacion.models import Autoevaluacion

auto = Autoevaluacion.objects.get(numero_autoevaluacion="AUT-5200101213-2024")
print(f"Total cumplimientos: {auto.cumplimientos.count()}")
# Si imprime 0, entonces no hay cumplimientos creados
```

### Razón #2: El CAMPO NO ESTÁ EN LA LISTA ADMIN

**Solución:**
```python
# En habilitacion/admin.py → AutoevaluacionAdmin

list_display = [
    'numero_autoevaluacion_link',
    'prestador_codigo',
    'periodo',
    'version',
    'estado',
    'porcentaje_cumplimiento_bar',  # ← Esto muestra el %
    'cumplimientos_resumen',         # ← Esto muestra resumen
    'fecha_vencimiento_display',
    'vigencia_display',
]
```

---

## 📊 Ejemplo Real: Desde Cero

### 1. CREAR AUTOEVALUACIÓN

```python
from habilitacion.models import Autoevaluacion, DatosPrestador
from datetime import date, timedelta

# Obtener datos del prestador
datos = DatosPrestador.objects.get(codigo_reps="5200101213")

# Crear autoevaluación
auto = Autoevaluacion.objects.create(
    datos_prestador=datos,
    periodo=2024,
    version=1,
    numero_autoevaluacion="AUT-5200101213-2024",
    fecha_vencimiento=date(2025, 12, 31),
    estado="EN_PROCESO"
)

print(f"Autoevaluación creada: {auto.numero_autoevaluacion}")
print(f"Cumplimientos: {auto.cumplimientos.count()}")  # Imprime: 0
print(f"Porcentaje: {auto.porcentaje_cumplimiento()}%")  # Imprime: 0%
```

### 2. CREAR CUMPLIMIENTOS (Uno por Uno)

```python
from habilitacion.models import Cumplimiento, ServicioSede
from normativity.models import Criterio

# Obtener servicios y criterios
emergencias = ServicioSede.objects.get(nombre_servicio="Emergencias")
criterio_11 = Criterio.objects.get(codigo="1.1")

# Crear cumplimiento
cumpl = Cumplimiento.objects.create(
    autoevaluacion=auto,
    servicio_sede=emergencias,
    criterio=criterio_11,
    cumple="CUMPLE",
    hallazgo="Personal disponible 24/7"
)

print(f"Cumplimiento creado: {cumpl}")
print(f"Total cumplimientos ahora: {auto.cumplimientos.count()}")  # Imprime: 1
print(f"Porcentaje: {auto.porcentaje_cumplimiento()}%")  # Imprime: ~1.6% (1/63)
```

### 3. CREAR CUMPLIMIENTOS EN BATCH

```python
from habilitacion.models import ServicioSede
from normativity.models import Criterio

# Obtener todos los servicios y criterios
servicios = ServicioSede.objects.filter(autoevaluacion=auto)
criterios = Criterio.objects.all()

# Crear cumplimiento para cada servicio × criterio
for servicio in servicios:
    for criterio in criterios:
        Cumplimiento.objects.create(
            autoevaluacion=auto,
            servicio_sede=servicio,
            criterio=criterio,
            cumple="CUMPLE"  # O lo que sea
        )

# Después de esto:
print(f"Total cumplimientos: {auto.cumplimientos.count()}")
# Imprime: 21 × número_de_servicios
print(f"Porcentaje: {auto.porcentaje_cumplimiento()}%")
# Imprime: 100% (todos en "CUMPLE")
```

---

## 🔍 Debugging: Cómo Verificar

### En Django Shell

```python
from habilitacion.models import Autoevaluacion, Cumplimiento

# 1. Ver todas las autoevaluaciones
auto_list = Autoevaluacion.objects.all()
for auto in auto_list:
    cumpl_count = auto.cumplimientos.count()
    porcentaje = auto.porcentaje_cumplimiento()
    print(f"{auto.numero_autoevaluacion}: {cumpl_count} cumplimientos, {porcentaje}%")

# 2. Ver detalle de una autoevaluación
auto = Autoevaluacion.objects.get(numero_autoevaluacion="AUT-5200101213-2024")

print(f"Autoevaluación: {auto.numero_autoevaluacion}")
print(f"Total cumplimientos: {auto.cumplimientos.count()}")
print(f"Porcentaje: {auto.porcentaje_cumplimiento()}%")

# 3. Ver desglose por resultado
print("\nDesglose por resultado:")
for resultado in ["CUMPLE", "NO_CUMPLE", "PARCIALMENTE", "NO_APLICA"]:
    count = auto.cumplimientos.filter(cumple=resultado).count()
    print(f"  {resultado}: {count}")

# 4. Ver cumplimientos específicos
print("\nCumplimientos con NO_CUMPLE:")
for cumpl in auto.cumplimientos.filter(cumple="NO_CUMPLE"):
    print(f"  - {cumpl.criterio.codigo}: {cumpl.servicio_sede.nombre_servicio}")

# 5. Ver si hay planes de mejora pendientes
print("\nPlanes de mejora pendientes:")
for cumpl in auto.cumplimientos.filter(plan_mejora__isnull=False):
    if cumpl.mejora_vencida():
        print(f"  - ⚠️ VENCIDA: {cumpl.criterio.codigo}")
    else:
        print(f"  - ✓ En progreso: {cumpl.criterio.codigo}")
```

---

## 🎨 Visualización en Admin

### Opción 1: Desde la Autoevaluación
```
/admin/habilitacion/autoevaluacion/1/change/

Aquí verás (si está configurado):
  ├─ Número: AUT-5200101213-2024
  ├─ Estado: COMPLETADA
  ├─ Cumplimiento: [████████░░] 85% (ver en barra)
  ├─ Resumen: "54 CUMPLE, 6 NO_CUMPLE, 3 PARCIALMENTE"
  └─ Inline (si existe):
      ├─ Cumplimiento #1: TH 1.1 → CUMPLE
      ├─ Cumplimiento #2: TH 1.2 → NO_CUMPLE
      └─ ...
```

### Opción 2: Desde el Listado de Cumplimientos
```
/admin/habilitacion/cumplimiento/?autoevaluacion__numero_autoevaluacion=AUT-5200101213-2024

Aquí verás todos los cumplimientos de esa evaluación:
  ├─ TH 1.1 | AUT-5200101213-2024 | Emergencias | CUMPLE ✓
  ├─ TH 1.2 | AUT-5200101213-2024 | Emergencias | NO_CUMPLE ✗
  ├─ TH 1.3 | AUT-5200101213-2024 | Emergencias | PARCIALMENTE ⚠
  └─ ...
```

---

## 💡 Resumen Final

| Concepto | Explicación |
|----------|-------------|
| **Autoevaluación** | Evaluación anual de una institución (una por año/versión) |
| **Cumplimiento** | Evaluación de UN criterio en UN servicio dentro de una autoevaluación |
| **¿Cuántos?** | 21 criterios × número de servicios = total cumplimientos |
| **Resultado** | CUMPLE \| NO_CUMPLE \| PARCIALMENTE \| NO_APLICA |
| **Porcentaje** | (CUMPLE / total) × 100 |
| **Evidencia** | Documentos que prueban el cumplimiento |
| **Plan Mejora** | Para los NO_CUMPLE: qué se va a hacer, quién y cuándo |

---

**¿Aún tienes dudas? Pregúntame:**
- ¿Cómo creo cumplimientos en batch?
- ¿Cómo calculo el % por estándar?
- ¿Cómo exporto un reporte de cumplimientos?
- ¿Cómo vinculo documentos a cumplimientos?
