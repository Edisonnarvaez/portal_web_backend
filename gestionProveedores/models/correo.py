
from django.db import models
# models.py
class Correo(models.Model):
    subject = models.CharField(max_length=255)
    from_email = models.EmailField()
    date_received = models.DateTimeField()
    raw_message = models.TextField()
    uid = models.BigIntegerField(unique=True, null=True, blank=True)  # <--- NUEVO
    archivos = models.TextField(blank=True, null=True)
