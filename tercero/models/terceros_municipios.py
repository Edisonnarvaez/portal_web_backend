from django.db import models
from .terceros_departamentos import Departamento

class Municipio(models.Model):
    municipio_id = models.AutoField(primary_key=True, verbose_name="ID Municipio")
    municipio_codigo = models.CharField(max_length=100, verbose_name="codigo del municipio")
    municipio_nombre = models.CharField(max_length=100, verbose_name="Nombre del municipio")
    municipio_departamento = models.ForeignKey(
        Departamento, on_delete=models.CASCADE, related_name='municipios', verbose_name="Departamento"
    )

    def __str__(self):
        return self.municipio_nombre

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "MUNICIPIOS"
