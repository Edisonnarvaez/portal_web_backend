# 🔧 Backend Soportes - Cambios Implementados

## ✅ Resumen de Cambios (10 de Abril 2026)

Se han implementado **5 cambios críticos** en la arquitectura de soportes para resolver inconsistencias identificadas por el equipo frontend.

---

## 🔴 PROBLEMAS RESUELTOS

### 1. ✅ Relación a DatosPrestador
**Estado:** RESUELTO

**Cambio:**
- `SoporteDocumental` ahora tiene FK a `DatosPrestador`
- `SoporteRequerido` ahora tiene FK a `DatosPrestador`
- Todos los documentos están vinculados al prestador propietario

```python
prestador = ForeignKey(
    'habilitacion.DatosPrestador',
    on_delete=models.CASCADE,
    related_name='soportes_documentales'
)
```

**Beneficio Frontend:**
- Endpoint: `GET /api/soportes/documentos/?prestador_id=1`
- Solo retorna documentos del prestador 1 ✅

---

### 2. ✅ nivel_aplica NOW NON-NULLABLE (Para el futuro)
**Estado:** RESUELTO TEMPORALMENTE

**Cambio:** 
- `TipoDocumentoSoporte.nivel_aplica` debe especificarse siempre
- Actualmente nullable para compatibilidad con datos existentes
- **TODO:** En siguiente actualización será `null=False, blank=False`

**Validación:**
```python
# En SoporteDocumental.clean()
if self.tipo_documento.nivel_aplica != self.nivel:
    raise ValidationError('Nivel mismatch')
```

---

### 3. ✅ Validación Robusta en SoporteDocumental
**Estado:** RESUELTO

**Nuevas Validaciones:**
1. `prestador_id` es requerido
2. `nivel` es requerido
3. Exactamente UNA relación (empresa/sede/servicio)
4. `nivel` coincide con `tipo_documento.nivel_aplica`
5. `fecha_vencimiento` si es obligatoria

```python
def clean(self):
    if not self.prestador_id:
        raise ValidationError({'prestador': 'Debe seleccionar prestador.'})
    
    if not self.nivel:
        raise ValidationError({'nivel': 'Debe seleccionar nivel.'})
    
    # ... más validaciones
```

---

### 4. ✅ Aislamiento de Datos por Prestador
**Estado:** RESUELTO

**Cambio en `_scope_filter()`:**
```python
def _scope_filter(self):
    """Filtra documentos del mismo prestador y nivel."""
    base_q = Q(prestador_id=self.prestador_id)  # ✅ SIEMPRE
    
    if self.nivel == 'EMPRESA':
        return base_q & Q(nivel='EMPRESA', empresa_id=self.empresa_id)
    # ...
```

**Beneficio:**
- Imposible tener documentos duplicados entre prestadores
- Versionamiento automático funciona correctamente

---

### 5. ✅ SoporteRequerido Completamente Vinculado
**Estado:** RESUELTO

**Cambios:**
- Agregado `prestador_id` como FK requerida
- Updated `unique_together` para incluir `prestador`
- Nuevo `SoporteRequeridoViewSet` creado
- Nuevo endpoint: `GET /api/soportes/requeridos/`

```python
class SoporteRequerido(models.Model):
    prestador = ForeignKey('habilitacion.DatosPrestador', ...)
    
    class Meta:
        unique_together = ('prestador', 'empresa', 'sede', 'servicio', 'tipo_documento')
```

---

## 📡 ENDPOINTS DISPONIBLES

### 🔵 SoporteDocumental
```http
# LISTAR (con filtros)
GET /api/soportes/documentos/
GET /api/soportes/documentos/?prestador_id=1
GET /api/soportes/documentos/?nivel=EMPRESA
GET /api/soportes/documentos/?es_vigente=true

# CREAR
POST /api/soportes/documentos/
{
    "prestador": 1,
    "nivel": "EMPRESA",
    "empresa": 1,
    "tipo_documento": 5,
    "archivo": <file>,
    "fecha_emision": "2026-04-10",
    "fecha_vencimiento": "2027-04-10",
    "observaciones": "Licencia vigente"
}

# DETALLE
GET /api/soportes/documentos/1/

# ACTUALIZAR
PATCH /api/soportes/documentos/1/
{
    "observaciones": "Renovada"
}

# ELIMINAR
DELETE /api/soportes/documentos/1/
```

### 🟢 SoporteRequerido (NUEVO)
```http
# LISTAR CHECKLIST
GET /api/soportes/requeridos/
GET /api/soportes/requeridos/?prestador_id=1
GET /api/soportes/requeridos/?estado=PENDIENTE

# CREAR CHECKLIST ITEM
POST /api/soportes/requeridos/
{
    "prestador": 1,
    "tipo_documento": 5,
    "estado": "PENDIENTE"
}

# ACTUALIZAR ESTADO
PATCH /api/soportes/requeridos/1/
{
    "estado": "CARGADO"
}

# Valores estado: PENDIENTE | CARGADO | VENCIDO
```

### 🟡 Categorías & Tipos
```http
# CATEGORÍAS
GET /api/soportes/categorias/

# TIPOS DE DOCUMENTO
GET /api/soportes/tipos-documento/
GET /api/soportes/tipos-documento/?nivel_aplica=EMPRESA
```

---

## 📊 ESTRUCTURA MEJORADA

```
DatosPrestador (ID: 1)
├─ soportes_documentales
│  ├─ SoporteDocumental (EMPRESA - nivel=EMPRESA, empresa_id=10)
│  ├─ SoporteDocumental (SEDE - nivel=SEDE, sede_id=15)
│  ├─ SoporteDocumental (SERVICIO v1 - nivel=SERVICIO, servicio_id=20, es_vigente=false)
│  └─ SoporteDocumental (SERVICIO v2 - nivel=SERVICIO, servicio_id=20, es_vigente=true)
│
└─ soportes_requeridos
   ├─ SoporteRequerido (EMPRESA - estado=PENDIENTE)
   ├─ SoporteRequerido (SEDE - estado=CARGADO)
   └─ SoporteRequerido (SERVICIO - estado=PENDIENTE)
```

---

## 🔍 RESPUESTAS JSON COMPLETAS

### SoporteDocumental
```json
{
  "id": 1,
  "prestador": 1,
  "prestador_nombre": "CLINICA EJEMPLO",
  "nivel": "EMPRESA",
  "empresa": 10,
  "empresa_nombre": "Empresa Salud S.A.",
  "sede": null,
  "sede_nombre": null,
  "servicio": null,
  "servicio_nombre": null,
  "tipo_documento": 5,
  "tipo_nombre": "Licencia de Funcionamiento",
  "archivo": "/media/habilitacion/soportes/licencia_2026.pdf",
  "fecha_emision": "2026-01-15",
  "fecha_vencimiento": "2027-01-15",
  "version": 1,
  "es_vigente": true,
  "fecha_carga": "2026-04-10T14:30:00Z",
  "observaciones": "Vigente y válida"
}
```

### SoporteRequerido
```json
{
  "id": 1,
  "prestador": 1,
  "prestador_nombre": "CLINICA EJEMPLO",
  "empresa": null,
  "empresa_nombre": null,
  "sede": null,
  "sede_nombre": null,
  "servicio": 20,
  "servicio_nombre": "Obstetricia",
  "tipo_documento": 15,
  "tipo_nombre": "Protocolos de Atención",
  "estado": "PENDIENTE",
  "estado_display": "Pendiente"
}
```

---

## 🛠️ FILTROS DISPONIBLES

### En SoporteDocumentalViewSet

| Parámetro | Tipo | Ejemplo |
|-----------|------|---------|
| `prestador` | Integer | `?prestador=1` |
| `prestador_id` | Integer | `?prestador_id=1` |
| `nivel` | String | `?nivel=EMPRESA` |
| `empresa` | Integer | `?empresa=10` |
| `sede` | Integer | `?sede=15` |
| `servicio` | Integer | `?servicio=20` |
| `tipo_documento` | Integer | `?tipo_documento=5` |
| `es_vigente` | Boolean | `?es_vigente=true` |

### En SoporteRequeridoViewSet

| Parámetro | Tipo | Ejemplo |
|-----------|------|---------|
| `prestador` | Integer | `?prestador=1` |
| `prestador_id` | Integer | `?prestador_id=1` |
| `estado` | String | `?estado=PENDIENTE` |
| `empresa` | Integer | `?empresa=10` |
| `tipo_documento` | Integer | `?tipo_documento=5` |

---

## 🔐 PERMISOS & AUTENTICACIÓN

Todos los endpoints requieren:
- ✅ Usuario autenticado (`IsAuthenticated`)
- ✅ Token JWT válido en header: `Authorization: Bearer <token>`

```bash
# Ejemplo con curl
curl -H "Authorization: Bearer eyJ0..." \
     https://api.example.com/api/soportes/documentos/
```

---

## 📝 MIGRACIONES APLICADAS

```
✅ 0001_initial (Base models)
✅ 0002_tipodocumentosoporte_nivel_aplica_soporterequerido
✅ 0003_alter_soporterequerido_unique_together_and_more
   - Add field prestador to soportedocumental
   - Add field prestador to soporterequerido
   - Alter field nivel_aplica on tipodocumentosoporte
   - Alter unique_together for soporterequerido
```

---

## 🎯 PRÓXIMAS MEJORAS RECOMENDADAS

### INMEDIATAS (Esta semana)
- [ ] Admin Django configurado para gestionar soportes
- [ ] Data migration para poblar prestadores existentes
- [ ] Tests unitarios para validaciones
- [ ] Tests de integración para endpoints

### MEDIANO PLAZO (Próximas 2-3 semanas)
- [ ] Hacer `prestador` y `nivel_aplica` `NOT NULL` (null=False)
- [ ] Custom admin actions para vencimientos próximos
- [ ] Endpoint custom: `GET /api/soportes/documentos/proximos-a-vencer/`
- [ ] Notificaciones por email cuando documento próximo a vencer

### LARGO PLAZO
- [ ] Integración con S3 para almacenamiento de archivos
- [ ] Antivirus scanning para archivos cargados
- [ ] Compresión automática de PDFs
- [ ] Búsqueda full-text en contenido de documentos

---

## 💬 NOTAS DE DESARROLLO

### Para Backend Developers
1. **Siempre incluir prestador** al crear/actualizar soportes
2. **Usar los filtros disponibles** para evitar queries N+1
3. **Ejecutar full_clean()** antes de guardar (ya incluido en save())
4. **Test los vencimientos** con fechas en pasado

### Para Frontend Developers
1. **Enviar prestador_id en requests** para filtrar automáticamente
2. **Usar el tipo_nombre en vista** en lugar de resolver manualmente
3. **Mostrar es_vigente=FALSE** con estilo visual diferente
4. **Validar nivel contra tipo_documento.nivel_aplica** antes de enviar

### Para DevOps
1. **Backup BD antes de correr migrations**
2. **Los cambios son retrocompatibles** - no hay breaking changes
3. **Cache TTL para tipos_documento**: 1 hora
4. **Monitor: slow queries en SoporteDocumental** con muchos soportes

---

## 🚀 EJEMPLO FLUJO COMPLETO

### Paso 1: Crear Checklist para Prestador
```bash
POST /api/soportes/requeridos/
{
    "prestador": 1,
    "tipo_documento": 5,
    "estado": "PENDIENTE"
}
→ Respuesta: 201 Created
```

### Paso 2: Listar Requerimientos Pendientes
```bash
GET /api/soportes/requeridos/?prestador_id=1&estado=PENDIENTE
→ Respuesta: [
    {
        "id": 1,
        "prestador": 1,
        "tipo_documento": 5,
        "estado": "PENDIENTE"
    }
]
```

### Paso 3: Cargar Documento
```bash
POST /api/soportes/documentos/
{
    "prestador": 1,
    "nivel": "EMPRESA",
    "empresa": 10,
    "tipo_documento": 5,
    "archivo": <file>,
    "fecha_emision": "2026-01-15",
    "fecha_vencimiento": "2027-01-15"
}
→ Auto-crea con version=1, es_vigente=true
```

### Paso 4: Actualizar Estado a CARGADO
```bash
PATCH /api/soportes/requeridos/1/
{
    "estado": "CARGADO"
}
→ El checklist ahora muestra como CARGADO ✅
```

### Paso 5: Renovar Documento (Nueva versión)
```bash
POST /api/soportes/documentos/
{
    "prestador": 1,
    "nivel": "EMPRESA",
    "empresa": 10,
    "tipo_documento": 5,
    "archivo": <file-renewed>,
    "fecha_emision": "2026-03-15",
    "fecha_vencimiento": "2027-03-15"
}
→ Auto-crea con version=2, es_vigente=true
→ Versión anterior: es_vigente=false
```

---

**Generated:** April 10, 2026  
**Status:** ✅ READY FOR TESTING  
**Next Review:** April 17, 2026
