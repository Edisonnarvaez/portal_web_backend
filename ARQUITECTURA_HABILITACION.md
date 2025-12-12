╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║    📐 ARQUITECTURA: Habilitación con Company y Headquarters                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

## 🎯 Problema Resuelto

El sistema ahora soporta dos escenarios de habilitación:

✅ **Escenario 1: Una sola sede**
   - Una empresa tiene una sola ubicación física
   - Un único prestador (habilitación) para toda la empresa

✅ **Escenario 2: Múltiples sedes**
   - Una empresa tiene varias ubicaciones (Bogotá, Medellín, Cali, etc.)
   - Cada sede puede tener su propia habilitación
   - Cada sede es un prestador independiente

═══════════════════════════════════════════════════════════════════════════════

## 🏗️ Estructura de Datos

```
COMPANY (Empresa)
│
├─ Nombre: "Clínica Integral de Salud"
├─ NIT: "9009876543"
├─ Razón Social: "Clínica Integral de Salud S.A.S."
├─ Estado: Activa
│
└─ HEADQUARTERS (Sedes - OneToMany)
   │
   ├─ Sede #1: "Sede Principal" (Bogotá)
   │   │
   │   └─ DATOS PRESTADOR (OneToOne)
   │       ├─ Código REPS: "9009876543-001"
   │       ├─ Clase: "IPS"
   │       ├─ Estado Habilitación: "HABILITADA"
   │       └─ Autoevaluaciones: [2024 v1, 2024 v2, 2025 v1]
   │
   ├─ Sede #2: "Sede Medellín"
   │   │
   │   └─ DATOS PRESTADOR (OneToOne)
   │       ├─ Código REPS: "9009876543-002"
   │       ├─ Clase: "IPS"
   │       ├─ Estado Habilitación: "EN_PROCESO"
   │       └─ Autoevaluaciones: [2024 v1]
   │
   └─ Sede #3: "Sede Cali"
       │
       └─ DATOS PRESTADOR (OneToOne)
           ├─ Código REPS: "9009876543-003"
           ├─ Clase: "IPS"
           ├─ Estado Habilitación: "SUSPENDIDA"
           └─ Autoevaluaciones: []
```

═══════════════════════════════════════════════════════════════════════════════

## 📊 Relaciones en Base de Datos

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  COMPANY (companies_company)                                     │
│  ├─ id: PK                                                       │
│  ├─ nombre: VARCHAR                                              │
│  ├─ nit: VARCHAR (UNIQUE)                                        │
│  └─ ...                                                          │
│                                                                  │
│  ↓ OneToMany                                                     │
│                                                                  │
│  HEADQUARTERS (companies_headquarters)                           │
│  ├─ id: PK                                                       │
│  ├─ company_id: FK → COMPANY                                     │
│  ├─ codigo: VARCHAR                                              │
│  ├─ nombre: VARCHAR                                              │
│  ├─ direccion: VARCHAR                                           │
│  └─ ...                                                          │
│                                                                  │
│  ↓ OneToOne                                                      │
│                                                                  │
│  DATOS PRESTADOR (habilitacion_datosprestador)                   │
│  ├─ id: PK                                                       │
│  ├─ headquarters_id: FK → HEADQUARTERS (UNIQUE)                  │
│  ├─ codigo_reps: VARCHAR (UNIQUE)                                │
│  ├─ clase_prestador: CHAR                                        │
│  ├─ estado_habilitacion: VARCHAR                                 │
│  └─ ...                                                          │
│                                                                  │
│  ↓ OneToMany                                                     │
│                                                                  │
│  AUTOEVALUACION (habilitacion_autoevaluacion)                    │
│  ├─ id: PK                                                       │
│  ├─ datos_prestador_id: FK → DATOS PRESTADOR                     │
│  ├─ periodo: INT (YEAR)                                          │
│  ├─ version: INT                                                 │
│  └─ ...                                                          │
│                                                                  │
│  ↓ OneToMany                                                     │
│                                                                  │
│  CUMPLIMIENTO (habilitacion_cumplimiento)                        │
│  ├─ id: PK                                                       │
│  ├─ autoevaluacion_id: FK → AUTOEVALUACION                       │
│  ├─ criterio_id: FK → CRITERIO                                   │
│  └─ ...                                                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

═══════════════════════════════════════════════════════════════════════════════

## 🔑 Cambios Principales

### Antes (Architecture anterior)
```python
class DatosPrestador(models.Model):
    company = models.OneToOneField(Company, ...)  # ❌ Acoplado a empresa
    # ...
```

**Problema:** Una empresa = Un prestador. No funciona para múltiples sedes.

### Después (Arquitectura actual)
```python
class DatosPrestador(models.Model):
    headquarters = models.OneToOneField(Headquarters, ...)  # ✅ Acoplado a sede
    # ...
```

**Ventaja:** Una empresa → Varias sedes → Varios prestadores.

═══════════════════════════════════════════════════════════════════════════════

## 💾 Ejemplo de Datos en BD

### Tabla: companies_company
```
┌────┬───────────────────────────────────────┬──────────────┐
│ id │ nombre                                │ nit          │
├────┼───────────────────────────────────────┼──────────────┤
│ 1  │ Clínica Integral de Salud             │ 9009876543   │
│ 2  │ Hospital Regional del Sur             │ 9008765432   │
└────┴───────────────────────────────────────┴──────────────┘
```

### Tabla: companies_headquarters
```
┌────┬────────────┬────────────────────┬─────────────────────────┐
│ id │ company_id │ codigo             │ nombre                  │
├────┼────────────┼────────────────────┼─────────────────────────┤
│ 1  │ 1          │ SEDE-001           │ Sede Principal (Bogotá) │
│ 2  │ 1          │ SEDE-002           │ Sede Medellín           │
│ 3  │ 1          │ SEDE-003           │ Sede Cali               │
│ 4  │ 2          │ SEDE-001           │ Hospital Principal      │
└────┴────────────┴────────────────────┴─────────────────────────┘
```

### Tabla: habilitacion_datosprestador
```
┌────┬─────────────────┬────────────────┬──────────────────────────┐
│ id │ headquarters_id │ codigo_reps    │ estado_habilitacion      │
├────┼─────────────────┼────────────────┼──────────────────────────┤
│ 1  │ 1               │ 9009876543-001 │ HABILITADA               │
│ 2  │ 2               │ 9009876543-002 │ EN_PROCESO               │
│ 3  │ 3               │ 9009876543-003 │ SUSPENDIDA               │
│ 4  │ 4               │ 9008765432-001 │ HABILITADA               │
└────┴─────────────────┴────────────────┴──────────────────────────┘
```

### Tabla: habilitacion_autoevaluacion
```
┌────┬──────────────────┬──────────────────────────┬─────────┐
│ id │ datos_prestador_ │ numero_autoevaluacion    │ periodo │
│    │ id               │                          │         │
├────┼──────────────────┼──────────────────────────┼─────────┤
│ 1  │ 1                │ AUT-9009876543-001-2024  │ 2024    │
│ 2  │ 1                │ AUT-9009876543-001-2024  │ 2024    │ (v2)
│ 3  │ 2                │ AUT-9009876543-002-2024  │ 2024    │
└────┴──────────────────┴──────────────────────────┴─────────┘
```

═══════════════════════════════════════════════════════════════════════════════

## 🎯 Casos de Uso

### Caso 1: Empresa con una sola sede
```
Clínica de Ortopedia
├─ Sede Principal (única)
   └─ Datos Prestador: HABILITADA
      └─ Autoevaluación 2024: 100%
```

### Caso 2: Hospital con múltiples sedes
```
Red de Hospitales del Centro
├─ Sede Bogotá
│  └─ Datos Prestador: HABILITADA
│     ├─ Autoevaluación 2024: 95%
│     └─ Autoevaluación 2025: 98%
├─ Sede Medellín
│  └─ Datos Prestador: EN_PROCESO
│     ├─ Autoevaluación 2024: 70%
│     └─ Plan de mejora activo
└─ Sede Cali
   └─ Datos Prestador: SUSPENDIDA
      └─ Última Autoevaluación 2023: 45%
```

### Caso 3: Profesional independiente
```
Dr. Juan Pérez (Consultorio)
├─ Sede Única (Consultorio)
   └─ Datos Prestador: HABILITADA
      └─ Autoevaluación 2024: 88%
```

═══════════════════════════════════════════════════════════════════════════════

## 🔄 Flujos de Trabajo

### Flujo 1: Crear nueva empresa con una sede
```
1. Crear Company
   ├─ Nombre: "Nueva Clínica"
   ├─ NIT: "9009876543"
   └─ Estado: Activa

2. Crear Headquarters (asociada a Company)
   ├─ Código: "SEDE-001"
   ├─ Nombre: "Sede Principal"
   └─ Dirección: "..."

3. Crear DatosPrestador (asociado a Headquarters)
   ├─ Headquarters: Sede Principal
   ├─ Código REPS: "9009876543"
   ├─ Clase: "IPS"
   └─ Estado: "EN_PROCESO"

4. Crear Autoevaluación
   ├─ Datos Prestador: (del paso 3)
   ├─ Período: 2024
   └─ Versión: 1
```

### Flujo 2: Agregar nueva sede a empresa existente
```
1. Crear nueva Headquarters (asociada a Company existente)
   ├─ Company: "Clínica Integral de Salud"
   ├─ Código: "SEDE-002"
   ├─ Nombre: "Sede Medellín"
   └─ ...

2. Crear DatosPrestador (para nueva sede)
   ├─ Headquarters: "Sede Medellín"
   ├─ Código REPS: "9009876543-002"
   ├─ ...

3. Crear Autoevaluación para nueva sede
   └─ Datos Prestador: (del paso 2)

RESULTADO: Ahora empresa tiene 2 prestadores independientes
```

═══════════════════════════════════════════════════════════════════════════════

## 📱 Cómo se ve en el Admin

### Listar Prestadores (DatosPrestador)
```
/admin/habilitacion/datosprestador/

┌─────────────┬──────────────────────┬────────────────┬──────────────────────┐
│ Código REPS │ Sede (Headquarters)  │ Clase          │ Estado Habilitación  │
├─────────────┼──────────────────────┼────────────────┼──────────────────────┤
│ 9009876543- │ Sede Principal       │ IPS            │ ✅ HABILITADA        │
│ 001         │ (Bogotá)             │                │                      │
├─────────────┼──────────────────────┼────────────────┼──────────────────────┤
│ 9009876543- │ Sede Medellín        │ IPS            │ 🔄 EN_PROCESO        │
│ 002         │ (Medellín)           │                │                      │
├─────────────┼──────────────────────┼────────────────┼──────────────────────┤
│ 9008765432- │ Hospital Principal   │ IPS            │ ✅ HABILITADA        │
│ 001         │ (Cali)               │                │                      │
└─────────────┴──────────────────────┴────────────────┴──────────────────────┘
```

### Ver detalles de un Prestador
```
/admin/habilitacion/datosprestador/1/change/

┌─────────────────────────────────────────────────────┐
│ DATOS DE PRESTADOR                                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Identificación REPS                                 │
│ ├─ Sede: [Sede Principal ▼]                        │
│ ├─ Código REPS: 9009876543-001                      │
│ └─ Clase Prestador: [IPS ▼]                         │
│                                                     │
│ Estado de Habilitación                              │
│ ├─ Estado: ✅ HABILITADA                            │
│ ├─ Inscripción REPS: 2020-01-15                     │
│ ├─ Renovación: 2024-01-15                           │
│ └─ Vencimiento: 2025-12-31                          │
│                                                     │
│ Responsabilidad Civil                               │
│ ├─ Aseguradora: Seguros La Confianza                │
│ ├─ Póliza: POL-2024-001234                          │
│ └─ Vigencia: 2025-12-31                             │
│                                                     │
│ [SAVE] [SAVE AND ADD ANOTHER] [SAVE AND CONTINUE]   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

═══════════════════════════════════════════════════════════════════════════════

## 🔗 Relación con Autoevaluaciones

Cada DatosPrestador (= Una Sede) puede tener múltiples Autoevaluaciones:

```
DatosPrestador
├─ Código REPS: "9009876543-001"
│
└─ Autoevaluaciones (OneToMany)
   ├─ AUT-9009876543-001-2024 (v1)
   │  ├─ 63 Cumplimientos
   │  └─ Porcentaje: 75%
   │
   ├─ AUT-9009876543-001-2024 (v2)
   │  ├─ 63 Cumplimientos
   │  └─ Porcentaje: 85%
   │
   └─ AUT-9009876543-001-2025 (v1)
      ├─ 63 Cumplimientos
      └─ Porcentaje: 90%
```

VENTAJA: Cada sede tiene su propio histórico de evaluaciones.

═══════════════════════════════════════════════════════════════════════════════

## 📝 Queries Útiles

### Ver todos los prestadores
```python
from habilitacion.models import DatosPrestador

prestadores = DatosPrestador.objects.all()
for p in prestadores:
    print(f"{p.codigo_reps} - {p.headquarters.nombre} ({p.estado_habilitacion})")
```

### Ver prestadores de una empresa
```python
from companies.models import Company
from habilitacion.models import DatosPrestador

company = Company.objects.get(nombre="Clínica Integral de Salud")
prestadores = DatosPrestador.objects.filter(headquarters__company=company)

for p in prestadores:
    print(f"{p.headquarters.nombre}: {p.estado_habilitacion}")
```

### Ver todas las sedes de una empresa
```python
from companies.models import Company

company = Company.objects.get(nombre="Clínica Integral de Salud")
sedes = company.headquarters.all()

for sede in sedes:
    if hasattr(sede, 'datos_habilitacion'):
        print(f"{sede.nombre}: {sede.datos_habilitacion.estado_habilitacion}")
    else:
        print(f"{sede.nombre}: Sin habilitación")
```

═══════════════════════════════════════════════════════════════════════════════

## ✅ Ventajas de esta Arquitectura

| Aspecto | Ventaja |
|---------|---------|
| **Escalabilidad** | Soporta 1 o N sedes por empresa |
| **Independencia** | Cada sede puede estar habilitada o no |
| **Histórico** | Cada sede mantiene su historia de evaluaciones |
| **Reportes** | Comparar desempeño entre sedes |
| **Flexibilidad** | Agregar sedes sin afectar existentes |
| **Realismo** | Refleja estructura real de hospitales/clínicas |

═══════════════════════════════════════════════════════════════════════════════

## 🚀 Próximas Mejoras Posibles

1. **Dashboard comparativo** de sedes
2. **Reportes agregados** por empresa
3. **Alertas por sede** con vencimientos próximos
4. **Métricas por empresa** (promedio, máx, mín)
5. **Planes de mejora** coordinados entre sedes
6. **Auditoría integrada** a nivel empresa

═══════════════════════════════════════════════════════════════════════════════

**Conclusión:** La arquitectura ahora es flexible, escalable y realista.
Soporta tanto pequeños consultorios como grandes redes hospitalarias.
