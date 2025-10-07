from django.db import models

from .company import Company

class Headquarters(models.Model):
    habilitationCode = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    departament = models.CharField(max_length=100,null=True)
    city = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=100,null=True)
    habilitationDate = models.DateField(null=True)
    closingDate = models.DateField(null=True)
    status = models.BooleanField(default=True)  # Activo/Inactivo
    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)

    def __str__(self):
        return self.name