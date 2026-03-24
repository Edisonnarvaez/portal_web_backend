from django.db import models

class Region(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    
class Municipality(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='Departamento')
    def __str__(self):
        return f"{self.name} ({self.code})"

