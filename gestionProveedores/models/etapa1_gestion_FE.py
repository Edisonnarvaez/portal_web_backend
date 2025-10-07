from django.db import models
from .causal_devolucion import CausalDevolucion
from .centro_operaciones import CentroOperaciones
from .factura_detalle import FacturaElectronicaDetalle
from .factura import Factura

class GestionarFactura(models.Model):
    factura_id = models.AutoField(primary_key=True, verbose_name="ID")
    
    factura_centro_op = models.ForeignKey(
        CentroOperaciones,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas_operaciones_gestionar', 
        verbose_name="Centro de operaciones"
    )

    factura_estado_factura_gestion = models.ForeignKey(
        'gestionProveedores.EstadoFactura',
        on_delete=models.PROTECT,  
        null=False,
        blank=False,
        db_column='factura_estado_factura_id',
        verbose_name="Estado",
        default=1  
    )
 
    causal_devolucion_anulacion = models.ForeignKey(
        CausalDevolucion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anulaciones_gestionar',  
        verbose_name="Causal Devolución y/o Anulación"
    )
    observaciones_gestion = models.TextField(
        null=True, blank=True,
        verbose_name="Observaciones gestión"
    )


    factura_relacionada = models.OneToOneField(
        Factura,
        on_delete=models.CASCADE,
        related_name='gestion_factura',  
        null=True,
        blank=True,
        verbose_name="Factura relacionada"
    )
    factura_estado = models.BooleanField(default=True, verbose_name="Status")


    def __str__(self):
        return f"Factura {self.factura_estado_factura}"

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Etapa 1 : Gestión F.E."
