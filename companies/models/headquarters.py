from django.db import models
from django.core.exceptions import ValidationError
from .company import Company, Region, Municipality

class Headquarters(models.Model):
    #habilitationCode = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    municipality = models.ForeignKey(Municipality, on_delete=models.PROTECT)
    address = models.CharField(max_length=100,null=True)

    concepto_sanitario = models.BooleanField(
        default=False, 
        help_text="Concepto sanitario vigente expedido por la autoridad competente"
    )
    reserva_agua_24h = models.BooleanField(
        default=False, 
        help_text="Obligatorio para servicios de urgencias e internación"
    )
    planta_electrica = models.BooleanField(
        default=False, 
        help_text="Fuente de energía de emergencia exigible para todos los servicios"
    )

    # Configuración de Sede (Res. 544/2023)
    es_domicilio_ong = models.BooleanField(
        default=False, 
        verbose_name="Sede es Domicilio (Cooperación/ONG)",
        help_text="Habilita el uso de domicilio como sede para organismos internacionales o ONGs"
    )

    status = models.BooleanField(default=True)  # Activo/Inactivo
    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = "Sede Física"
        verbose_name_plural = "Sedes Físicas"

    def clean(self):
        super().clean()
        if self.region_id and self.municipality_id and self.municipality.region_id != self.region_id:
            raise ValidationError(
                {'municipality': 'El municipio seleccionado no pertenece a la region elegida.'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.municipality.name}"