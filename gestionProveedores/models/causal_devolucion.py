from django.db import models

class CausalDevolucion(models.Model):
    causalid = models.AutoField(primary_key=True, verbose_name="ID")
    causal_nombre = models.CharField(max_length=200, default="", verbose_name="Nombre")
    causal_fecha = models.DateField(null=True, blank=True, verbose_name="Fecha")
    causal_estado = models.BooleanField(default=True, verbose_name="Status")

    def __str__(self):
        return self.causal_nombre
    class Meta:
        verbose_name = "Causal Devolución"
        verbose_name_plural = "CAUSAL DEVOLUCIONES"