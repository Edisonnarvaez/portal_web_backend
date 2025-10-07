from django.db import models
from .causal_devolucion import CausalDevolucion
from .centro_costo import CentroCostos
from .centro_operaciones import CentroOperaciones

class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True, verbose_name="ID")
    factura_id_factura_electronica = models.CharField(max_length=100, default="", null=True, blank=True, verbose_name="ID FE")

    factura_centro_operaciones = models.ForeignKey(
        CentroOperaciones,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas_operaciones',
        verbose_name="Centro de operaciones"
    )

    factura_centro_costo = models.ForeignKey(
        CentroCostos,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas_costos',
        verbose_name="Centro de costo"
    )

    factura_etapa = models.CharField(max_length=50, default="", null=True, blank=True, verbose_name="Etapa")
    factura_fecha = models.DateField(null=True, blank=True, verbose_name="Fecha")
    factura_estado_factura = models.ForeignKey(
        'gestionProveedores.EstadoFactura',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        db_column='factura_estado_factura_id',
        verbose_name="Estado factura",
        default=1
    )

    factura_numero_autorizacion = models.CharField(max_length=100, default="", null=True, blank=True, verbose_name="Factura autorizada")
    factura_concepto = models.TextField(default="", null=True, blank=True, verbose_name="Concepto")
    factura_razon_social_proveedor = models.CharField(max_length=150, default="", null=True, blank=True, verbose_name="Razón social proveedor")
    factura_razon_social_adquiriente = models.CharField(max_length=150, default="", null=True, blank=True, verbose_name="Razón social adquiriente")
    factura_valor = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="valor")
    factura_estado = models.BooleanField(default=True)

    causal_anulacion = models.ForeignKey(
        CausalDevolucion, on_delete=models.SET_NULL, null=True, blank=True, related_name='anulaciones',
        verbose_name="Causal devolución por anulación"
    )
    causal_contabilidad = models.ForeignKey(
        CausalDevolucion, on_delete=models.SET_NULL, null=True, blank=True, related_name='contabilidades',
        verbose_name="Causal devolución por contabilidad"
    )
    causal_revision = models.ForeignKey(
        CausalDevolucion, on_delete=models.SET_NULL, null=True, blank=True, related_name='revisiones',
        verbose_name="Causal devolución por revisión"
    )
    causal_impuestos = models.ForeignKey(
        CausalDevolucion, on_delete=models.SET_NULL, null=True, blank=True, related_name='impuestos',
        verbose_name="Causal devolución por impuestos"
    )

    def _str_(self):
        return f"Factura {self.factura_numero_autorizacion or self.factura_id}"


    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "FACTURAS ELECTRÓNICAS PRINCIPAL"
