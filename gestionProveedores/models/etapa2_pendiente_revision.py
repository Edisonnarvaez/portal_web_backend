from django.db import models
from .factura import Factura
from .centro_costo import CentroCostos
from .causal_devolucion import CausalDevolucion
from .estado_revision import EstadoRevision 

class PendienteRevision(models.Model):
    revision_id = models.AutoField(primary_key=True)
    revision_fecha_gestion = models.DateField(null=True, blank=True)
    revision_fecha_recibe = models.DateField(null=True, blank=True)
    
    revision_centro_costo = models.ForeignKey(
        CentroCostos,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revision_costos',
        verbose_name="Centro Costo"
    )

    revision_estado_revision = models.ForeignKey(
        'gestionProveedores.EstadoRevision',
        on_delete=models.PROTECT, 
        null=False,
        blank=False,
        db_column='revision_estado_revision_id',
        verbose_name="Estado",
        default=1  
    )
    revision_causal_revision = models.ForeignKey(
        CausalDevolucion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisiones_devolucion',
        verbose_name="Causal devolución"
    )

    revision_observacion_revision = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observación"
    )

    factura_relacionada = models.OneToOneField(
        Factura,
        on_delete=models.CASCADE,
        related_name='revision_factura',
        null=True,
        blank=True,
        verbose_name="Factura relacionada"
    )
    revision_estado = models.BooleanField(default=True,verbose_name="Status")

    def __str__(self):
        return f"Factura {self.factura_relacionada}"

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Etapa 2 : Pendiente Revisión"
 