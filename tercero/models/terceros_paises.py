from django.db import models

class Pais(models.Model):
    pais_id = models.AutoField(primary_key=True, verbose_name="ID País")
    pais_codigo = models.CharField(max_length=100, verbose_name="codigo del país")
    pais_nombre = models.CharField(max_length=100, verbose_name="Nombre del país")

    def __str__(self):
        return self.pais_nombre

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "PAÍSES"