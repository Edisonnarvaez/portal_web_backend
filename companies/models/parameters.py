from django.db import models


class Region(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Región"
        verbose_name_plural = "Regiones"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Municipality(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, related_name="municipalities"
    )

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ["name"]
        unique_together = [["region", "code"]]

    def __str__(self):
        return f"{self.name} ({self.code})"

