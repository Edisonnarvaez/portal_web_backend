from django.db import models
from .company import Company

class Department(models.Model):
    name = models.CharField(max_length=255)
    departmentCode = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='departments')
    description = models.TextField()
    status = models.BooleanField(default=True)  # Activo/Inactivo
    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)

    def __str__(self):
        return self.name