"""
habilitacion/admin.py

Administración avanzada para habilitación de servicios de salud.
Incluye validaciones, visualizaciones coloridas y acciones en lote.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone

from .models import DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento


# ============================================================================
# COLORES Y UTILIDADES
# ============================================================================

ESTADO_HABILITACION_COLORS = {
    'HABILITADA': '#28a745',      # Verde
    'EN_PROCESO': '#ffc107',       # Amarillo
    'SUSPENDIDA': '#dc3545',       # Rojo
    'NO_HABILITADA': '#6c757d',    # Gris
    'CANCELADA': '#000000',         # Negro
}

ESTADO_SERVICIO_COLORS = {
    'HABILITADO': '#28a745',       # Verde
    'EN_PROCESO': '#ffc107',       # Amarillo
    'SUSPENDIDO': '#dc3545',       # Rojo
    'NO_HABILITADO': '#6c757d',    # Gris
    'CANCELADO': '#000000',         # Negro
}

ESTADO_AUTOEVALUACION_COLORS = {
    'BORRADOR': '#6c757d',         # Gris
    'EN_CURSO': '#17a2b8',         # Azul
    'COMPLETADA': '#28a745',       # Verde
    'REVISADA': '#ffc107',         # Amarillo
    'VALIDADA': '#007bff',         # Azul Oscuro
}

CUMPLIMIENTO_COLORS = {
    'CUMPLE': '#28a745',           # Verde
    'NO_CUMPLE': '#dc3545',        # Rojo
    'PARCIALMENTE': '#ffc107',     # Amarillo
    'NO_APLICA': '#6c757d',        # Gris
}

COMPLEJIDAD_COLORS = {
    'BAJA': '#28a745',             # Verde
    'MEDIA': '#ffc107',            # Amarillo
    'ALTA': '#dc3545',             # Rojo
}


def colored_badge(value, color_dict, text=None):
    """Crear un badge coloreado HTML."""
    if value not in color_dict:
        return value
    color = color_dict[value]
    display_text = text or value
    return format_html(
        '<span style="background-color: {}; color: white; padding: 4px 8px; '
        'border-radius: 4px; font-weight: bold;">{}</span>',
        color,
        display_text
    )


# ============================================================================
# ADMIN: DatosPrestador
# ============================================================================

@admin.register(DatosPrestador)
class DatosPrestadorAdmin(admin.ModelAdmin):
    """Administración de datos de prestadores habilitados."""
    
    list_display = [
        'codigo_reps_link',
        'headquarters_link',
        'clase_prestador_badge',
        'estado_habilitacion_badge',
        'vencimiento_status',
        'poliza_icon',
        'fecha_creacion',
    ]
    
    list_filter = [
        'estado_habilitacion',
        'clase_prestador',
        'fecha_vencimiento_habilitacion',
    ]
    
    search_fields = [
        'codigo_reps',
        'headquarters__nombre',
        'aseguradora_pep',
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'dias_para_vencimiento_display',
        'estado_actual_display',
    ]
    
    fieldsets = (
        ('Identificación REPS', {
            'fields': (
                'headquarters',
                'codigo_reps',
                'clase_prestador',
            )
        }),
        ('Estado de Habilitación', {
            'fields': (
                'estado_habilitacion',
                'estado_actual_display',
                'fecha_inscripcion',
                'fecha_renovacion',
                'fecha_vencimiento_habilitacion',
                'dias_para_vencimiento_display',
            )
        }),
        ('Responsabilidad Civil', {
            'fields': (
                'aseguradora_pep',
                'numero_poliza',
                'vigencia_poliza',
            )
        }),
        ('Auditoría', {
            'fields': (
                'usuario_responsable',
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def codigo_reps_link(self, obj):
        """Link al código REPS con color."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:habilitacion_datosprestador_change', args=[obj.pk]),
            obj.codigo_reps
        )
    codigo_reps_link.short_description = 'Código REPS'
    
    def headquarters_link(self, obj):
        """Link a la sede."""
        url = reverse('admin:companies_headquarters_change', args=[obj.headquarters.pk])
        return format_html('<a href="{}">{}</a>', url, obj.headquarters.name)
    headquarters_link.short_description = 'Sede (Headquarters)'
    
    def clase_prestador_badge(self, obj):
        """Badge de clase de prestador."""
        colors = {
            'IPS': '#007bff',
            'PROF': '#28a745',
            'PH': '#17a2b8',
            'PJ': '#6c757d',
        }
        return colored_badge(obj.clase_prestador, colors)
    clase_prestador_badge.short_description = 'Clase'
    
    def estado_habilitacion_badge(self, obj):
        """Badge del estado de habilitación."""
        return colored_badge(
            obj.estado_habilitacion,
            ESTADO_HABILITACION_COLORS
        )
    estado_habilitacion_badge.short_description = 'Estado'
    
    def vencimiento_status(self, obj):
        """Indicador visual de vencimiento."""
        if obj.esta_vencida():
            return colored_badge('VENCIDA', {'VENCIDA': '#dc3545'})
        elif obj.esta_proxima_a_vencer(dias=90):
            return colored_badge('PRÓXIMA A VENCER', {'PRÓXIMA A VENCER': '#ffc107'})
        else:
            return colored_badge('VIGENTE', {'VIGENTE': '#28a745'})
    vencimiento_status.short_description = 'Vigencia'
    
    def poliza_icon(self, obj):
        """Icono indicando si tiene póliza vigente."""
        if obj.vigencia_poliza and obj.vigencia_poliza > timezone.now().date():
            return format_html(
                '<span style="color: #28a745; font-size: 18px;">✓</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-size: 18px;">✗</span>'
        )
    poliza_icon.short_description = 'Póliza'
    
    def dias_para_vencimiento_display(self, obj):
        """Días para vencimiento (readonly)."""
        dias = obj.dias_para_vencimiento()
        if dias is None:
            return '—'
        return f"{dias} días"
    dias_para_vencimiento_display.short_description = 'Días para Vencimiento'
    
    def estado_actual_display(self, obj):
        """Descripción detallada del estado."""
        if obj.esta_vencida():
            return 'VENCIDA'
        elif obj.esta_proxima_a_vencer(dias=90):
            dias = obj.dias_para_vencimiento()
            return f'Próxima a vencer en {dias} días'
        else:
            dias = obj.dias_para_vencimiento()
            return f'Vigente ({dias} días)'
    estado_actual_display.short_description = 'Estado Actual'


# ============================================================================
# ADMIN: ServicioSede
# ============================================================================

@admin.register(ServicioSede)
class ServicioSedeAdmin(admin.ModelAdmin):
    """Administración de servicios de salud por sede."""
    
    list_display = [
        'codigo_servicio_link',
        'sede_link',
        'modalidad_badge',
        'complejidad_badge',
        'estado_habilitacion_badge',
        'fecha_vencimiento_display',
        'cumplimientos_count',
    ]
    
    list_filter = [
        'modalidad',
        'complejidad',
        'estado_habilitacion',
        'sede__company',
    ]
    
    search_fields = [
        'codigo_servicio',
        'nombre_servicio',
        'sede__name',
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'vencimiento_display',
        'cumplimientos_count',
    ]
    
    fieldsets = (
        ('Identificación', {
            'fields': (
                'sede',
                'codigo_servicio',
                'nombre_servicio',
                'descripcion',
            )
        }),
        ('Clasificación', {
            'fields': (
                'modalidad',
                'complejidad',
            )
        }),
        ('Habilitación', {
            'fields': (
                'estado_habilitacion',
                'fecha_habilitacion',
                'fecha_vencimiento',
                'vencimiento_display',
            )
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
                'cumplimientos_count',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def codigo_servicio_link(self, obj):
        """Link al código con color."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:habilitacion_serviciosede_change', args=[obj.pk]),
            obj.codigo_servicio
        )
    codigo_servicio_link.short_description = 'Código'
    
    def sede_link(self, obj):
        """Link a la sede."""
        url = reverse('admin:companies_headquarters_change', args=[obj.sede.pk])
        return format_html('<a href="{}">{}</a>', url, obj.sede.name)
    sede_link.short_description = 'Sede'
    
    def modalidad_badge(self, obj):
        """Badge de modalidad."""
        colors = {
            'INTRAMURAL': '#007bff',
            'AMBULATORIA': '#28a745',
            'TELEMEDICINA': '#17a2b8',
            'URGENCIAS': '#dc3545',
            'AMBULANCIA': '#6c757d',
        }
        return colored_badge(obj.modalidad, colors)
    modalidad_badge.short_description = 'Modalidad'
    
    def complejidad_badge(self, obj):
        """Badge de complejidad."""
        return colored_badge(obj.complejidad, COMPLEJIDAD_COLORS)
    complejidad_badge.short_description = 'Complejidad'
    
    def estado_habilitacion_badge(self, obj):
        """Badge del estado."""
        return colored_badge(
            obj.estado_habilitacion,
            ESTADO_SERVICIO_COLORS
        )
    estado_habilitacion_badge.short_description = 'Estado'
    
    def fecha_vencimiento_display(self, obj):
        """Mostrar vencimiento con código de color."""
        if not obj.fecha_vencimiento:
            return '—'
        if obj.esta_vencido():
            return colored_badge('VENCIDO', {'VENCIDO': '#dc3545'})
        dias = obj.dias_para_vencimiento()
        if dias <= 90:
            return colored_badge(
                f'{dias} días',
                {'temp': '#ffc107'}
            )
        return colored_badge(f'{dias} días', {'temp': '#28a745'})
    fecha_vencimiento_display.short_description = 'Vencimiento'
    
    def vencimiento_display(self, obj):
        """Información detallada de vencimiento."""
        if not obj.fecha_vencimiento:
            return 'No establecida'
        if obj.esta_vencido():
            return 'VENCIDA'
        dias = obj.dias_para_vencimiento()
        return f'Vigente ({dias} días)'
    vencimiento_display.short_description = 'Estado de Vencimiento'
    
    def cumplimientos_count(self, obj):
        """Cantidad de cumplimientos evaluados."""
        count = obj.cumplimientos.count()
        url = reverse('admin:habilitacion_cumplimiento_changelist')
        return format_html(
            '<a href="{}?servicio_sede__id__exact={}">{} evaluaciones</a>',
            url,
            obj.pk,
            count
        )
    cumplimientos_count.short_description = 'Evaluaciones'


# ============================================================================
# ADMIN: Autoevaluacion
# ============================================================================

@admin.register(Autoevaluacion)
class AutoevaluacionAdmin(admin.ModelAdmin):
    """Administración de autoevaluaciones anuales."""
    
    list_display = [
        'numero_autoevaluacion_link',
        'prestador_codigo',
        'periodo',
        'version',
        'estado_badge',
        'porcentaje_cumplimiento_bar',
        'usuario_responsable',
        'fecha_vencimiento_display',
    ]
    
    list_filter = [
        'estado',
        'periodo',
        'version',
        'datos_prestador__codigo_reps',
    ]
    
    search_fields = [
        'numero_autoevaluacion',
        'datos_prestador__codigo_reps',
    ]
    
    readonly_fields = [
        'numero_autoevaluacion',
        'fecha_inicio_display',
        'fecha_creacion',
        'fecha_actualizacion',
        'porcentaje_cumplimiento_display',
        'cumplimientos_resumen',
        'vigencia_display',
    ]
    
    fieldsets = (
        ('Identificación', {
            'fields': (
                'numero_autoevaluacion',
                'datos_prestador',
                'periodo',
                'version',
            )
        }),
        ('Estado (Editable)', {
            'fields': (
                'estado',
                'fecha_completacion',
                'fecha_vencimiento',
            )
        }),
        ('Resultados', {
            'fields': (
                'porcentaje_cumplimiento_display',
                'cumplimientos_resumen',
            )
        }),
        ('Notas', {
            'fields': (
                'observaciones',
            )
        }),
        ('Sistema (Solo Lectura)', {
            'fields': (
                'fecha_inicio_display',
                'vigencia_display',
                'usuario_responsable',
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def numero_autoevaluacion_link(self, obj):
        """Link con número de autoevaluación."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:habilitacion_autoevaluacion_change', args=[obj.pk]),
            obj.numero_autoevaluacion
        )
    numero_autoevaluacion_link.short_description = 'Autoevaluación'
    
    def prestador_codigo(self, obj):
        """Código REPS del prestador."""
        url = reverse(
            'admin:habilitacion_datosprestador_change',
            args=[obj.datos_prestador.pk]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.datos_prestador.codigo_reps
        )
    prestador_codigo.short_description = 'Prestador'
    
    def estado_badge(self, obj):
        """Badge del estado."""
        return colored_badge(obj.estado, ESTADO_AUTOEVALUACION_COLORS)
    estado_badge.short_description = 'Estado'
    
    def porcentaje_cumplimiento_bar(self, obj):
        """Barra de progreso de cumplimiento."""
        porcentaje = obj.porcentaje_cumplimiento()
        
        # Determinar color
        if porcentaje >= 80:
            color = '#28a745'  # Verde
        elif porcentaje >= 60:
            color = '#ffc107'  # Amarillo
        else:
            color = '#dc3545'  # Rojo
        
        # Formatear el porcentaje ANTES de pasarlo a format_html
        porcentaje_formateado = f"{porcentaje:.1f}"
        
        return format_html(
            '<div style="background-color: #e9ecef; border-radius: 4px; '
            'overflow: hidden; width: 150px;">'
            '<div style="background-color: {}; width: {}%; height: 20px; '
            'display: flex; align-items: center; justify-content: center; '
            'color: white; font-weight: bold; font-size: 12px;">'
            '{}%</div></div>',
            color,
            int(porcentaje),
            porcentaje_formateado
        )
    porcentaje_cumplimiento_bar.short_description = 'Cumplimiento'
    
    def porcentaje_cumplimiento_display(self, obj):
        """Porcentaje de cumplimiento (readonly)."""
        return f"{obj.porcentaje_cumplimiento():.2f}%"
    porcentaje_cumplimiento_display.short_description = 'Cumplimiento (%)'
    
    def cumplimientos_resumen(self, obj):
        """Resumen de cumplimientos por estado."""
        cumplimientos = obj.cumplimientos.all()
        total = cumplimientos.count()
        
        if total == 0:
            return 'Sin evaluaciones'
        
        cumple = cumplimientos.filter(cumple='CUMPLE').count()
        no_cumple = cumplimientos.filter(cumple='NO_CUMPLE').count()
        parcialmente = cumplimientos.filter(cumple='PARCIALMENTE').count()
        no_aplica = cumplimientos.filter(cumple='NO_APLICA').count()
        
        url = reverse('admin:habilitacion_cumplimiento_changelist')
        return format_html(
            '<a href="{}?autoevaluacion__id__exact={}">'
            'Total: {} | Cumple: {} | No cumple: {} | Parcial: {} | N/A: {}'
            '</a>',
            url,
            obj.pk,
            total,
            cumple,
            no_cumple,
            parcialmente,
            no_aplica
        )
    cumplimientos_resumen.short_description = 'Resumen de Cumplimientos'
    
    def fecha_vencimiento_display(self, obj):
        """Indicador visual de vencimiento."""
        if not obj.esta_vigente():
            return colored_badge('VENCIDA', {'VENCIDA': '#dc3545'})
        return colored_badge('VIGENTE', {'VIGENTE': '#28a745'})
    fecha_vencimiento_display.short_description = 'Vigencia'
    
    def vigencia_display(self, obj):
        """Detalle de vigencia."""
        if obj.esta_vigente():
            return 'Vigente'
        return 'Vencida'
    vigencia_display.short_description = 'Estado de Vigencia'
    
    def fecha_inicio_display(self, obj):
        """Fecha de inicio (solo lectura - auto_now_add)."""
        if obj.fecha_inicio:
            return obj.fecha_inicio.strftime('%d/%m/%Y')
        return '—'
    fecha_inicio_display.short_description = 'Fecha de Inicio'


# ============================================================================
# ADMIN: Cumplimiento
# ============================================================================

@admin.register(Cumplimiento)
class CumplimientoAdmin(admin.ModelAdmin):
    """Administración de cumplimientos de criterios."""
    
    list_display = [
        'criterio_codigo_link',
        'autoevaluacion_numero',
        'servicio_nombre',
        'cumple_badge',
        'plan_mejora_icon',
        'fecha_compromiso_display',
        'responsable_mejora_user',
    ]
    
    list_filter = [
        'cumple',
        'autoevaluacion__periodo',
        'criterio__estandar',
        'responsable_mejora',
    ]
    
    search_fields = [
        'criterio__codigo',
        'criterio__nombre',
        'hallazgo',
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'criterio_detail',
        'plan_mejora_icon',
        'mejora_estado_display',
    ]
    
    fieldsets = (
        ('Evaluación', {
            'fields': (
                'autoevaluacion',
                'servicio_sede',
                'criterio',
                'criterio_detail',
            )
        }),
        ('Resultado', {
            'fields': (
                'cumple',
                'hallazgo',
            )
        }),
        ('Plan de Mejora', {
            'fields': (
                'plan_mejora',
                'responsable_mejora',
                'fecha_compromiso',
                'mejora_estado_display',
            ),
            'classes': ('wide',),
        }),
        ('Evidencia Documental', {
            'fields': (
                'documentos_evidencia',
            )
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',),
        }),
    )
    
    filter_horizontal = ('documentos_evidencia',)
    
    def criterio_codigo_link(self, obj):
        """Link al criterio con código."""
        return format_html(
            '<a href="{}">Estándar {}: {}</a>',
            reverse(
                'admin:normativity_criterio_change',
                args=[obj.criterio.pk]
            ),
            obj.criterio.estandar.codigo,
            obj.criterio.codigo
        )
    criterio_codigo_link.short_description = 'Criterio'
    
    def autoevaluacion_numero(self, obj):
        """Número de autoevaluación."""
        url = reverse(
            'admin:habilitacion_autoevaluacion_change',
            args=[obj.autoevaluacion.pk]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.autoevaluacion.numero_autoevaluacion
        )
    autoevaluacion_numero.short_description = 'Autoevaluación'
    
    def servicio_nombre(self, obj):
        """Nombre del servicio."""
        return obj.servicio_sede.nombre_servicio
    servicio_nombre.short_description = 'Servicio'
    
    def cumple_badge(self, obj):
        """Badge de resultado de cumplimiento."""
        return colored_badge(obj.cumple, CUMPLIMIENTO_COLORS)
    cumple_badge.short_description = 'Resultado'
    
    def plan_mejora_icon(self, obj):
        """Icono indicando si hay plan de mejora."""
        if obj.plan_mejora:
            return format_html(
                '<span style="color: #28a745; font-size: 18px;">✓</span>'
            )
        return format_html(
            '<span style="color: #6c757d; font-size: 18px;">—</span>'
        )
    plan_mejora_icon.short_description = 'Plan'
    
    def fecha_compromiso_display(self, obj):
        """Mostrar fecha de compromiso con código de color."""
        if not obj.fecha_compromiso:
            return '—'
        
        hoy = timezone.now().date()
        if obj.fecha_compromiso < hoy:
            return colored_badge('VENCIDA', {'VENCIDA': '#dc3545'})
        
        dias_falta = (obj.fecha_compromiso - hoy).days
        if dias_falta <= 30:
            return colored_badge(
                f'{dias_falta} días',
                {'temp': '#ffc107'}
            )
        return colored_badge(f'{dias_falta} días', {'temp': '#28a745'})
    fecha_compromiso_display.short_description = 'Compromiso'
    
    def responsable_mejora_user(self, obj):
        """Usuario responsable de la mejora."""
        if not obj.responsable_mejora:
            return '—'
        return obj.responsable_mejora.username
    responsable_mejora_user.short_description = 'Responsable'
    
    def criterio_detail(self, obj):
        """Detalle del criterio (readonly)."""
        return format_html(
            '<strong>{}</strong> - {} <br/>'
            '<em>Complejidad: {} | Mandatorio: {} | Evidencia: {}</em>',
            obj.criterio.codigo,
            obj.criterio.nombre,
            obj.criterio.get_complejidad_display(),
            '✓' if obj.criterio.es_mandatorio else '✗',
            '✓' if obj.criterio.requiere_evidencia_documental else '✗',
        )
    criterio_detail.short_description = 'Detalle del Criterio'
    
    def mejora_estado_display(self, obj):
        """Estado de la mejora."""
        if not obj.plan_mejora:
            return 'Sin plan de mejora'
        
        if obj.cumple == 'CUMPLE':
            return 'Mejora completada'
        
        if obj.mejora_vencida():
            return 'Plazo vencido'
        
        dias_falta = (obj.fecha_compromiso - timezone.now().date()).days
        return f'Pendiente ({dias_falta} días)'
    mejora_estado_display.short_description = 'Estado de Mejora'
