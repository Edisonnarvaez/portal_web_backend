# 📄 Ajustes Backend – Sistema de Habilitación IPS

## 🎯 Objetivo

Estandarizar la gestión de soportes, documentos y cumplimiento normativo, alineando el sistema con buenas prácticas de arquitectura y requisitos de habilitación.

---

# 🧩 1. Separación de responsabilidades (CRÍTICO)

## 🔹 Mantener modelos separados

* **Documento (processes)**

  * Uso: Manuales, protocolos, guías
  * Enfoque: Sistema de calidad

* **SoporteDocumental (nuevo)**

  * Uso: Evidencia normativa (RETIE, uso de suelo, etc.)
  * Enfoque: Habilitación

✅ NO mezclar estos modelos
✅ NO reutilizar `Documento` para soportes

---

# 🏗️ 2. Refactor de Headquarters

## ❌ ELIMINAR campos FileField

Eliminar todos los campos tipo:

* licencia_construccion
* soporte_concepto_sanitario
* plano_sede
* plano_electrico
* uso_suelos
* certificado_retie
* plano_ruta_evacuación

## ✅ MANTENER solo indicadores (opcional)

```python
concepto_sanitario = models.BooleanField(default=False)
planta_electrica = models.BooleanField(default=False)
reserva_agua_24h = models.BooleanField(default=False)
```

---

# 📎 3. Implementación de SoporteDocumental

## ✅ Modelo final recomendado

```python
class SoporteDocumental(models.Model):

    NIVEL_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('SEDE', 'Sede'),
        ('SERVICIO', 'Servicio'),
    ]

    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES)

    empresa = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    sede = models.ForeignKey(Headquarters, null=True, blank=True, on_delete=models.CASCADE)
    servicio = models.ForeignKey(ServicioSede, null=True, blank=True, on_delete=models.CASCADE)

    tipo_documento = models.ForeignKey(TipoDocumentoSoporte, on_delete=models.PROTECT)
    archivo = models.FileField(upload_to='habilitacion/soportes/')

    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

    version = models.PositiveIntegerField(default=1)
    es_vigente = models.BooleanField(default=True)

    fecha_carga = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
```

---

## 🔒 Validación obligatoria

```python
def clean(self):
    relaciones = [self.empresa, self.sede, self.servicio]
    if sum(1 for r in relaciones if r) != 1:
        raise ValidationError("Debe asociarse a un único nivel: empresa, sede o servicio.")
```

---

# 🔗 4. Integración con Cumplimiento

## ❌ Actual

```python
documentos_evidencia = models.ManyToManyField(Documento)
```

## ✅ Nuevo diseño

```python
documentos = models.ManyToManyField(Documento, blank=True)
soportes = models.ManyToManyField(SoporteDocumental, blank=True)
```

---

# 🧠 5. Ajuste en modelo Criterio

Agregar control de evidencia requerida:

```python
requiere_documento = models.BooleanField(default=False)
requiere_soporte = models.BooleanField(default=False)
```

---

# 🔒 6. Validación en Cumplimiento

```python
def clean(self):
    if self.criterio.requiere_documento and not self.documentos.exists():
        raise ValidationError("Este criterio requiere documentos.")
    
    if self.criterio.requiere_soporte and not self.soportes.exists():
        raise ValidationError("Este criterio requiere soportes.")
```

---

# 🏢 7. Ajuste en DatosPrestador

## ❗ Agregar relación con Company

```python
company = models.ForeignKey(Company, on_delete=models.PROTECT)
```

---

# 🏥 8. Ajuste en ServicioSede

## ✅ Agregar control opcional

```python
requiere_renovacion = models.BooleanField(default=True)
```

---

# 📅 9. Mejora en Autoevaluación

## ✅ Automatizar vencimiento

```python
from datetime import timedelta

def save(self, *args, **kwargs):
    if not self.fecha_vencimiento:
        self.fecha_vencimiento = self.fecha_inicio + timedelta(days=365)
    super().save(*args, **kwargs)
```

---

# 📊 10. Reglas de negocio clave

* Un soporte solo puede pertenecer a:

  * Empresa O
  * Sede O
  * Servicio

* Los soportes deben:

  * Tener vigencia
  * Permitir versionado
  * Mantener histórico

* Un cumplimiento puede tener:

  * Documentos (calidad)
  * Soportes (normativa)

---

# 🚀 11. Resultado esperado

Con estos cambios el sistema tendrá:

✅ Arquitectura limpia
✅ Sin duplicidad de archivos
✅ Soporte de auditoría real
✅ Escalabilidad
✅ Base para producto comercial

---

# 📌 Checklist de implementación

* [ ] Eliminar FileFields de Headquarters
* [ ] Crear modelo SoporteDocumental
* [ ] Agregar validación de nivel
* [ ] Modificar Cumplimiento (documentos + soportes)
* [ ] Ajustar modelo Criterio
* [ ] Agregar relación Company en DatosPrestador
* [ ] Implementar vencimiento automático en Autoevaluación

---

# 🧠 Nota final

Este diseño separa correctamente:

* Gestión documental (calidad)
* Evidencia normativa (habilitación)

y los integra únicamente en el proceso de evaluación, que es donde realmente deben converger.

---

