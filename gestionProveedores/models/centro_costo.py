from django.db import models

class CentroCostos(models.Model):
    costos_id = models.AutoField(primary_key=True,verbose_name="ID",)
    costos_nombre_sede = models.CharField(max_length=250, default="", verbose_name="Nombre sede")
    costos_codigo = models.CharField(max_length=100, default="", verbose_name="Código")
    costos_estado = models.BooleanField(default=True, verbose_name="Status")

    def __str__(self):
     return f"Código: {self.costos_codigo}: {self.costos_nombre_sede}"

    class Meta:
        verbose_name = "Centro de costo"
        verbose_name_plural = "CENTRO DE COSTOS"