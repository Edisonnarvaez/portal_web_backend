# Plan de Mejora - Implementación Backend (Django)

**Fecha**: 2026-02-19  
**Objetivo**: Crear el modelo `PlanMejora` y `Hallazgo` como modelos propios dentro de la app `habilitacion` en Django  
**Decisión**: Opción B — Modelos separados dentro de la misma app `habilitacion`

---

## Tabla de Contenidos

1. [Contexto y Justificación](#1-contexto-y-justificación)
2. [Paso 1: Modelo PlanMejora](#2-paso-1-modelo-planmejora)
3. [Paso 2: Modelo Hallazgo](#3-paso-2-modelo-hallazgo)
4. [Paso 3: Actualizar modelo Cumplimiento](#4-paso-3-actualizar-modelo-cumplimiento)
5. [Paso 4: Migraciones](#5-paso-4-migraciones)
6. [Paso 5: Serializers](#6-paso-5-serializers)
7. [Paso 6: ViewSets](#7-paso-6-viewsets)
8. [Paso 7: URLs (Router)](#8-paso-7-urls-router)
9. [Paso 8: Admin](#9-paso-8-admin)
10. [Paso 9: Signals (opcional)](#10-paso-9-signals-opcional)
11. [Paso 10: Tests](#11-paso-10-tests)
12. [Endpoints Resultantes](#12-endpoints-resultantes)
13. [Diagrama Relacional Actualizado](#13-diagrama-relacional-actualizado)
14. [Checklist de Implementación](#14-checklist-de-implementación)

---

## 1. Contexto y Justificación

### Estado actual

En el modelo `Cumplimiento` actual, `plan_mejora` es un **TextField** simple:

```python
class Cumplimiento(models.Model):
    plan_mejora = models.TextField(blank=True)          # Solo texto
    responsable_mejora = models.ForeignKey(User, ...)   # Un solo responsable
    fecha_compromiso = models.DateField(null=True)      # Una sola fecha
```

### Problema

El frontend ya necesita (y tiene construido):
- **Ciclo de vida completo**: PENDIENTE → EN_CURSO → COMPLETADO / VENCIDO
- **Porcentaje de avance** (0-100%)
- **Múltiples fechas**: inicio, vencimiento, implementación
- **Acciones a implementar** como campo separado
- **Evidencia** documental
- **Hallazgos** que referencian `plan_mejora_id` como FK
- **Dashboard con métricas**: planes vencidos, próximos a vencer, resumen estadístico

Un TextField **no puede soportar** ninguno de estos requerimientos.

### Decisión

Crear `PlanMejora` y `Hallazgo` como **modelos independientes** dentro de `habilitacion/models.py`, manteniendo la cohesión del dominio.

---

## 2. Paso 1: Modelo PlanMejora

### Archivo: `habilitacion/models.py`

Agregar después del modelo `Cumplimiento`:

```python
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class PlanMejora(models.Model):
    """
    Plan de mejora asociado a un cumplimiento de criterio en una autoevaluación.
    Permite rastrear acciones correctivas con ciclo de vida completo.
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        VENCIDO = 'VENCIDO', 'Vencido'

    # Identificación
    numero_plan = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador único del plan (ej: PM-2026-001)"
    )
    descripcion = models.TextField(
        help_text="Descripción general del plan de mejora"
    )

    # Relaciones
    cumplimiento = models.ForeignKey(
        'Cumplimiento',
        on_delete=models.CASCADE,
        related_name='planes_mejora',
        null=True,
        blank=True,
        help_text="Cumplimiento asociado que originó este plan"
    )
    criterio = models.ForeignKey(
        'normativity.Criterio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planes_mejora',
        help_text="Criterio normativo relacionado"
    )
    autoevaluacion = models.ForeignKey(
        'Autoevaluacion',
        on_delete=models.CASCADE,
        related_name='planes_mejora',
        help_text="Autoevaluación a la que pertenece este plan"
    )

    # Estado del cumplimiento cuando se creó el plan
    estado_cumplimiento_actual = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Estado del cumplimiento al momento de crear el plan"
    )
    objetivo_mejorado = models.TextField(
        blank=True,
        default='',
        help_text="Meta u objetivo que se quiere alcanzar"
    )

    # Plan de acción
    acciones_implementar = models.TextField(
        help_text="Acciones concretas a implementar para la mejora"
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planes_mejora_asignados',
        help_text="Usuario responsable de ejecutar el plan"
    )

    # Fechas
    fecha_inicio = models.DateField(
        help_text="Fecha de inicio del plan"
    )
    fecha_vencimiento = models.DateField(
        help_text="Fecha límite para completar el plan"
    )
    fecha_implementacion = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en que se completó la implementación"
    )

    # Seguimiento
    porcentaje_avance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de avance (0-100)"
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        help_text="Estado actual del plan"
    )
    evidencia = models.TextField(
        blank=True,
        default='',
        help_text="Descripción de la evidencia o referencia a documentos"
    )
    observaciones = models.TextField(
        blank=True,
        default='',
        help_text="Observaciones adicionales"
    )

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'habilitacion_plan_mejora'
        ordering = ['-fecha_creacion']
        verbose_name = 'Plan de Mejora'
        verbose_name_plural = 'Planes de Mejora'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['autoevaluacion']),
        ]

    def __str__(self):
        return f"{self.numero_plan} - {self.descripcion[:50]}"

    # ─── Métodos calculados ───

    @property
    def esta_vencido(self) -> bool:
        """True si la fecha de vencimiento ya pasó y no está completado."""
        if self.estado == self.Estado.COMPLETADO:
            return False
        return self.fecha_vencimiento < timezone.now().date()

    @property
    def dias_restantes(self) -> int | None:
        """Días restantes para el vencimiento. Negativo si ya venció."""
        if not self.fecha_vencimiento:
            return None
        return (self.fecha_vencimiento - timezone.now().date()).days

    @property
    def proximo_a_vencer(self) -> bool:
        """True si vence en los próximos 30 días."""
        dias = self.dias_restantes
        if dias is None:
            return False
        return 0 < dias <= 30

    def marcar_vencidos(self):
        """Actualiza el estado a VENCIDO si aplica."""
        if self.esta_vencido and self.estado not in [self.Estado.COMPLETADO, self.Estado.VENCIDO]:
            self.estado = self.Estado.VENCIDO
            self.save(update_fields=['estado', 'fecha_actualizacion'])

    # ─── Manager personalizado (opcional) ───

    class PlanMejoraManager(models.Manager):
        def vencidos(self):
            return self.filter(
                fecha_vencimiento__lt=timezone.now().date()
            ).exclude(estado='COMPLETADO')

        def proximos_a_vencer(self, dias=30):
            fecha_limite = timezone.now().date() + timezone.timedelta(days=dias)
            return self.filter(
                fecha_vencimiento__lte=fecha_limite,
                fecha_vencimiento__gte=timezone.now().date()
            ).exclude(estado__in=['COMPLETADO', 'VENCIDO'])

        def por_autoevaluacion(self, autoevaluacion_id):
            return self.filter(autoevaluacion_id=autoevaluacion_id)

    objects = PlanMejoraManager()
```

> **Nota sobre el Manager**: Si prefieres no usar un Manager anidado, puedes definirlo fuera de la clase como `class PlanMejoraManager(models.Manager)` y luego asignarlo con `objects = PlanMejoraManager()`.

---

## 3. Paso 2: Modelo Hallazgo

### Archivo: `habilitacion/models.py`

Agregar después de `PlanMejora`:

```python
class Hallazgo(models.Model):
    """
    Hallazgo identificado durante una autoevaluación de habilitación.
    Puede estar vinculado a un plan de mejora.
    """

    class TipoHallazgo(models.TextChoices):
        FORTALEZA = 'FORTALEZA', 'Fortaleza'
        OPORTUNIDAD_MEJORA = 'OPORTUNIDAD_MEJORA', 'Oportunidad de Mejora'
        NO_CONFORMIDAD = 'NO_CONFORMIDAD', 'No Conformidad'
        HALLAZGO = 'HALLAZGO', 'Hallazgo'

    class Severidad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRÍTICA', 'Crítica'

    class EstadoHallazgo(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        EN_SEGUIMIENTO = 'EN_SEGUIMIENTO', 'En Seguimiento'
        CERRADO = 'CERRADO', 'Cerrado'

    # Identificación
    numero_hallazgo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador único del hallazgo (ej: HAL-2026-001)"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del hallazgo"
    )
    tipo = models.CharField(
        max_length=30,
        choices=TipoHallazgo.choices,
        help_text="Tipo de hallazgo"
    )
    severidad = models.CharField(
        max_length=10,
        choices=Severidad.choices,
        help_text="Nivel de severidad"
    )

    # Relaciones
    autoevaluacion = models.ForeignKey(
        'Autoevaluacion',
        on_delete=models.CASCADE,
        related_name='hallazgos',
        help_text="Autoevaluación donde se identificó"
    )
    datos_prestador = models.ForeignKey(
        'DatosPrestador',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Prestador asociado"
    )
    criterio = models.ForeignKey(
        'normativity.Criterio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Criterio normativo relacionado"
    )
    plan_mejora = models.ForeignKey(
        'PlanMejora',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hallazgos',
        help_text="Plan de mejora asociado para resolver este hallazgo"
    )

    # Datos adicionales
    area_responsable = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Área o departamento responsable"
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoHallazgo.choices,
        default=EstadoHallazgo.ABIERTO,
        help_text="Estado actual del hallazgo"
    )
    fecha_identificacion = models.DateField(
        help_text="Fecha en que se identificó el hallazgo"
    )
    fecha_cierre = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en que se cerró el hallazgo"
    )
    observaciones = models.TextField(
        blank=True,
        default='',
        help_text="Observaciones adicionales"
    )

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'habilitacion_hallazgo'
        ordering = ['-fecha_creacion']
        verbose_name = 'Hallazgo'
        verbose_name_plural = 'Hallazgos'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['tipo']),
            models.Index(fields=['severidad']),
            models.Index(fields=['autoevaluacion']),
        ]

    def __str__(self):
        return f"{self.numero_hallazgo} - {self.get_tipo_display()} ({self.get_severidad_display()})"
```

---

## 4. Paso 3: Actualizar modelo Cumplimiento

Mantener los campos `plan_mejora` (TextField) y `fecha_compromiso` en el modelo `Cumplimiento` original como **resumen rápido** para no romper nada existente. Pero agregar una relación inversa automática gracias al `ForeignKey` de `PlanMejora`:

```python
# El campo plan_mejora (TextField) en Cumplimiento se mantiene tal cual.
# La relación inversa ya existe gracias a:
#   PlanMejora.cumplimiento = ForeignKey('Cumplimiento', related_name='planes_mejora')
#
# Ahora puedes hacer:
#   cumplimiento.planes_mejora.all()  → Todos los planes de mejora de ese cumplimiento
#   cumplimiento.plan_mejora          → El texto resumen (campo original)
```

### (Opcional) Agregar propiedad de conveniencia en Cumplimiento

```python
class Cumplimiento(models.Model):
    # ... campos existentes ...

    @property
    def tiene_planes_activos(self) -> bool:
        """True si hay planes de mejora activos (no completados)."""
        return self.planes_mejora.exclude(estado='COMPLETADO').exists()

    @property
    def planes_mejora_count(self) -> int:
        """Número total de planes de mejora."""
        return self.planes_mejora.count()
```

---

## 5. Paso 4: Migraciones

Ejecutar en orden:

```bash
# 1. Crear la migración automática
python manage.py makemigrations habilitacion

# 2. Verificar la migración generada (revisar antes de aplicar)
python manage.py showmigrations habilitacion

# 3. Aplicar la migración
python manage.py migrate habilitacion

# 4. Verificar que las tablas se crearon
python manage.py dbshell
# Luego en SQL:
# \dt habilitacion_plan_mejora
# \dt habilitacion_hallazgo
```

### Migración esperada

Django debería generar algo como:

```python
# habilitacion/migrations/XXXX_create_planmejora_hallazgo.py

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('habilitacion', 'XXXX_previous_migration'),
        ('normativity', 'XXXX_latest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanMejora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_plan', models.CharField(max_length=50, unique=True)),
                ('descripcion', models.TextField()),
                ('estado_cumplimiento_actual', models.CharField(blank=True, default='', max_length=100)),
                ('objetivo_mejorado', models.TextField(blank=True, default='')),
                ('acciones_implementar', models.TextField()),
                ('fecha_inicio', models.DateField()),
                ('fecha_vencimiento', models.DateField()),
                ('fecha_implementacion', models.DateField(blank=True, null=True)),
                ('porcentaje_avance', models.IntegerField(default=0, validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ])),
                ('estado', models.CharField(choices=[
                    ('PENDIENTE', 'Pendiente'),
                    ('EN_CURSO', 'En Curso'),
                    ('COMPLETADO', 'Completado'),
                    ('VENCIDO', 'Vencido'),
                ], default='PENDIENTE', max_length=20)),
                ('evidencia', models.TextField(blank=True, default='')),
                ('observaciones', models.TextField(blank=True, default='')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                # ForeignKeys se generan automáticamente
            ],
        ),
        migrations.CreateModel(
            name='Hallazgo',
            # ... similar ...
        ),
    ]
```

---

## 6. Paso 5: Serializers

### Archivo: `habilitacion/serializers.py`

Agregar los siguientes serializers:

```python
from rest_framework import serializers
from .models import PlanMejora, Hallazgo


# ─────────────── PLAN MEJORA ───────────────

class PlanMejoraListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados."""
    criterio_codigo = serializers.CharField(source='criterio.codigo', read_only=True, default='')
    criterio_nombre = serializers.CharField(source='criterio.nombre', read_only=True, default='')
    autoevaluacion_numero = serializers.CharField(source='autoevaluacion.numero_autoevaluacion', read_only=True, default='')
    responsable_nombre = serializers.SerializerMethodField()
    esta_vencido = serializers.BooleanField(read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    proximo_a_vencer = serializers.BooleanField(read_only=True)

    class Meta:
        model = PlanMejora
        fields = [
            'id', 'numero_plan', 'descripcion',
            'criterio_id', 'criterio_codigo', 'criterio_nombre',
            'autoevaluacion_id', 'autoevaluacion_numero',
            'estado_cumplimiento_actual', 'objetivo_mejorado',
            'acciones_implementar',
            'responsable', 'responsable_nombre',
            'fecha_inicio', 'fecha_vencimiento', 'fecha_implementacion',
            'porcentaje_avance', 'estado',
            'evidencia', 'observaciones',
            'esta_vencido', 'dias_restantes', 'proximo_a_vencer',
            'fecha_creacion', 'fecha_actualizacion',
        ]

    def get_responsable_nombre(self, obj):
        if obj.responsable:
            return f"{obj.responsable.first_name} {obj.responsable.last_name}".strip() or obj.responsable.username
        return None


class PlanMejoraDetailSerializer(PlanMejoraListSerializer):
    """Serializer completo para detalle, incluye hallazgos asociados."""
    hallazgos = serializers.SerializerMethodField()

    class Meta(PlanMejoraListSerializer.Meta):
        fields = PlanMejoraListSerializer.Meta.fields + ['hallazgos']

    def get_hallazgos(self, obj):
        """Lista resumida de hallazgos asociados al plan."""
        return HallazgoListSerializer(obj.hallazgos.all(), many=True).data


class PlanMejoraCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar planes de mejora."""

    class Meta:
        model = PlanMejora
        fields = [
            'numero_plan', 'descripcion',
            'cumplimiento', 'criterio', 'autoevaluacion',
            'estado_cumplimiento_actual', 'objetivo_mejorado',
            'acciones_implementar', 'responsable',
            'fecha_inicio', 'fecha_vencimiento', 'fecha_implementacion',
            'porcentaje_avance', 'estado',
            'evidencia', 'observaciones',
        ]

    def validate(self, data):
        """Validaciones de negocio."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_vencimiento = data.get('fecha_vencimiento')

        if fecha_inicio and fecha_vencimiento:
            if fecha_vencimiento <= fecha_inicio:
                raise serializers.ValidationError({
                    'fecha_vencimiento': 'La fecha de vencimiento debe ser posterior a la fecha de inicio.'
                })

        porcentaje = data.get('porcentaje_avance', 0)
        estado = data.get('estado', 'PENDIENTE')

        if estado == 'COMPLETADO' and porcentaje < 100:
            raise serializers.ValidationError({
                'porcentaje_avance': 'El porcentaje debe ser 100% para marcar como completado.'
            })

        return data


class PlanMejoraResumenSerializer(serializers.Serializer):
    """Serializer para el resumen/estadísticas de planes."""
    total_planes = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    en_curso = serializers.IntegerField()
    completados = serializers.IntegerField()
    vencidos = serializers.IntegerField()
    porcentaje_promedio_avance = serializers.FloatField()


# ─────────────── HALLAZGO ───────────────

class HallazgoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de hallazgos."""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    severidad_display = serializers.CharField(source='get_severidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    criterio_codigo = serializers.CharField(source='criterio.codigo', read_only=True, default='')
    criterio_nombre = serializers.CharField(source='criterio.nombre', read_only=True, default='')
    plan_mejora_numero = serializers.CharField(source='plan_mejora.numero_plan', read_only=True, default='')

    class Meta:
        model = Hallazgo
        fields = [
            'id', 'numero_hallazgo', 'descripcion',
            'tipo', 'tipo_display',
            'severidad', 'severidad_display',
            'estado', 'estado_display',
            'area_responsable',
            'autoevaluacion_id', 'datos_prestador_id',
            'criterio_id', 'criterio_codigo', 'criterio_nombre',
            'plan_mejora_id', 'plan_mejora_numero',
            'fecha_identificacion', 'fecha_cierre',
            'observaciones',
            'fecha_creacion', 'fecha_actualizacion',
        ]


class HallazgoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar hallazgos."""

    class Meta:
        model = Hallazgo
        fields = [
            'numero_hallazgo', 'descripcion',
            'tipo', 'severidad', 'estado',
            'area_responsable',
            'autoevaluacion', 'datos_prestador',
            'criterio', 'plan_mejora',
            'fecha_identificacion', 'fecha_cierre',
            'observaciones',
        ]

    def validate(self, data):
        estado = data.get('estado')
        fecha_cierre = data.get('fecha_cierre')

        if estado == 'CERRADO' and not fecha_cierre:
            raise serializers.ValidationError({
                'fecha_cierre': 'Se requiere fecha de cierre para cerrar un hallazgo.'
            })

        return data


class EstadisticasHallazgosSerializer(serializers.Serializer):
    """Serializer para estadísticas de hallazgos."""
    total_hallazgos = serializers.IntegerField()
    fortalezas = serializers.IntegerField()
    oportunidades_mejora = serializers.IntegerField()
    no_conformidades = serializers.IntegerField()
    hallazgos = serializers.IntegerField()
    abiertos = serializers.IntegerField()
    en_seguimiento = serializers.IntegerField()
    cerrados = serializers.IntegerField()
    criticos = serializers.IntegerField()
```

---

## 7. Paso 6: ViewSets

### Archivo: `habilitacion/views.py`

Agregar los ViewSets:

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import PlanMejora, Hallazgo
from .serializers import (
    PlanMejoraListSerializer,
    PlanMejoraDetailSerializer,
    PlanMejoraCreateUpdateSerializer,
    PlanMejoraResumenSerializer,
    HallazgoListSerializer,
    HallazgoCreateUpdateSerializer,
    EstadisticasHallazgosSerializer,
)


# ─────────────── PLAN DE MEJORA ───────────────

class PlanMejoraViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Planes de Mejora.

    Endpoints:
        GET    /planes-mejora/                    → Listar todos
        POST   /planes-mejora/                    → Crear
        GET    /planes-mejora/{id}/                → Detalle
        PUT    /planes-mejora/{id}/                → Actualizar completo
        PATCH  /planes-mejora/{id}/                → Actualizar parcial
        DELETE /planes-mejora/{id}/                → Eliminar
        GET    /planes-mejora/vencidos/            → Planes vencidos
        GET    /planes-mejora/proximos_vencer/     → Próximos a vencer
        GET    /planes-mejora/resumen/{id}/        → Resumen por autoevaluación
    """

    queryset = PlanMejora.objects.select_related(
        'criterio', 'autoevaluacion', 'responsable', 'cumplimiento'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['autoevaluacion', 'criterio', 'estado', 'responsable']
    search_fields = ['numero_plan', 'descripcion', 'acciones_implementar']
    ordering_fields = ['fecha_creacion', 'fecha_vencimiento', 'porcentaje_avance', 'estado']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action == 'list':
            return PlanMejoraListSerializer
        elif self.action == 'retrieve':
            return PlanMejoraDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PlanMejoraCreateUpdateSerializer
        return PlanMejoraListSerializer

    # ─── Actions personalizadas ───

    @action(detail=False, methods=['get'], url_path='vencidos')
    def vencidos(self, request):
        """Planes de mejora con fecha de vencimiento pasada y no completados."""
        queryset = self.get_queryset().filter(
            fecha_vencimiento__lt=timezone.now().date()
        ).exclude(estado='COMPLETADO')

        # Aplicar filtros adicionales si vienen
        autoevaluacion = request.query_params.get('autoevaluacion')
        if autoevaluacion:
            queryset = queryset.filter(autoevaluacion_id=autoevaluacion)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlanMejoraListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PlanMejoraListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='proximos-vencer')
    def proximos_vencer(self, request):
        """Planes que vencen en los próximos N días (default: 30)."""
        dias = int(request.query_params.get('dias', 30))
        fecha_limite = timezone.now().date() + timezone.timedelta(days=dias)

        queryset = self.get_queryset().filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date()
        ).exclude(estado__in=['COMPLETADO', 'VENCIDO'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlanMejoraListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PlanMejoraListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path=r'resumen/(?P<autoevaluacion_id>\d+)')
    def resumen(self, request, autoevaluacion_id=None):
        """Estadísticas resumidas de planes de mejora para una autoevaluación."""
        queryset = self.get_queryset().filter(autoevaluacion_id=autoevaluacion_id)

        data = {
            'total_planes': queryset.count(),
            'pendientes': queryset.filter(estado='PENDIENTE').count(),
            'en_curso': queryset.filter(estado='EN_CURSO').count(),
            'completados': queryset.filter(estado='COMPLETADO').count(),
            'vencidos': queryset.filter(
                fecha_vencimiento__lt=timezone.now().date()
            ).exclude(estado='COMPLETADO').count(),
            'porcentaje_promedio_avance': queryset.aggregate(
                avg=Avg('porcentaje_avance')
            )['avg'] or 0.0,
        }

        serializer = PlanMejoraResumenSerializer(data)
        return Response(serializer.data)


# ─────────────── HALLAZGO ───────────────

class HallazgoViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Hallazgos.

    Endpoints:
        GET    /hallazgos/                              → Listar todos
        POST   /hallazgos/                              → Crear
        GET    /hallazgos/{id}/                          → Detalle
        PUT    /hallazgos/{id}/                          → Actualizar
        PATCH  /hallazgos/{id}/                          → Actualizar parcial
        DELETE /hallazgos/{id}/                          → Eliminar
        GET    /hallazgos/estadisticas/{id}/              → Estadísticas por autoevaluación
    """

    queryset = Hallazgo.objects.select_related(
        'autoevaluacion', 'datos_prestador', 'criterio', 'plan_mejora'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['autoevaluacion', 'datos_prestador', 'tipo', 'severidad', 'estado', 'criterio']
    search_fields = ['numero_hallazgo', 'descripcion', 'area_responsable']
    ordering_fields = ['fecha_creacion', 'fecha_identificacion', 'severidad', 'estado']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HallazgoCreateUpdateSerializer
        return HallazgoListSerializer

    @action(detail=False, methods=['get'], url_path=r'estadisticas/(?P<autoevaluacion_id>\d+)')
    def estadisticas(self, request, autoevaluacion_id=None):
        """Estadísticas de hallazgos para una autoevaluación."""
        queryset = self.get_queryset().filter(autoevaluacion_id=autoevaluacion_id)

        data = {
            'total_hallazgos': queryset.count(),
            'fortalezas': queryset.filter(tipo='FORTALEZA').count(),
            'oportunidades_mejora': queryset.filter(tipo='OPORTUNIDAD_MEJORA').count(),
            'no_conformidades': queryset.filter(tipo='NO_CONFORMIDAD').count(),
            'hallazgos': queryset.filter(tipo='HALLAZGO').count(),
            'abiertos': queryset.filter(estado='ABIERTO').count(),
            'en_seguimiento': queryset.filter(estado='EN_SEGUIMIENTO').count(),
            'cerrados': queryset.filter(estado='CERRADO').count(),
            'criticos': queryset.filter(severidad='CRÍTICA').count(),
        }

        serializer = EstadisticasHallazgosSerializer(data)
        return Response(serializer.data)
```

---

## 8. Paso 7: URLs (Router)

### Archivo: `habilitacion/urls.py`

Agregar al router existente:

```python
from rest_framework.routers import DefaultRouter
from .views import (
    # ... ViewSets existentes ...
    DatosPrestadorViewSet,
    ServicioSedeViewSet,
    AutoevaluacionViewSet,
    CumplimientoViewSet,
    # Nuevos ViewSets
    PlanMejoraViewSet,
    HallazgoViewSet,
)

router = DefaultRouter()

# Rutas existentes
router.register(r'prestadores', DatosPrestadorViewSet)
router.register(r'servicios', ServicioSedeViewSet)
router.register(r'autoevaluaciones', AutoevaluacionViewSet)
router.register(r'cumplimientos', CumplimientoViewSet)

# ═══ NUEVAS RUTAS ═══
router.register(r'planes-mejora', PlanMejoraViewSet, basename='plan-mejora')
router.register(r'hallazgos', HallazgoViewSet, basename='hallazgo')

urlpatterns = router.urls
```

### Verificar: `config/urls.py` (archivo principal)

Asegurar que las URLs de habilitación estén incluidas:

```python
# config/urls.py (o el archivo principal de URLs)
from django.urls import path, include

urlpatterns = [
    # ... otras rutas ...
    path('api/habilitacion/', include('habilitacion.urls')),
    # ... otras rutas ...
]
```

---

## 9. Paso 8: Admin

### Archivo: `habilitacion/admin.py`

```python
from django.contrib import admin
from .models import PlanMejora, Hallazgo


@admin.register(PlanMejora)
class PlanMejoraAdmin(admin.ModelAdmin):
    list_display = [
        'numero_plan', 'descripcion_corta', 'estado',
        'porcentaje_avance', 'fecha_vencimiento',
        'autoevaluacion', 'responsable',
    ]
    list_filter = ['estado', 'fecha_vencimiento', 'autoevaluacion']
    search_fields = ['numero_plan', 'descripcion', 'acciones_implementar']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_editable = ['estado', 'porcentaje_avance']
    date_hierarchy = 'fecha_creacion'

    fieldsets = (
        ('Identificación', {
            'fields': ('numero_plan', 'descripcion')
        }),
        ('Relaciones', {
            'fields': ('cumplimiento', 'criterio', 'autoevaluacion', 'responsable')
        }),
        ('Plan de Acción', {
            'fields': (
                'estado_cumplimiento_actual', 'objetivo_mejorado',
                'acciones_implementar',
            )
        }),
        ('Seguimiento', {
            'fields': (
                'fecha_inicio', 'fecha_vencimiento', 'fecha_implementacion',
                'porcentaje_avance', 'estado',
            )
        }),
        ('Evidencia', {
            'fields': ('evidencia', 'observaciones'),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + '...' if len(obj.descripcion) > 60 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'


@admin.register(Hallazgo)
class HallazgoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_hallazgo', 'tipo', 'severidad', 'estado',
        'autoevaluacion', 'fecha_identificacion',
    ]
    list_filter = ['tipo', 'severidad', 'estado', 'autoevaluacion']
    search_fields = ['numero_hallazgo', 'descripcion', 'area_responsable']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_identificacion'

    fieldsets = (
        ('Identificación', {
            'fields': ('numero_hallazgo', 'descripcion', 'tipo', 'severidad')
        }),
        ('Relaciones', {
            'fields': ('autoevaluacion', 'datos_prestador', 'criterio', 'plan_mejora')
        }),
        ('Seguimiento', {
            'fields': ('area_responsable', 'estado', 'fecha_identificacion', 'fecha_cierre')
        }),
        ('Notas', {
            'fields': ('observaciones',),
            'classes': ('collapse',),
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )
```

---

## 10. Paso 9: Signals (opcional)

### Archivo: `habilitacion/signals.py`

Para auto-actualizar el estado de un plan cuando vence:

```python
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import PlanMejora


@receiver(pre_save, sender=PlanMejora)
def auto_marcar_vencido(sender, instance, **kwargs):
    """
    Automáticamente marca un plan como VENCIDO si la fecha de vencimiento pasó
    y el estado no es COMPLETADO.
    """
    if instance.estado not in ['COMPLETADO', 'VENCIDO']:
        if instance.fecha_vencimiento and instance.fecha_vencimiento < timezone.now().date():
            instance.estado = 'VENCIDO'


@receiver(pre_save, sender=PlanMejora)
def auto_completar_fecha_implementacion(sender, instance, **kwargs):
    """
    Si el estado cambia a COMPLETADO y no tiene fecha_implementacion,
    la establece automáticamente.
    """
    if instance.estado == 'COMPLETADO' and not instance.fecha_implementacion:
        instance.fecha_implementacion = timezone.now().date()
```

### Registrar signals en `habilitacion/apps.py`

```python
from django.apps import AppConfig


class HabilitacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'habilitacion'
    verbose_name = 'Habilitación'

    def ready(self):
        import habilitacion.signals  # noqa: F401
```

---

## 11. Paso 10: Tests

### Archivo: `habilitacion/tests/test_plan_mejora.py`

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta

from habilitacion.models import PlanMejora, Autoevaluacion, DatosPrestador

User = get_user_model()


class PlanMejoraModelTest(TestCase):
    """Tests para el modelo PlanMejora."""

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test123')
        # Crear dependencias necesarias (DatosPrestador, Autoevaluacion)
        # ... setup de datos de prueba ...

    def test_crear_plan_mejora(self):
        """Verifica la creación básica de un plan de mejora."""
        plan = PlanMejora.objects.create(
            numero_plan='PM-2026-001',
            descripcion='Plan de prueba',
            autoevaluacion=self.autoevaluacion,
            acciones_implementar='Acción de prueba',
            fecha_inicio=timezone.now().date(),
            fecha_vencimiento=timezone.now().date() + timedelta(days=30),
        )
        self.assertEqual(plan.estado, 'PENDIENTE')
        self.assertEqual(plan.porcentaje_avance, 0)

    def test_plan_vencido(self):
        """Verifica la detección de planes vencidos."""
        plan = PlanMejora.objects.create(
            numero_plan='PM-2026-002',
            descripcion='Plan vencido',
            autoevaluacion=self.autoevaluacion,
            acciones_implementar='Acción vencida',
            fecha_inicio=timezone.now().date() - timedelta(days=60),
            fecha_vencimiento=timezone.now().date() - timedelta(days=1),
        )
        self.assertTrue(plan.esta_vencido)

    def test_plan_proximo_a_vencer(self):
        """Verifica la detección de planes próximos a vencer."""
        plan = PlanMejora.objects.create(
            numero_plan='PM-2026-003',
            descripcion='Plan próximo a vencer',
            autoevaluacion=self.autoevaluacion,
            acciones_implementar='Acción urgente',
            fecha_inicio=timezone.now().date(),
            fecha_vencimiento=timezone.now().date() + timedelta(days=15),
        )
        self.assertTrue(plan.proximo_a_vencer)


class PlanMejoraAPITest(TestCase):
    """Tests para los endpoints de la API de PlanMejora."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test', password='test123')
        self.client.force_authenticate(user=self.user)
        # Crear dependencias necesarias
        # ...

    def test_listar_planes(self):
        """GET /api/habilitacion/planes-mejora/"""
        response = self.client.get('/api/habilitacion/planes-mejora/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_plan(self):
        """POST /api/habilitacion/planes-mejora/"""
        data = {
            'numero_plan': 'PM-2026-010',
            'descripcion': 'Plan nuevo',
            'autoevaluacion': self.autoevaluacion.id,
            'acciones_implementar': 'Implementar cambios',
            'fecha_inicio': str(timezone.now().date()),
            'fecha_vencimiento': str(timezone.now().date() + timedelta(days=30)),
        }
        response = self.client.post('/api/habilitacion/planes-mejora/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_planes_vencidos(self):
        """GET /api/habilitacion/planes-mejora/vencidos/"""
        response = self.client.get('/api/habilitacion/planes-mejora/vencidos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_planes_proximos_vencer(self):
        """GET /api/habilitacion/planes-mejora/proximos-vencer/?dias=30"""
        response = self.client.get('/api/habilitacion/planes-mejora/proximos-vencer/', {'dias': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resumen_por_autoevaluacion(self):
        """GET /api/habilitacion/planes-mejora/resumen/{id}/"""
        response = self.client.get(f'/api/habilitacion/planes-mejora/resumen/{self.autoevaluacion.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_planes', response.data)
        self.assertIn('pendientes', response.data)


class HallazgoAPITest(TestCase):
    """Tests para los endpoints de la API de Hallazgo."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test', password='test123')
        self.client.force_authenticate(user=self.user)

    def test_listar_hallazgos(self):
        """GET /api/habilitacion/hallazgos/"""
        response = self.client.get('/api/habilitacion/hallazgos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_estadisticas(self):
        """GET /api/habilitacion/hallazgos/estadisticas/{id}/"""
        response = self.client.get(f'/api/habilitacion/hallazgos/estadisticas/{self.autoevaluacion.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_hallazgos', response.data)
```

---

## 12. Endpoints Resultantes

### PlanMejora

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/habilitacion/planes-mejora/` | Listar todos (paginado, filtros, search) |
| `POST` | `/api/habilitacion/planes-mejora/` | Crear plan de mejora |
| `GET` | `/api/habilitacion/planes-mejora/{id}/` | Detalle de un plan |
| `PUT` | `/api/habilitacion/planes-mejora/{id}/` | Actualizar completo |
| `PATCH` | `/api/habilitacion/planes-mejora/{id}/` | Actualizar parcial |
| `DELETE` | `/api/habilitacion/planes-mejora/{id}/` | Eliminar plan |
| `GET` | `/api/habilitacion/planes-mejora/vencidos/` | Planes vencidos |
| `GET` | `/api/habilitacion/planes-mejora/proximos-vencer/?dias=30` | Próximos a vencer |
| `GET` | `/api/habilitacion/planes-mejora/resumen/{autoevaluacion_id}/` | Resumen estadístico |

**Query Parameters disponibles en listados**:
- `?page=N` — Paginación (20 items/página)
- `?search=texto` — Buscar en numero_plan, descripcion, acciones
- `?autoevaluacion=ID` — Filtrar por autoevaluación
- `?criterio=ID` — Filtrar por criterio
- `?estado=PENDIENTE` — Filtrar por estado
- `?responsable=ID` — Filtrar por responsable
- `?ordering=-fecha_vencimiento` — Ordenar (prefijo `-` = descendente)

### Hallazgo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/habilitacion/hallazgos/` | Listar todos |
| `POST` | `/api/habilitacion/hallazgos/` | Crear hallazgo |
| `GET` | `/api/habilitacion/hallazgos/{id}/` | Detalle |
| `PUT` | `/api/habilitacion/hallazgos/{id}/` | Actualizar completo |
| `PATCH` | `/api/habilitacion/hallazgos/{id}/` | Actualizar parcial |
| `DELETE` | `/api/habilitacion/hallazgos/{id}/` | Eliminar |
| `GET` | `/api/habilitacion/hallazgos/estadisticas/{autoevaluacion_id}/` | Estadísticas |

**Query Parameters disponibles en listados**:
- `?page=N` — Paginación
- `?search=texto` — Buscar en numero_hallazgo, descripcion, area_responsable
- `?autoevaluacion=ID` — Filtrar por autoevaluación
- `?tipo=NO_CONFORMIDAD` — Filtrar por tipo
- `?severidad=CRÍTICA` — Filtrar por severidad
- `?estado=ABIERTO` — Filtrar por estado
- `?criterio=ID` — Filtrar por criterio
- `?ordering=-severidad` — Ordenar

---

## 13. Diagrama Relacional Actualizado

```
┌─────────────────────────────────────────────────────────────────┐
│                    HABILITACION - MODELOS                       │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  DatosPrestador  │
    │  (existente)     │
    └────────┬─────────┘
             │ 1:N
             │
    ┌────────▼───────────────┐
    │  Autoevaluacion        │
    │  (existente)           │
    └────┬──────────┬────────┘
         │ 1:N      │ 1:N
         │          │
    ┌────▼────┐  ┌──▼──────────────┐
    │Cumplim. │  │  PlanMejora     │ ◄── NUEVO
    │(existe) │  │  (numero_plan,  │
    └────┬────┘  │   estado,       │
         │ 1:N   │   porcentaje,   │
         │       │   acciones,     │
         ├───────┤   responsable,  │
         │       │   vencimiento)  │
         │       └────┬────────────┘
         │            │ 1:N
         │       ┌────▼────────────┐
         │       │  Hallazgo       │ ◄── NUEVO
         │       │  (numero,       │
         │       │   tipo,         │
         │       │   severidad,    │
         │       │   estado)       │
         │       └─────────────────┘
         │
    ┌────▼──────┐
    │ Criterio  │  (app: normativity)
    │(existente)│
    └───────────┘

    Relaciones clave:
    ─────────────────
    PlanMejora.cumplimiento     → Cumplimiento (N:1, opcional)
    PlanMejora.autoevaluacion   → Autoevaluacion (N:1, obligatorio)
    PlanMejora.criterio         → Criterio (N:1, opcional)
    PlanMejora.responsable      → User (N:1, opcional)
    Hallazgo.plan_mejora        → PlanMejora (N:1, opcional)
    Hallazgo.autoevaluacion     → Autoevaluacion (N:1, obligatorio)
    Hallazgo.datos_prestador    → DatosPrestador (N:1, opcional)
    Hallazgo.criterio           → Criterio (N:1, opcional)
```

---

## 14. Checklist de Implementación

### Orden de ejecución

- [ ] **1.** Agregar modelo `PlanMejora` en `habilitacion/models.py`
- [ ] **2.** Agregar modelo `Hallazgo` en `habilitacion/models.py`
- [ ] **3.** (Opcional) Agregar propiedades de conveniencia en `Cumplimiento`
- [ ] **4.** Ejecutar `python manage.py makemigrations habilitacion`
- [ ] **5.** Revisar la migración generada
- [ ] **6.** Ejecutar `python manage.py migrate habilitacion`
- [ ] **7.** Crear serializers en `habilitacion/serializers.py`
- [ ] **8.** Crear ViewSets en `habilitacion/views.py`
- [ ] **9.** Registrar rutas en `habilitacion/urls.py`
- [ ] **10.** Registrar en admin en `habilitacion/admin.py`
- [ ] **11.** (Opcional) Crear signals en `habilitacion/signals.py`
- [ ] **12.** (Opcional) Registrar signals en `habilitacion/apps.py`
- [ ] **13.** Ejecutar tests: `python manage.py test habilitacion`
- [ ] **14.** Probar endpoints con Postman/curl
- [ ] **15.** Actualizar `documentos.md` con los nuevos endpoints

### Verificación post-implementación

```bash
# 1. Verificar que las migraciones están aplicadas
python manage.py showmigrations habilitacion

# 2. Verificar que las tablas existen
python manage.py dbshell
# SQL> SELECT * FROM habilitacion_plan_mejora LIMIT 1;
# SQL> SELECT * FROM habilitacion_hallazgo LIMIT 1;

# 3. Verificar que las rutas están registradas
python manage.py show_urls | grep planes-mejora
python manage.py show_urls | grep hallazgos

# 4. Ejecutar el servidor y probar
python manage.py runserver
# GET http://localhost:8000/api/habilitacion/planes-mejora/
# GET http://localhost:8000/api/habilitacion/hallazgos/
```

### Alineación con el Frontend

El frontend (React/TypeScript) ya tiene preparadas las siguientes capas que consumirán estos endpoints exactos:

| Capa Frontend | Archivo | Endpoint que consume |
|---------------|---------|---------------------|
| Entity | `domain/entities/PlanMejora.ts` | Tipado de respuesta |
| Repository Interface | `domain/repositories/IPlanMejoraRepository.ts` | Contrato |
| Repository Impl | `infrastructure/repositories/PlanMejoraRepository.ts` | `/habilitacion/planes-mejora/` |
| Service | `application/services/PlanMejoraService.ts` | Lógica de negocio |
| Hook | `presentation/hooks/usePlanMejora.ts` | Estado React |
| Pages | `PlanesMejoraPage.tsx`, `DashboardHabilitacionPageEnhanced.tsx` | UI |

**No se necesitan cambios en el frontend** — los endpoints del backend coincidirán exactamente con lo que el frontend ya está llamando.

---

**Fin del documento**
