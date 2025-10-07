from django.db import models

class EntidadAuditoria(models.Model):
    entidad_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la entidad")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auditoria_entidadauditoria"  
        verbose_name = "Entidad de auditoría"
        verbose_name_plural = "Entidad de auditoría"
