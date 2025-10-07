
from django.db import models
from .correo import Correo
class ArchivoAdjunto(models.Model):
    correo = models.ForeignKey(Correo, on_delete=models.CASCADE, related_name='adjuntos')
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='adjuntos/')
