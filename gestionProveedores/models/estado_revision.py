from django.db import models

class EstadoRevision(models.Model):
    estado_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del estado")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "gestionProveedores_estadorevision" 
        verbose_name = "Estado de revisión"
        verbose_name_plural = "Estados de revisión"
