from django.db import models
from .factura import Factura
from .causal_devolucion import CausalDevolucion
from .estado_impuestos import EstadoImpuestos

class RevisionImpuestos(models.Model):
    revision_impuestos_id = models.AutoField(primary_key=True)
    revision_impuestos_estado_impuestos = models.ForeignKey(
        EstadoImpuestos,
        on_delete=models.CASCADE,
        default=1  
    )
    revision_impuestos_observaciones = models.TextField(blank=True, null=True)
    revision_impuestos_estado = models.BooleanField(default=True)

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        null=False,
        related_name='etapas_impuestos'
    )
    
    revision_impuestos_causal_devolucion = models.ForeignKey(
        CausalDevolucion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revision_impuestos',
        verbose_name="Causal devolución por revisión impuestos"
    )
    def __str__(self):
        return f"Revision de impuestos de la factura con ID: {self.factura.factura_id}"
    class Meta:
        verbose_name = "Revisión impuestos"
        verbose_name_plural = "Etapa 4 : Revisión Impuestos"