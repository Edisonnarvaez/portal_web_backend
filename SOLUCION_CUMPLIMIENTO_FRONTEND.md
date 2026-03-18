# Solución: Cumplimiento sin Servicios Disponibles

## 🎯 Problema
El modal muestra: **"No hay servicios disponibles para esta autoevaluación"**

## 🔍 Causa Raíz
1. El prestador de la autoevaluación **NO tiene servicios registrados**
2. El frontend no está validando esto antes de abrir el modal
3. El backend validaba pero sin mensajes claros

## ✅ Solución Implementada

### Backend (Cambios Realizados)

#### 1. Serializer mejorado (`serializers.py`)
- ✅ `get_servicios_disponibles()` - Ahora soporta contexto durante POST
- ✅ `validate_servicio_sede_id()` - Mensajes de error descriptivos con sugerencias

**Beneficio**: El backend retorna errores claros indicando:
- Cuáles servicios están disponibles
- O que NO hay servicios y dónde registrarlos

#### 2. Endpoint existente (ya funcional)
```
GET /api/habilitacion/cumplimientos/servicios_de_autoevaluacion/?autoevaluacion_id=5
```

**Retorna**:
```json
{
  "autoevaluacion": { "id": 5, "numero": "AE-2026-01", "periodo": "2026" },
  "prestador": { "id": 1, "codigo_reps": "1234567890", "nombre": "Clínica XYZ" },
  "servicios": [
    {
      "id": 1,
      "codigo": "SRV-001",
      "nombre": "Cirugía General",
      "modalidad": "Intramural",
      "complejidad": "Alta",
      "estado": "Habilitado"
    }
  ],
  "total_servicios": 1
}
```

### Frontend (Recomendación)

#### Flujo Recomendado

**OPCIÓN A: Carga Dinámica (Recomendado)**
```
1. Usuario abre modal "Nuevo Cumplimiento"
2. Usuario selecciona AUTOEVALUACIÓN
3. Frontend → GET /api/habilitacion/cumplimientos/servicios_de_autoevaluacion/?autoevaluacion_id=X
4. Si total_servicios = 0 → Mostrar ALERTA y deshabilitar botón guardar
5. Si total_servicios > 0 → Llenar select con opciones
6. Usuario selecciona servicio y completa form
7. POST /api/habilitacion/cumplimientos/
```

**OPCIÓN B: Validación en Backend (Actual)**
```
1. Usuario intenta crear cumplimiento
2. Si el servicio no es del prestador correcto
3. Backend retorna error descriptivo
4. Frontend muestra el error al usuario
```

---

## 🔧 Implementación Frontend

### Paso 1: Crear Servicio para obtener Servicios
```typescript
// servicioService.ts
export const obtenerServiciosDeAutoevaluacion = async (autoevaluacionId: number) => {
  const response = await api.get(
    `/api/habilitacion/cumplimientos/servicios_de_autoevaluacion/`,
    { params: { autoevaluacion_id: autoevaluacionId } }
  );
  return response.data;
};
```

### Paso 2: Usar en el Hook / Componente
```typescript
const [servicios, setServicios] = useState<ServicioSede[]>([]);
const [cargandoServicios, setCargandoServicios] = useState(false);

const handleAutoevaluacionChange = async (autoevaluacionId: number) => {
  setCargandoServicios(true);
  try {
    const data = await obtenerServiciosDeAutoevaluacion(autoevaluacionId);
    setServicios(data.servicios);
    
    // Validación
    if (data.servicios.length === 0) {
      toast.warning(
        `No hay servicios para ${data.prestador.nombre}. ` +
        `Debe crear servicios primero.`
      );
      setServicioDisabled(true);
    } else {
      setServicioDisabled(false);
    }
  } catch (error) {
    toast.error("Error al cargar servicios");
  } finally {
    setCargandoServicios(false);
  }
};
```

### Paso 3: Renderizar con Estados
```tsx
<div className="form-group">
  <label>Servicio del Prestador *</label>
  
  {cargandoServicios && <Spinner />}
  
  {servicios.length === 0 && !cargandoServicios && (
    <Alert type="warning">
      ⚠️ No hay servicios disponibles para esta autoevaluación.
      <Link to="/servicios">Registrar servicios</Link>
    </Alert>
  )}
  
  {servicios.length > 0 && (
    <select
      value={servicioId}
      onChange={(e) => onServicioChange(e.target.value)}
      disabled={servicioDisabled}
    >
      <option value="">-- Seleccione un servicio --</option>
      {servicios.map(s => (
        <option key={s.id} value={s.id}>
          {s.codigo} - {s.nombre} ({s.complejidad})
        </option>
      ))}
    </select>
  )}
  
  {errors.servicio_sede && (
    <ErrorMessage>{errors.servicio_sede}</ErrorMessage>
  )}
</div>
```

---

## 📊 Comparativa de Implementaciones

| Aspecto | Validación Backend | Carga Dinámica Frontend |
|--------|:------------------:|:---------------------:|
| **UX** | ❌ Error tras clickear | ✅ Alerta inmediata |
| **Performance** | ✅ Sin requests extra | ❌ +1 request |
| **Escalabilidad** | ✅ Fácil mantener | ✅ Flexible |
| **Recomendado** | Para cambios rápidos | Para formularios |

---

## 🚀 Checklist de Implementación

- [ ] Backend: Nuevos métodos en serializer ✅ (ya hecho)
- [ ] Frontend: Crear servicio HTTP para `servicios_de_autoevaluacion`
- [ ] Frontend: Implementar lógica `onAutoevaluacionChange`
- [ ] Frontend: Mostrar alerta cuando `total_servicios = 0`
- [ ] Frontend: Deshabilitar botón guardar si no hay servicios
- [ ] QA: Probar flujos:
  - [x] Prestador sin servicios
  - [x] Prestador con 1 servicio
  - [x] Prestador con múltiples servicios
- [ ] QA: Validar mensajes de error desde backend

---

## 🔗 Endpoints Relevantes

```
GET  /api/habilitacion/cumplimientos/servicios_de_autoevaluacion/?autoevaluacion_id={id}
GET  /api/habilitacion/servicios/
POST /api/habilitacion/cumplimientos/
GET  /api/habilitacion/autoevaluaciones/{id}/
```

---

**Fecha**: 12 Mar 2026
**Estado**: Solución Backend Completa ✅
**Próximo Paso**: Implementación Frontend
