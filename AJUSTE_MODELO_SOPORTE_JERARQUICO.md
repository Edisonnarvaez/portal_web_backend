# 🎯 AJUSTE DEL MODELO - Flujo Jerárquico Correcto

**Fecha:** 10 Abril 2026  
**Análisis:** Cómo ajustar SoporteDocumental para la jerarquía correcta

---

## 🏛️ ESTRUCTURA JERÁRQUICA CORRECTA

```
Company (Empresa)
    ↓ FK en Headquarters
Headquarters (Sede Física)
    ↓ FK en DatosPrestador
DatosPrestador (Prestador)
    ↓ FK en ServicioSede
ServicioSede (Servicios)
```

**Validaciones de integridad:**
```python
# Validar que Headquarters pertenece a Company
Headquarters.company_id == soporte.empresa_id  ✅

# Validar que DatosPrestador pertenece a Headquarters
DatosPrestador.headquarters_id == soporte.sede_id  ✅

# Validar que ServicioSede pertenece a DatosPrestador
ServicioSede.prestador_id == soporte.prestador_id  ✅
```

---

## 📊 DISEÑO ACTUAL vs PROPUESTO

### ❌ PROBLEMA ACTUAL

El modelo actual tiene:
```python
class SoporteDocumental(models.Model):
    prestador = FK(DatosPrestador)
    empresa = FK(Company)       # Puede no estar vinculada a ninguna sede
    sede = FK(Headquarters)     # Puede no estar vinculada a empresa
    servicio = FK(ServicioSede) # Puede no estar vinculado a prestador
    
    # Validación débil: "Exactamente UNA relación"
    relaciones = [empresa_id, sede_id, servicio_id]
    # Esto permite: empresa=1, sede=null, PERO ¿y prestador?
```

**Problema:** No valida la **cadena de pertenencia** correcta

---

## ✅ MODELO PROPUESTO

**La estructura debe reflejar la jerarquía:**

```python
class SoporteDocumental(models.Model):
    # NIVEL: Indica hasta qué nivel llega el documento
    NIVEL_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('SEDE', 'Sede'),
        ('PRESTADOR', 'Prestador'),  # ← ¿NUEVO?
        ('SERVICIO', 'Servicio'),
    ]
    
    prestador = FK(DatosPrestador)      # Siempre requerido
    
    # NIVEL 1: EMPRESA
    empresa = FK(Company)               # Requerido para todos
    
    # NIVEL 2: SEDE
    sede = FK(Headquarters)             # null para NIVEL=EMPRESA, requerido para NIVEL >= SEDE
    
    # NIVEL 3: PRESTADOR (¿Nuevo nivel?)
    # Nota: En ServicioSede ya está implícito por prestador_id
    
    # NIVEL 4: SERVICIO
    servicio = FK(ServicioSede)         # null para NIVEL < SERVICIO, requerido para NIVEL=SERVICIO
```

---

## 🤔 PREGUNTA CRÍTICA: ¿Cuántos niveles debería haber?

### OPCIÓN A: 3 Niveles (Actual)
```
NIVEL_CHOICES = [
    ('EMPRESA', 'Empresa'),           # Company
    ('SEDE', 'Sede'),                 # Company + Headquarters
    ('SERVICIO', 'Servicio'),         # Company + Headquarters + ServicioSede
                                      # ¿Pero qué pasa con DatosPrestador?
]
```

**Problema:** Falta un nivel para Prestador

---

### OPCIÓN B: 4 Niveles (Recomendado)
```
NIVEL_CHOICES = [
    ('EMPRESA', 'Empresa'),           # Company
    ('SEDE', 'Sede'),                 # Company + Headquarters
    ('PRESTADOR', 'Prestador'),       # Company + Headquarters + DatosPrestador
    ('SERVICIO', 'Servicio'),         # Company + Headquarters + DatosPrestador + ServicioSede
]
```

**Ventaja:** Refleja la jerarquía real

---

## 📋 VALIDACIONES POR NIVEL (OPCIÓN B - 4 NIVELES)

### NIVEL = 'EMPRESA'
```python
Requerido:
  ✅ prestador_id        (siempre)
  ✅ empresa_id          (obligatorio para este nivel)

Debe ser NULL:
  ✅ sede_id = null
  ✅ servicio_id = null

Validación adicional:
  ✅ prestador.company_id == empresa_id
     (Asegurar que el prestador está en la empresa)
```

**Pero espera...** Si prestador es FK, ¿cómo puede existir un soporte de EMPRESA sin especificar qué prestador?

---

## 🚨 CONFLICTO FUNDAMENTAL

**Problema:** Si `prestador` SIEMPRE es requerido, entonces:
- Todos los documentos están ligados a un prestador
- Un documento de NIVEL EMPRESA también debe especificar un prestador? ❌

**Soluciones posibles:**

### SOLUCIÓN 1: Prestador NO es requerido
```python
prestador = FK(DatosPrestador, null=True, blank=True)  # Opcional

NIVEL = 'EMPRESA':
  ✅ empresa_id (requerido)
  ✅ prestador_id (NULL - es documento para toda la empresa)
  ✅ sede_id (NULL)
  ✅ servicio_id (NULL)

NIVEL = 'SEDE':
  ✅ empresa_id (requerido)
  ✅ sede_id (requerido)
  ✅ prestador_id (NULL - documento para toda la sede)
  ✅ servicio_id (NULL)

NIVEL = 'PRESTADOR':
  ✅ empresa_id (requerido)
  ✅ sede_id (requerido)
  ✅ prestador_id (requerido)
  ✅ servicio_id (NULL)

NIVEL = 'SERVICIO':
  ✅ empresa_id (requerido)
  ✅ sede_id (requerido)
  ✅ prestador_id (requerido)
  ✅ servicio_id (requerido)
```

**Ventaja:** Flujo cascada perfecto  
**Desventaja:** Cambia la lógica actual

---

### SOLUCIÓN 2: Usar DatosPrestador para todos (Mantener prestador siempre)
```python
prestador = FK(DatosPrestador)  # Siempre requerido

# Entonces:
# NIVEL = 'EMPRESA' significa: "Documento del prestador X, pero importante para toda la empresa"
# NIVEL = 'SEDE' significa: "Documento del prestador X, importante para toda su sede"
# NIVEL = 'SERVICIO' significa: "Documento específico del servicio"

# La jerarquía se establece por:
# - Si empresa, sede, servicio son null pero prestador existe
#   → Es documento a nivel de esa empresa/sede del prestador
```

**Ventaja:** Mantiene estructura actual  
**Desventaja:** Poco intuitivo

---

## 🎯 RECOMENDACIÓN FINAL

**OPCIÓN 1 es mejor porque:**

1. ✅ Refleja la lógica real de negocio
2. ✅ Permite documentos a nivel Empresa, Sede, Prestador o Servicio
3. ✅ Cada nivel es independiente y cumple su propósito
4. ✅ Flujo cascada es intuitivo
5. ✅ Validaciones son claras

---

## 🔄 CAMBIOS NECESARIOS (OPCIÓN 1)

### 1. Modelo SoporteDocumental

```python
class SoporteDocumental(models.Model):
    NIVEL_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('SEDE', 'Sede'),
        ('PRESTADOR', 'Prestador'),    # ← NUEVO
        ('SERVICIO', 'Servicio'),
    ]

    prestador = FK(DatosPrestador, null=True, blank=True)  # ← CAMBIAR nullable
    
    nivel = CharField(choices=NIVEL_CHOICES)
    empresa = FK(Company)                      # ← SIEMPRE REQUERIDO
    sede = FK(Headquarters, null=True, blank=True)
    servicio = FK(ServicioSede, null=True, blank=True)
    
    # Validaciones mejoradas
    def clean(self):
        # Caso EMPRESA
        if self.nivel == 'EMPRESA':
            assert self.empresa_id
            assert not self.sede_id
            assert not self.prestador_id
            assert not self.servicio_id
        
        # Caso SEDE
        elif self.nivel == 'SEDE':
            assert self.empresa_id
            assert self.sede_id
            assert not self.prestador_id
            assert not self.servicio_id
            # Validar que sede pertenece a empresa
            assert self.sede.company_id == self.empresa_id
        
        # Caso PRESTADOR
        elif self.nivel == 'PRESTADOR':
            assert self.empresa_id
            assert self.sede_id
            assert self.prestador_id
            assert not self.servicio_id
            # Validar cadena
            assert self.sede.company_id == self.empresa_id
            assert self.prestador.headquarters_id == self.sede_id
        
        # Caso SERVICIO
        elif self.nivel == 'SERVICIO':
            assert self.empresa_id
            assert self.sede_id
            assert self.prestador_id
            assert self.servicio_id
            # Validar cadena completa
            assert self.sede.company_id == self.empresa_id
            assert self.prestador.headquarters_id == self.sede_id
            assert self.servicio.prestador_id == self.prestador_id
```

### 2. Actualizar TipoDocumentoSoporte

```python
class TipoDocumentoSoporte(models.Model):
    NIVEL_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('SEDE', 'Sede'),
        ('PRESTADOR', 'Prestador'),    # ← NUEVO
        ('SERVICIO', 'Servicio'),
    ]
    
    nivel_aplica = CharField(choices=NIVEL_CHOICES)  # ← Especifica a qué nivel aplica
```

### 3. Migración

```
- Alterar prestador: null=True, blank=True
- Hacer empresa NOT NULL
- Agregar nivel PRESTADOR a NIVEL_CHOICES
```

---

## 📱 FLUJO FRONTEND CASCADA (OPCIÓN 1)

```
Usuario selecciona NIVEL: [EMPRESA, SEDE, PRESTADOR, SERVICIO]
│
├─ Si EMPRESA:
│  ├─ GET /api/companies/
│  └─ Usuario selecciona empresa
│
├─ Si SEDE:
│  ├─ GET /api/companies/
│  ├─ Usuario selecciona empresa
│  ├─ GET /api/headquarters/?company_id={empresa}
│  └─ Usuario selecciona sede
│
├─ Si PRESTADOR:
│  ├─ GET /api/companies/
│  ├─ Usuario selecciona empresa
│  ├─ GET /api/headquarters/?company_id={empresa}
│  ├─ Usuario selecciona sede
│  ├─ GET /api/prestadores/?headquarters_id={sede}
│  └─ Usuario selecciona prestador
│
└─ Si SERVICIO:
   ├─ GET /api/companies/
   ├─ Usuario selecciona empresa
   ├─ GET /api/headquarters/?company_id={empresa}
   ├─ Usuario selecciona sede
   ├─ GET /api/prestadores/?headquarters_id={sede}
   ├─ Usuario selecciona prestador
   ├─ GET /api/servicios/?prestador_id={prestador}
   └─ Usuario selecciona servicio
```

---

## 🎯 PREGUNTAS PARA TI

1. **¿Necesitas un nivel PRESTADOR** o solo EMPRESA, SEDE, SERVICIO?
   - Si solo 3 niveles: ¿Cómo documentos de SEDE sin especificar prestador?

2. **¿Prestador SIEMPRE es requerido** o puede ser null?
   - Si es requerido: ¿Qué significa NIVEL=EMPRESA si siempre hay prestador?
   - Si es opcional: Debería ser null=True

3. **¿La estructura de validación que propuse te parece correcta?**

---

**Mi recomendación:** Usa OPCIÓN 1 con 4 niveles y prestador opcional. Así:
- ✅ Flujo cascada perfecto
- ✅ Lógica de negocio clara
- ✅ Validaciones robustas
- ✅ Cada nivel tiene propósito específico

¿Quieres que implementemos esto?
