from django.db import models

class EstadoPendienteRContable(models.Model):
    estado_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del estado")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "gestionProveedores_estadopendientercontable"
        verbose_name = "Estado de pendiente reconocimiento contable"
        verbose_name_plural = "Estados de pendientes de reconocimientos contables"
