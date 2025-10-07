from django.db import models

class EstadoFactura(models.Model):
    estado_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del estado")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "gestionProveedores_estadofactura" 
        verbose_name = "Estado de factura"
        verbose_name_plural = "Estados de facturas"
