# 📊 ANÁLISIS - Flujo Cascada de Soportes Documentales

**Fecha:** 10 Abril 2026  
**Pregunta:** ¿Los modelos actuales permiten el flujo cascada Empresa → Sede → Servicio?  
**Respuesta:** ⚠️ PARCIALMENTE (con limitaciones críticas)

---

## 🔍 ESTRUCTURA ACTUAL DE MODELOS

```
┌─────────────────────────────────────────────────────┐
│                      MODELS                          │
└─────────────────────────────────────────────────────┘

Company (Empresa)
├── name, nit, etc.
└── Relacionado con Headquarters

Headquarters (Sede) 
├── FK: Company  ✅
├── name, address, etc.
└── Relacionado con SoporteDocumental

ServicioSede (Servicio)
├── FK: DatosPrestador  ✅
├── nombre_servicio, modalidad, complejidad
└── ❌ NO tiene FK a Headquarters

SoporteDocumental
├── FK: prestador (DatosPrestador)
├── FK: empresa (Company)       [null=True]
├── FK: sede (Headquarters)     [null=True]
├── FK: servicio (ServicioSede) [null=True]
└── nivel: EMPRESA | SEDE | SERVICIO
```

---

## ✅ ANÁLISIS POR NIVEL

### 1️⃣ NIVEL EMPRESA
**Usuario selecciona:** Solo empresa  
**Modelo permite:** ✅ SÍ
```
SoporteDocumental.nivel = 'EMPRESA'
SoporteDocumental.empresa = Company(1)  ✅
SoporteDocumental.sede = null
SoporteDocumental.servicio = null
```
**Estado:** ✅ FUNCIONA PERFECTO

---

### 2️⃣ NIVEL SEDE  
**Flujo esperado:** Empresa → Sede  
**Modelo permite:** ✅ SÍ
```
SoporteDocumental.nivel = 'SEDE'
SoporteDocumental.empresa = Company(1)
SoporteDocumental.sede = Headquarters(5)  ✅ (FK a Company)
SoporteDocumental.servicio = null
```

**Relación validada:**
```python
Headquarters.company_id == SoporteDocumental.empresa_id
# ✅ Se puede validar que la sede pertenece a la empresa
```

**Estado:** ✅ FUNCIONA

---

### 3️⃣ NIVEL SERVICIO  
**Flujo esperado:** Empresa → Sede → Servicio  
**Modelo ACTUAL permite:** ❌ PARCIALMENTE (PROBLEMA)

```
SoporteDocumental.nivel = 'SERVICIO'
SoporteDocumental.empresa = Company(1)
SoporteDocumental.sede = Headquarters(5)
SoporteDocumental.servicio = ServicioSede(12)  
    ↓
    ❌ PROBLEMA: ServicioSede NO tiene FK a Headquarters
    ¿Cómo sé que ServicioSede(12) pertenece a Headquarters(5)?
```

**El problema real:**
```python
# ServicioSede estructura actual
class ServicioSede(models.Model):
    prestador = ForeignKey('DatosPrestador', ...)  # ✅ Tiene esto
    nombre_servicio = CharField(...)
    # ❌ FALTA: sede = ForeignKey('Headquarters', ...)
    
# Resultado:
# - Sé que el servicio pertenece al prestador
# - PERO NO sé a qué sede física pertenece
# - Imposible validar: "¿Este servicio pertenece a esta sede?"
```

**Estado:** ❌ INCOMPLETO (Ver solución abajo)

---

## 🚨 PROBLEMA IDENTIFICADO

### El Cuello de Botella

```
FLUJO ESPERADO:
┌──────────────┐
│   EMPRESA    │  ← Usuario selecciona Company(1)
│   Clinica X  │
└──────┬───────┘
       │ FK en Headquarters
       ↓
┌──────────────┐
│     SEDE     │  ← Usuario selecciona Headquarters(5)
│  Sede Cali   │
└──────┬───────┘
       │ FK en ServicioSede (❌ NO EXISTE)
       ↓
┌──────────────┐
│  SERVICIO    │  ← Usuario selecciona ServicioSede(12)
│  Obstetricia │
└──────────────┘

PROBLEMA:
ServicioSede.sede_id  ❌ FALTA este campo
```

### Validación que FALTA

```python
# PARA NIVEL EMPRESA - Works ✅
if nivel == 'EMPRESA':
    # Solo valida que empresa existe
    assert SoporteDocumental.empresa_id

# PARA NIVEL SEDE - Works ✅
if nivel == 'SEDE':
    # Valida que sede pertenece a empresa
    sede = Headquarters.objects.get(id=soporte.sede_id)
    assert sede.company_id == soporte.empresa_id

# PARA NIVEL SERVICIO - FAILS ❌
if nivel == 'SERVICIO':
    # Intenta validar pero NO PUEDE
    servicio = ServicioSede.objects.get(id=soporte.servicio_id)
    # ❌ servicio.sede_id NO EXISTE
    # assert servicio.sede_id == soporte.sede_id ???
```

---

## 🛠️ SOLUCIÓN RECOMENDADA

### CAMBIO NECESARIO: Agregar FK a Headquarters en ServicioSede

**Archivo:** `habilitacion/models/servicioSede.py`

```python
class ServicioSede(models.Model):
    # CAMPOS EXISTENTES
    prestador = ForeignKey('DatosPrestador', ...)
    codigo_servicio = CharField(...)
    nombre_servicio = CharField(...)
    
    # ✅ NUEVO CAMPO REQUERIDO
    sede = models.ForeignKey(
        'companies.Headquarters',
        on_delete=models.CASCADE,
        related_name='servicios_sede',
        null=False,  # Requerido
        blank=False,
        help_text='Sede física donde se presta este servicio'
    )
    
    class Meta:
        # Actualizar unique_together para incluir sede
        unique_together = ('prestador', 'codigo_servicio', 'sede')
```

### ¿POR QUÉ es necesario este cambio?

1. **Validación Cascada:** Un servicio DEBE estar en una sede específica
2. **Integridad de Datos:** Imposible que un servicio "flote" sin sede
3. **Queries Eficientes:** `Headquarters.servicios_sede.all()` 
4. **Lógica de Negocio:** Un mismo servicio podría ofrecerse en múltiples sedes

### Ejemplo después del cambio:

```python
class ServicioSede(models.Model):
    prestador = FK(DatosPrestador)   # Prestador "Clínica X"
    sede = FK(Headquarters)          # ✅ NUEVA: Sede "Cali"
    nombre_servicio = "Obstetricia"
    
    # Antes: ❌ "No sé en qué sede está este servicio"
    # Ahora: ✅ "Este servicio está en sede_id=5"
```

---

## 📋 IMPACTO DE LA SOLUCIÓN

### ✅ Ventajas

| Aspecto | Resultado |
|---------|-----------|
| **Flujo Cascada** | ✅ Funciona perfecto |
| **Validación** | ✅ Puede validar sede del servicio |
| **Queries** | ✅ `Headquarters.servicios_sede.all()` |
| **Integridad**: | ✅ Datos consistentes |
| **Lógica Negocio** | ✅ Un servicio = Una sede |

### ⚠️ Cambios Necesarios

| Componente | Cambio |
|-----------|--------|
| **models.py** | ✅ Agregar FK sede |
| **migrations** | ✅ Nueva migración |
| **serializers** | ⚠️ Actualizar si es necesario |
| **admin** | ⚠️ Actualizar formulario |
| **views** | ⚠️ Posibles ajustes de queries |
| **tests** | ⚠️ Actualizar datos de prueba |
| **Datos existentes** | ⚠️ Data migration para poblar sede |

---

## 🎯 RESPUESTA DIRECTA A TU PREGUNTA

### ¿Los modelos ACTUALES permiten este flujo?

```
❌ NIVEL EMPRESA      → ✅ Sí, perfectamente
❌ NIVEL SEDE         → ✅ Sí, perfectamente  
❌ NIVEL SERVICIO     → ❌ NO, tiene limitación crítica
```

### ¿Qué ajustes se deben realizar?

**OBLIGATORIO (Para que funcione el flujo completo):**
1. ✅ Agregar `sede = ForeignKey(Headquarters, ...)` en `ServicioSede`
2. ✅ Crear migración para base de datos
3. ✅ Data migration para poblar sede en servicios existentes
4. ✅ Actualizar `unique_together` en ServicioSede

**RECOMENDADO (Para completar la funcionalidad):**
5. ⚠️ Agregar método helper en Headquarters: `get_servicios_por_sede()`
6. ⚠️ Agregar validación en SoporteDocumental para confirmar relación
7. ⚠️ Crear viewset para listar servicios por sede

---

## 🔄 FLUJO CASCADA CORRECTO (DESPUÉS DEL CAMBIO)

```
PASO 1: Usuario carga documento nivel SERVICIO
        ↓
PASO 2: Frontend solicita: GET /api/empresas/
        Backend retorna: [Company(1), Company(2), ...]
        Usuario selecciona: Company(1) ✅
        ↓
PASO 3: Frontend solicita: GET /api/sedes/?empresa=1
        Backend retorna: [Headquarters(5), Headquarters(6), ...]
        Usuario selecciona: Headquarters(5) ✅
        ↓
PASO 4: Frontend solicita: GET /api/servicios/?sede=5  ← ✅ NUEVA QUERY
        Backend retorna: [ServicioSede(12), ServicioSede(13), ...]
        Usuario selecciona: ServicioSede(12) ✅
        ↓
PASO 5: Backend valida:
        - servicio.sede_id == 5  ✅ Está en la sede
        - servicio.prestador.empresa_id == 1  ✅ Empresa correcta
        ↓
PASO 6: Sistema acepta SoporteDocumental ✅
```

---

## 📝 IMPLEMENTACIÓN RECOMENDADA

### Orden de implementación:

1. **Modelos** - Agregar FK
2. **Migraciones** - Auto + Data migration
3. **Serializers** - Incluir sede en respuesta
4. **ViewSets** - Agregar /servicios/?sede= endpoint
5. **Frontend** - Actualizar lógica cascada
6. **Testing** - Validar flujo completo

---

**Conclusión:** Los modelos CASI funcionan, pero falta link Headquarters ↔ ServicioSede. Es un cambio pequeño pero **CRÍTICO** para que la cascada funcione.

¿Deseas que proceda con la implementación de este cambio?
