from django.db import models
from django.conf import settings  

class SedeAuditada(models.Model):
    nombre_sede = models.CharField(max_length=150, verbose_name="Nombre de la sede")
    direccion = models.CharField(max_length=255, verbose_name="Dirección de la sede")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    pais = models.CharField(max_length=100, default="Colombia", verbose_name="País")
    fecha_auditoria = models.DateField(verbose_name="Fecha de auditoría")
    auditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Auditor")  # ✅ CORREGIDO
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    def __str__(self):
        return f"{self.nombre_sede} - {self.fecha_auditoria}"

    class Meta:
        db_table = "audit_sedeauditada"
        verbose_name = "Sede auditada"
        verbose_name_plural = "Sedes auditadas"   
