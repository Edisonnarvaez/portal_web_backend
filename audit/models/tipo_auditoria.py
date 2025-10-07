from django.db import models

class TipoAuditoria(models.Model):
    tipo_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del tipo de auditoría")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "auditoria_tipoauditoria"  
        verbose_name = "Tipo de auditoría"
        verbose_name_plural = "Tipos de auditoría"
