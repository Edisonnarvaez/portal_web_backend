# Script de Datos de Habilitación - Guía Rápida

## 📋 Descripción

El script `create_habilitacion_data.py` crea datos de prueba completos para el módulo de habilitación, incluyendo:

- **Estándares**: 7 estándares de la Resolución 3100/2019
- **Criterios**: 32 criterios de evaluación por estándar
- **Prestadores**: DatosPrestador vinculados a cada Headquarters
- **Servicios**: ServicioSede con diferentes modalidades
- **Autoevaluaciones**: Evaluaciones 2024 (completadas) y 2025 (en curso)
- **Cumplimientos**: Registros de evaluación contra criterios

## 🚀 Cómo Usar

### 1. Opción 1: Ejecutar directamente en Django Shell

```bash
cd D:\portal_web_backend
.\venv\Scripts\python.exe manage.py shell -c "exec(open('create_habilitacion_data.py', encoding='utf-8').read())"
```

### 2. Opción 2: Ejecutar como script de management (Recomendado)

Crear `D:\portal_web_backend\habilitacion\management\commands\populate_habilitacion.py`:

```bash
cd D:\portal_web_backend
.\venv\Scripts\python.exe manage.py populate_habilitacion
```

## 📊 Datos Generados

### Estándares Creados
| Código | Nombre | Descripción |
|--------|--------|-------------|
| TH | Talento Humano | Disponibilidad de personal competente y capacitado |
| INF | Infraestructura Física | Infraestructura segura y adecuada |
| DOT | Dotación, Medicamentos e Insumos | Equipos, medicamentos e insumos necesarios |
| PO | Procesos Organizacionales | Procesos documentados e implementados |
| RS | Relacionamiento y Sostenibilidad | Relaciones efectivas y sostenibilidad |
| GI | Garantía de Calidad e Información | Sistemas de garantía de calidad |
| SA | Seguridad del Paciente y Ambiente | Seguridad del paciente y ambiente |

### Criterios por Estándar

**Talento Humano (TH):**
- TH-1.1: Disponibilidad de Médicos Especialistas
- TH-1.2: Perfiles y Competencias del Personal
- TH-1.3: Programa de Educación Continua

**Infraestructura (INF):**
- INF-2.1: Condiciones de Infraestructura
- INF-2.2: Mantenimiento Preventivo

**Dotación (DOT):**
- DOT-3.1: Disponibilidad de Equipos Básicos
- DOT-3.2: Control de Medicamentos e Insumos

**Procesos Organizacionales (PO):**
- PO-4.1: Documentación de Procesos
- PO-4.2: Protocolos Clínicos

**Seguridad del Paciente (SA):**
- SA-7.1: Programa de Seguridad del Paciente
- SA-7.2: Reporte de Eventos Adversos

### Servicios de Modalidad
```
- URG-001: Urgencias - Nivel I
- CNS-001: Consulta Externa - Medicina General
- INT-001: Hospitalización - Medicina Interna
- TEL-001: Telemedicina - Teleconsulta
- AMB-001: Servicio de Ambulancia
```

Se crean para cada prestador (4 sedes = 20 servicios totales)

### Autoevaluaciones

Para cada prestador se crean 2 autoevaluaciones:

| Período | Estado | Descripción |
|---------|--------|------------|
| 2024 | VALIDADA | Completada y auditada |
| 2025 | EN_CURSO | En proceso actual |

### Cumplimientos

Se generan 440 registros de cumplimiento con distribución:
- **63.6%** CUMPLE (280)
- **18.2%** PARCIALMENTE (80)
- **18.2%** NO_CUMPLE (80)

**Nota**: Los planes de mejora se asignan solo a criterios NO_CUMPLE y PARCIALMENTE

## 🔄 Idempotencia

El script es **completamente idempotente**:
- Si los datos ya existen, se reutilizan
- Si no existen, se crean automáticamente
- Puedes ejecutarlo múltiples veces sin duplicados
- Los indicadores de estado muestran `✅` para nuevos y `⏭️ ` para existentes

## 📁 Dependencias

El script requiere que primero ejecutes:
```bash
python manage.py shell < create_sample_data.py
```

Esto crea:
- Company: Red Medicron IPS S.A.S.
- Headquarters (Sedes): 4 sedes de la empresa
- Usuarios Admin
- Procesos y Departamentos

## 🗄️ Modelos Afectados

```python
habilitacion/
├── DatosPrestador (OneToOne con Headquarters)
├── ServicioSede (ForeignKey a DatosPrestador)
├── Autoevaluacion (ForeignKey a DatosPrestador)
└── Cumplimiento (ForeignKey a Autoevaluacion + ServicioSede + Criterio)

normativity/
├── Estandar
└── Criterio (ForeignKey a Estandar)
```

## 📈 Estadísticas Post-Ejecución

```
Estándares:                7
Criterios:                 32
Datos de Prestador:        4
Servicios de Sede:         20
Autoevaluaciones:          8 (4 por cada año: 2024 y 2025)
Cumplimientos:             440 (11 criterios × 4 prestadores × 2 años × 5 servicios)
```

## ✅ Validación de Integridad

El script valida:
- ✅ Company existente
- ✅ Sedes (Headquarters) existentes
- ✅ Usuario admin disponible
- ✅ Relaciones OneToOne respetadas
- ✅ Restricciones UNIQUE respetadas
- ✅ ForeignKey integridad

## 🎯 Próximas Mejoras

Para ampliar los datos de prueba, puedes:

1. **Agregar más criterios** por estándar
2. **Crear más servicios** de modalidad
3. **Agregar evidencia documental** link a `processes.Documento`
4. **Generar planes de mejora detallados**
5. **Crear auditorías internas** (auditoría app)

## ⚠️ Notas Importantes

- **OneToOne Relationship**: Cada `Headquarters` puede tener un único `DatosPrestador`
- **Fecha de Vencimiento**: Las autoevaluaciones 2024 están vencidas, 2025 vigentes
- **Planes de Mejora**: Se generan solo para evaluaciones NO_CUMPLE/PARCIALMENTE
- **Usuario Responsable**: Se asigna el admin para pruebas; cambiar en producción

---

*Documento actualizado: 2025-03-10*
*Script: create_habilitacion_data.py*
