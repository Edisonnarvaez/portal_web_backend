from django.db import models
class TipoTercero(models.Model):
    tercero_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Tipo del tercero")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "terceros_tipotercero"
        verbose_name = "Tipo de tercero"
        verbose_name_plural = "Tipo de terceros"