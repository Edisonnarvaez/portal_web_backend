from django.db import models
from .factura import Factura
from .estados_contraloria import EstadoContraloria

class RevisionContraloria(models.Model):
    contraloria_id = models.AutoField(primary_key=True)
    contraloria_estado_contraloria = models.ForeignKey(
        EstadoContraloria,
        on_delete=models.CASCADE,
        default=1  
    )
    contraloria_observaciones = models.TextField(blank=True, null=True)
    contraloria_estado = models.BooleanField(default=True)

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        null=False,
        related_name='etapas_contraloria'
    )

    def __str__(self):
        return f"Revision por contraloria de la factura con ID: {self.factura.factura_id}"
    class Meta:
        verbose_name = "Revisión contraloría"
        verbose_name_plural = "Etapa 5: Revisión Contraloría"