from django.db import models
from companies.models.headquarters import Headquarters
from .indicator import Indicator
from users.models import User

class Result(models.Model):
    headquarters = models.ForeignKey(Headquarters, on_delete=models.PROTECT)
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    numerator = models.FloatField()
    denominator = models.FloatField()
    calculatedValue = models.FloatField(null=True, blank=True)

    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)

    year = models.PositiveIntegerField()

    month = models.PositiveIntegerField(null=True, blank=True)  # Solo para frecuencia mensual
    quarter = models.PositiveIntegerField(null=True, blank=True)  # Solo para frecuencia trimestral
    semester = models.PositiveIntegerField(null=True, blank=True)  # Solo para frecuencia semestral

    def calculate_indicator(self):
        calculation_type = self.indicator.calculationMethod.lower()

        if self.denominator == 0:
            self.calculatedValue = 0  # Evitar la división por cero
        else:
            # Cálculo según el método definido en el indicador
            if calculation_type == 'percentage':
                self.calculatedValue = self._calculate_percentage()
            elif calculation_type == 'rate_per_1000':
                self.calculatedValue = self._calculate_rate_per_1000()
            elif calculation_type == 'rate_per_10000':
                self.calculatedValue = self._calculate_rate_per_10000()
            elif calculation_type == 'average':
                self.calculatedValue = self._calculate_average()
            elif calculation_type == 'ratio':
                self.calculatedValue = self._calculate_ratio()
            else:
                self.calculatedValue = self._default_calculation()  # Si no coincide con ninguno, usa cálculo por defecto

        self.save()

    # Cálculos específicos según el tipo
    def _calculate_percentage(self):
        return (self.numerator / self.denominator) * 100

    def _calculate_rate_per_1000(self):
        return (self.numerator / self.denominator) * 1000

    def _calculate_rate_per_10000(self):
        return (self.numerator / self.denominator) * 10000

    def _calculate_average(self):
        return self.numerator / self.denominator

    def _calculate_ratio(self):
        return self.numerator / self.denominator

    def _default_calculation(self):
        return self.numerator / self.denominator  # Cálculo básico por defecto
