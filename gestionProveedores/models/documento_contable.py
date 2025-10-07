from django.db import models
class DocumentoContable(models.Model):
    doc_contable_id = models.AutoField(primary_key=True, verbose_name="ID")
    doc_contable_tipo = models.CharField(max_length=250, default="", verbose_name="Tipo")
    doc_contable_descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    doc_contable_estado=  models.BooleanField(default=True, verbose_name="Status")
    
    def __str__(self):
     return f"{self.doc_contable_tipo}: {self.doc_contable_descripcion}"
    class Meta:
        verbose_name = "Documento contable"
        verbose_name_plural = "DOCUMENTOS CONTABLES"