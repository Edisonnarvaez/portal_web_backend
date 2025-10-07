from django.db import models
from .factura import Factura

class FacturaElectronicaDetalle(models.Model):
    descripcionFactura = models.TextField(default="", verbose_name="Descripción")
    observacionesGestion = models.TextField(blank=True, null=True, verbose_name="Observaciones de gestión")
    observacionesInconsistencias = models.TextField(blank=True, null=True, verbose_name="Observaciones de inconsistencias")
    observacionesConformidad = models.TextField(blank=True, null=True,verbose_name="Observaciones de conformidad")
    observacionesPago = models.TextField(blank=True, null=True, verbose_name="Observaciones de pago")
    observacionesContabilidad = models.TextField(blank=True, null=True, verbose_name="Observaciones de contabilidad")
    observacionesRevision = models.TextField(blank=True, null=True, verbose_name="Observaciones de revisión")
    observacionesImpuestos = models.TextField(blank=True, null=True, verbose_name="Observaciones de impuestos")
    observacionesContraloria = models.TextField(blank=True, null=True,verbose_name="Observaciones de contraloría")
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    estado = models.CharField(max_length=50, default="")

    def __str__(self):
        return f"Detalle de Factura ID {self.factura.factura_id}"
    class Meta:
        verbose_name = "Factura Detalle"
        verbose_name_plural = "DETALLES DE LAS FACTURAS"