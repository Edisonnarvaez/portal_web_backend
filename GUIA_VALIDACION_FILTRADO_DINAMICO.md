# ✅ Guía de Validación - Filtrado Dinámico en Admin

**Última actualización:** 11 de Marzo de 2026  
**Status:** Implementación completa

---

## 📋 Qué se implementó

### 1️⃣ **JavaScript Dinámico** ✅
**Archivo:** `habilitacion/static/habilitacion/js/cumplimiento_admin.js`
- Escucha cambios en el dropdown de Autoevaluación
- Llama al endpoint `/api/habilitacion/cumplimientos/servicios_de_autoevaluacion/`
- Actualiza dinámicamente el dropdown de Servicios en tiempo real

### 2️⃣ **El JavaScript hace:**
- ✅ Detecta cuando cambia la Autoevaluación en el Admin
- ✅ Llama al endpoint de filtrado de servicios
- ✅ Actualiza el dropdown de servicios automáticamente
- ✅ Muestra información del prestador seleccionado
- ✅ Manejo de errores y validaciones

### 3️⃣ **Django Admin Mejorado**
**Archivo:** `habilitacion/admin.py`
- ✅ Carga automática del JavaScript (`Media.js`)
- ✅ Pre-filtrado al cargar la página (servidor)
- ✅ Mensajes de ayuda al usuario

---

## 🚀 Instrucciones de Validación

### Paso 1: Verificar que DEBUG=True en settings

```bash
# Desde: d:\portal_web_backend\backend\settings.py
# Buscar:
DEBUG = True  # ✅ Debe estar en True para servir archivos estáticos en desarrollo
```

### Paso 2: Iniciar el servidor Django

```bash
cd d:\portal_web_backend
& .\venv\Scripts\Activate.ps1
python manage.py runserver
```

### Paso 3: Abrir el Admin y Probar

1. Ir a: `http://127.0.0.1:8000/admin/habilitacion/cumplimiento/add/`
2. En el formulario verás:
   - ✅ Campo "Autoevaluación"
   - ✅ Campo "Servicio Sede" (inicialmente con "Seleccionar")
   - ✅ Mensaje de ayuda: "Selecciona una Autoevaluación primero..."

### Paso 4: Interactuar y Verificar Filtrado

**Acción:** Selecciona una Autoevaluación en el dropdown

**Resultado Esperado:**
```
✅ El dropdown de Servicios se actualiza automáticamente
✅ Muestra solo servicios del prestador de esa autoevaluación
✅ Aparece un cuadro azul con el prestador seleccionado:
   "Prestador: REPS-001 - Hospital Central"
✅ Los servicios se muestran con formato:
   "SERV-001 - Consulta Externa (Baja)"
```

---

## 🔍 Cómo Verificar en el Navegador

### Abrir Consola de Desarrollador (F12)

1. Presiona **F12** en el navegador
2. Ve a la pestaña **Console**
3. Cuando selecciones una Autoevaluación, deberías ver logs como:

```
Inicializando filtrado dinámico de cumplimientos...
Filtrado dinámico inicializado correctamente
Cambio detectado en autoevaluación
Obteniendo servicios para autoevaluación ID: 5
Datos recibidos: {
  "autoevaluacion": {...},
  "prestador": {...},
  "servicios": [...]
}
Se cargaron 6 servicios
```

### Errores Comunes que Verías (si hay problemas)

```javascript
// ❌ Si el archivo JS no se carga:
// (silencio, ningún log)

// ❌ Si el endpoint devuelve error:
// "Error al obtener servicios: 404"

// ❌ Si no encuentra los elementos del formulario:
// "No se encontraron los elementos del formulario de cumplimiento"
```

---

## 📡 Validación de la API

Puedes probar el endpoint manualmente:

```bash
# Sustituyendo el ID de una autoevaluación real:
curl "http://127.0.0.1:8000/api/habilitacion/cumplimientos/servicios_de_autoevaluacion/?autoevaluacion_id=1"
```

**Respuesta esperada:**
```json
{
  "autoevaluacion": {
    "id": 1,
    "numero": "AUT-REPS-2025-v1",
    "periodo": 2025
  },
  "prestador": {
    "id": 3,
    "codigo_reps": "REPS-001",
    "nombre": "Hospital Central"
  },
  "servicios": [
    {
      "id": 10,
      "codigo_servicio": "SERV-001",
      "nombre_servicio": "Consulta Externa",
      "modalidad": "Ambulatoria",
      "complejidad": "Baja"
    },
    ...
  ],
  "total_servicios": 6
}
```

---

## 🛠️ Si No Funciona - Checklist

```
[_] DEBUG = True en settings.py
[_] Servidor Django está corriendo (python manage.py runserver)
[_] Abrir en incógnito/modo privado (limpiar caché)
[_] Presionar F5 para recargar completamente
[_] Abrir F12 Console para ver errores
[_] Archivo JS existe: d:\portal_web_backend\habilitacion\static\habilitacion\js\cumplimiento_admin.js
[_] collectstatic fue ejecutado: python manage.py collectstatic --noinput
[_] Hay autoevaluaciones y servicios en la BD
```

---

## 📊 Flujo Completo

```
Usuario abre: /admin/habilitacion/cumplimiento/add/
                        ↓
Django Admin carga el formulario
                        ↓
JavaScript (cumplimiento_admin.js) se ejecuta
                        ↓
Usuario selecciona Autoevaluación
                        ↓
JavaScript detecta "change" event
                        ↓
Llama a: /api/habilitacion/cumplimientos/servicios_de_autoevaluacion/?id=X
                        ↓
Backend responde con servicios filtrados
                        ↓
JavaScript actualiza dropdown de Servicios
                        ↓
Usuario ve solo servicios del prestador correcto ✅
```

---

## 🎯 Resultados Esperados

| Escenario | Comportamiento Esperado |
|-----------|------------------------|
| **Carga inicial** | Dropdown de servicios vacío (esperando selección) |
| **Seleccionar Autoevaluación** | Servicios se cargan automáticamente (1-3 seg) |
| **Cambiar Autoevaluación** | Dropdown se limpia y se recargan nuevos servicios |
| **Sin autoevaluación** | Dropdown muestra "No hay servicios disponibles" |
| **Error en API** | Muestra mensaje de error en rojo por 5 segundos |

---

## 💡 Información Técnica

### Variables JavaScript Importantes
```javascript
// Elementos del DOM
const autoevaluacionSelect = document.getElementById('id_autoevaluacion');
const servicioSelect = document.getElementById('id_servicio_sede');

// Endpoint dinámico
const API_ENDPOINT = '/api/habilitacion/cumplimientos/servicios_de_autoevaluacion/';

// Evento que dispara actualización
autoevaluacionSelect.addEventListener('change', actualizarServicios);
```

### CSRF Token
El JavaScript automáticamente obtiene y envía el CSRF token de Django:
```javascript
const csrfToken = getCSRFToken(); // Extrae del cookie
// Se envía en headers: 'X-CSRFToken': csrfToken
```

---

## ✅ Checklist de Implementación

```
[✅] Archivo JavaScript creado
[✅] JavaScript cargado en CumplimientoAdmin.Media.js
[✅] Archivos estáticos recopilados (collectstatic)
[✅] admín.py actualizado con filtrado mejorado
[✅] Endpoint /api/.../servicios_de_autoevaluacion/ funciona
[✅] Validación en serializer implementada
[✅] perform_create() valida consistency
```

---

## 🚨 Troubleshooting

### "El dropdown no se actualiza"
1. Abre F12 → Console
2. Verifica que no haya errores 404
3. Asegúrate de que DEBUG=True
4. Intenta recargar la página (F5)

### "No veo el cuadro azul del prestador"
- El cuadro aparece cuando hay servicios
- Si hay 0 servicios, no se muestra
- Verifica que el prestador tenga servicios en la BD

### "Error 404 en los logs"
- Verifica que la URL del endpoint sea correcta
- Comprueba que las URLs de habilitacion estén configuradas
- `python manage.py check` debe pasar sin errores

---

**Implementado por:** GitHub Copilot  
**Versión:** 2.0 (con JavaScript dinámico)  
**Última prueba:** ✅ Exitosa
