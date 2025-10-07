from django.db import models
from companies.models.process import Process
from users.models import User

class Indicator(models.Model):
    FREQUENCY_CHOICES = [
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('annual', 'Anual'),
    ]

    CALCULATION_CHOICES = [
        ('percentage', 'Porcentaje'),
        ('rate_per_1000', 'Tasa por 1000'),
        ('rate_per_10000', 'Tasa por 10000'),
        ('average', 'Promedio'),
        ('ratio', 'Razón'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    code = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    calculationMethod = models.CharField(max_length=50, choices=CALCULATION_CHOICES)  # Define el método de cálculo
    measurementUnit = models.CharField(max_length=255)
    numerator = models.TextField()
    numeratorResponsible = models.CharField(max_length=255)
    numeratorSource = models.CharField(max_length=255)
    numeratorDescription = models.TextField()
    denominator = models.TextField()
    denominatorResponsible = models.CharField(max_length=255)
    denominatorSource = models.CharField(max_length=255)
    denominatorDescription = models.TextField()
    trend = models.CharField(max_length=50, choices=[('increasing', 'Creciente'), ('decreasing', 'Decreciente')]) #, ('stable', 'Estable')
    target = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    process = models.ForeignKey(Process, on_delete=models.PROTECT)
    measurementFrequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)  # Periodicidad del indicador
    status = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

