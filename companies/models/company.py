from django.db import models
from django.core.exceptions import ValidationError

from .parameters import Region, Municipality

class Company(models.Model):
    CLASS_HEALTHCARE_ENTITY_CHOICES = [
        ('IPS', 'Institución Prestadora de Servicios'),
        ('PROF', 'Profesional de Salud'),
        ('PH', 'Persona Humana'),
        ('PJ', 'Persona Jurídica'),
    ]
    TYPE_DOCUMENT_CHOICES = [
        ('NIT', 'Número de Identificación Tributaria'),
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('PPT', 'Permiso de Permanencia Temporal')
    ]
    TYPE_LEGAL_NATURE_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('PRIVADA', 'Privada'),
        ('MIXTA', 'Mixta')
    ]
    name = models.CharField(max_length=255)
    type_document = models.CharField(max_length=50,choices=TYPE_DOCUMENT_CHOICES,verbose_name="Tipo de Documento")
    number_document = models.CharField(max_length=50)
    digit_verification = models.CharField(max_length=10, blank=True, null=True)
    legal_nature = models.CharField(max_length=255,choices=TYPE_LEGAL_NATURE_CHOICES,verbose_name="Naturaleza Legal")
    
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='companies')
    municipality = models.ForeignKey(Municipality, on_delete=models.PROTECT, related_name='companies')
    
    code_authorize = models.CharField(max_length=50, blank=True, null=True)
    class_healthcare_entity = models.CharField(max_length=10,choices=CLASS_HEALTHCARE_ENTITY_CHOICES,verbose_name="Clase de Entidad de Salud")
    company_social_state = models.BooleanField(default=False)
    type_document_legal_representative = models.CharField(max_length=50,choices=TYPE_DOCUMENT_CHOICES,verbose_name="Tipo de Documento del Representante Legal")
    number_document_legal_representative = models.CharField(max_length=50,verbose_name="Número de Documento del Representante Legal")
    name_legal_representative = models.CharField(max_length=255)
    # se cambio el nombre del legal_representative por el nombre completo del representante legal para evitar confusiones
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    contactEmail = models.EmailField()
    #cargue de soporte de documento del representante legal----------------------
    documento_representante_legal = models.FileField(
        upload_to='empresas/representantes_legales/',
        null=True, blank=True,
        help_text="Documento del representante legal"
    )

    foundationDate = models.DateField()
    status = models.BooleanField(default=True)  # Activo/Inactivo
    #date_autoevaluation = models.DateField(blank=True, null=True) # para que la entidad tenga el estado de activo  debe tener una autoevalucion vigente, por eso se agrega este campo para controlar la fecha de la última autoevaluación realizada por la entidad
    creationDate = models.DateField(auto_now_add=True)
    updateDate = models.DateField(auto_now=True)

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
        return self.name
