from django.db import models
from .factura import Factura
from .documento_contable import DocumentoContable
from .estado_pendiente_r_contable import EstadoPendienteRContable
from .causal_devolucion import CausalDevolucion

class PendienteReconocimientoContable(models.Model):
    contable_id = models.AutoField(primary_key=True)
    contable_NIT_prestador = models.CharField(max_length=150, default="", verbose_name="NIT Prestador")
    contable_documento = models.ForeignKey(
    DocumentoContable,
    on_delete=models.CASCADE,
    verbose_name="Documento_Contable",
    default=1
    )
    contable_numero_documento = models.CharField(max_length=100, default="", verbose_name="Número Documento")
    contable_estado_reconocimiento_contable = models.ForeignKey(
        EstadoPendienteRContable,
        on_delete=models.CASCADE,
        verbose_name="Estado",
        default=1  
    )
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        null=False,
        related_name='etapas_contables'
    )
    contable_causal_devolucion = models.ForeignKey(
        CausalDevolucion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pendientes_reconocimiento_contable',
        verbose_name="Causal Devolución"
    )
    contable_observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    contable_estado = models.BooleanField(default=True, verbose_name="Status")
    def __str__(self):
        return f"{self.contable_documento.doc_contable_tipo}: {self.contable_documento.doc_contable_descripcion}"

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Etapa 3 : Pendiente Reconocimiento Contable"
