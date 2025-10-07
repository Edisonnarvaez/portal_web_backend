from django.db import models
from .terceros_paises import Pais

class Departamento(models.Model):
    departamento_id = models.AutoField(primary_key=True, verbose_name="ID Departamento")
    departamento_codigo = models.CharField(max_length=100, verbose_name="codigo del departamento")
    departamento_nombre = models.CharField(max_length=100, verbose_name="Nombre del departamento")
    departamento_pais = models.ForeignKey(
        Pais, on_delete=models.CASCADE, related_name='departamentos', verbose_name="País"
    )

    def __str__(self):
        return self.departamento_nombre

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "DEPARTAMENTOS"
