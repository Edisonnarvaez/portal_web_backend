from django.db import models
from .factura import Factura

class PendientePago(models.Model):
    pago_id = models.AutoField(primary_key=True)
    pago_realizo_pago =   models.BooleanField(default=True)
    pago_soportes =  models.BooleanField(default=True)
    pago_estado = models.BooleanField(default=True)

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        null=False,
        related_name='etapas_pagos'
    )

    def __str__(self):
        return f"Pendiente de pagos de la factura con ID: {self.factura.factura_id}"
    class Meta:
        verbose_name = "Pendiente pago"
        verbose_name_plural = "Etapa 6: Tesorería/Pendiente Pagos"