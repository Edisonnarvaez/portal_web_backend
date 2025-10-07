from django.contrib import admin
from django.forms.widgets import RadioSelect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib import messages
from django.utils.html import format_html
from gestionProveedores.process_emails import process_emails
from gestionProveedores.models import (
    Factura,
    FacturaElectronicaDetalle,
    CausalDevolucion,
    GestionarFactura,
    PendienteRevision,
    PendienteReconocimientoContable,
    EstadoPendienteRContable,
    DocumentoContable,
    RevisionImpuestos,
    RevisionContraloria,
    CentroCostos,
    CentroOperaciones,
    EstadoRevision,
    EstadoFactura,
    EstadoImpuestos,
    EstadoContraloria,
    PendientePago,
    Correo,
    ArchivoAdjunto,
)



# INLINES
class FacturaElectronicaDetalleInline(admin.StackedInline):
    model = FacturaElectronicaDetalle
    extra = 0
    readonly_fields = []
    fieldsets = [
        (None, {
            'fields': [
                'descripcionFactura',
                'observacionesGestion',
                'observacionesInconsistencias',
                'observacionesConformidad',
                'observacionesPago',
                'observacionesContabilidad',
                'observacionesRevision',
                'observacionesImpuestos',
                'observacionesContraloria',
                'estado',
            ]
        }),
    ]

# FACTURA ADMIN CON ACCIÓN DE REENVÍO
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = [
        'factura_id',
        'factura_centro_operaciones',
        'factura_etapa',
        'factura_fecha',
        'factura_estado_factura',
        'factura_numero_autorizacion',
        'factura_concepto',
        'factura_razon_social_proveedor',
        'factura_razon_social_adquiriente',
    ]
    readonly_fields = ['factura_id']
    fields = [
        'factura_id',
        'factura_id_factura_electronica',
        'factura_etapa',
        'factura_fecha',
        'factura_estado_factura',
        'factura_numero_autorizacion',
        'factura_concepto',
        'factura_razon_social_proveedor',
        'factura_razon_social_adquiriente',
        'factura_valor',
        'factura_centro_operaciones',
        'factura_centro_costo',
        'causal_anulacion',
        'causal_contabilidad',
        'causal_revision',
        'causal_impuestos',
    ]
    inlines = [FacturaElectronicaDetalleInline]
    actions = ['reenviar_correo']

    def reenviar_correo(self, request, queryset):
        from gestionProveedores.reenviar_correo import reenviar_correo_factura
        for factura in queryset:
            try:
                response = reenviar_correo_factura(request, factura.factura_id)

                if response.status_code == 200:
                    self.message_user(request, f"Factura {factura.factura_id}: Correo reenviado correctamente.")
                else:
                    error = response.data.get('error', 'Error desconocido')
                    self.message_user(request, f"Factura {factura.factura_id}: {error}", level=messages.ERROR)
            except Exception as e:
                self.message_user(request, f"Factura {factura.factura_id}: {str(e)}", level=messages.ERROR)

    reenviar_correo.short_description = "📧 Reenviar correo con factura adjunta"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "factura_estado_factura":
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# OTROS MODELOS
@admin.register(CausalDevolucion)
class CausalDevolucionAdmin(admin.ModelAdmin):
    list_display = ['causalid', 'causal_nombre', 'causal_fecha']

@admin.register(GestionarFactura)
class GestionarFEAdmin(admin.ModelAdmin):
    list_display = [
        'factura_id',
        'factura_centro_op',
        'factura_estado_factura_gestion',
        'factura_estado',
        'causal_devolucion_anulacion',
        'observaciones_gestion',
        'ver_factura_relacionada'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "factura_estado_factura_gestion":
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.factura_relacionada:
            try:
                detalle = FacturaElectronicaDetalle.objects.filter(factura=obj.factura_relacionada).first()
                if detalle:
                    detalle.observacionesGestion = obj.observaciones_gestion
                    detalle.save()
            except Exception as e:
                print(f"Error actualizando detalle: {e}")

    def ver_factura_relacionada(self, obj):
        if obj.factura_relacionada:
            url = reverse('admin:gestionProveedores_factura_change', args=[obj.factura_relacionada.factura_id])
            return format_html('<a href="{}">Ver Factura #{}</a>', url, obj.factura_relacionada.factura_id)
        return "-"

    ver_factura_relacionada.short_description = "Factura Relacionada"

@admin.register(PendienteRevision)
class PendienteRevisionAdmin(admin.ModelAdmin):
    list_display = [
        'revision_id',
        'revision_fecha_gestion',
        'revision_fecha_recibe',
        'revision_centro_costo',
        'revision_estado_revision',
        'revision_estado',
        'revision_causal_revision',
        'revision_observacion_revision',
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "revision_estado_revision":
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(PendienteReconocimientoContable)
class PendienteReconocimientoContableAdmin(admin.ModelAdmin):
    list_display = ['contable_id', 'contable_NIT_prestador', 'contable_documento',
                    'contable_numero_documento', 'contable_estado_reconocimiento_contable',
                    'factura', 'contable_causal_devolucion', 'contable_estado', 'contable_observaciones']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contable_estado_reconocimiento_contable":
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(RevisionContraloria)
class RevisionContraloriaAdmin(admin.ModelAdmin):
    list_display = ['contraloria_id', 'contraloria_estado_contraloria', 'contraloria_observaciones', 'contraloria_estado']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contraloria_estado_contraloria":
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(CentroCostos)
class CentroCostoAdmin(admin.ModelAdmin):
    list_display = ['costos_id', 'costos_nombre_sede', 'costos_estado']

@admin.register(CentroOperaciones)
class CentroOperacionesAdmin(admin.ModelAdmin):
    list_display = ['operaciones_id', 'operaciones_nombre', 'operaciones_estado']

@admin.register(EstadoRevision)
class EstadoRevisionAdmin(admin.ModelAdmin):
    list_display = ['estado_id', 'nombre']

@admin.register(EstadoPendienteRContable)
class EstadoPendienteRContableAdmin(admin.ModelAdmin):
    list_display = ['estado_id', 'nombre']

@admin.register(EstadoFactura)
class EstadoFacturaAdmin(admin.ModelAdmin):
    list_display = ['estado_id', 'nombre']

@admin.register(DocumentoContable)
class DocumentoContableAdmin(admin.ModelAdmin):
    list_display = ['doc_contable_id', 'doc_contable_tipo', 'doc_contable_estado']

@admin.register(RevisionImpuestos)
class RevisionImpuestosAdmin(admin.ModelAdmin):
    list_display = ['revision_impuestos_id', 'revision_impuestos_estado_impuestos',
                    'revision_impuestos_observaciones', 'revision_impuestos_causal_devolucion', 'revision_impuestos_estado']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "revision_impuestos_estado_impuestos":
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(EstadoImpuestos)
class EstadoImpuestosAdmin(admin.ModelAdmin):
    list_display = ['estado_id', 'nombre']

@admin.register(EstadoContraloria)
class EstadoContraloriaAdmin(admin.ModelAdmin):
    list_display = ['estado_id', 'nombre']

@admin.register(PendientePago)
class PendientePagoAdmin(admin.ModelAdmin):
    list_display = ['pago_id', 'pago_realizo_pago', 'pago_soportes', 'pago_estado']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["pago_realizo_pago", "pago_soportes"]:
            kwargs["widget"] = RadioSelect()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Correo)
class CorreoAdmin(admin.ModelAdmin):
    list_display = ['subject', 'from_email', 'date_received', 'mostrar_archivos']
    readonly_fields = ['mostrar_archivos']
    fields = ('subject', 'from_email', 'date_received', 'raw_message', 'mostrar_archivos')

    def mostrar_archivos(self, obj):
        if not obj.archivos:
            return "-"
        links = []
        nombres = [nombre.strip() for nombre in obj.archivos.split(',')]
        for nombre in nombres:
            if nombre:
                url = reverse('descargar_archivo', args=[obj.id, nombre])
                links.append(f'<a href="{url}" target="_blank">{nombre}</a>')
        return mark_safe("<br>".join(links))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archivos__icontains='.zip')

    def changelist_view(self, request, extra_context=None):
        process_emails()
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('nombre_archivo', 'correo')
