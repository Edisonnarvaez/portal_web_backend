from django.db import models
from .terceros_paises import Pais
from .terceros_departamentos import Departamento
from .terceros_municipios import Municipio
from .tipo_tercero import TipoTercero



class Terceros(models.Model):
    TIPO_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('RC', 'Registro Civil'),
        ('NIT', 'Número de Identificación Tributaria'),
        ('OTRO', 'Otro'),
    ]
    #TIPO_TERCERO = [
    #    ('Natural', 'Persona Natural'),
    #    ('Juridica', 'Persona Jurídica'),
    #]
    tercero_id = models.AutoField(primary_key=True, verbose_name="ID Tercero")
    tercero_tipo_documento = models.CharField(max_length=50, choices=TIPO_DOCUMENTO)
    tercero_codigo = models.CharField(max_length=50, verbose_name="Código", null=True, blank=True)
    tercero_nombre_completo = models.CharField(max_length=200, verbose_name="Nombre completo", null=True, blank=True)
    tercero_razon_social = models.CharField(max_length=150, blank=True, null=True, verbose_name="Razón social")
    tercero_fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de nacimiento")
    tercero_direccion = models.CharField(max_length=150, blank=True, null=True, verbose_name="Dirección")
    tercero_telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    tercero_email = models.EmailField(blank=True, null=True, verbose_name="Correo electrónico")

    tercero_pais = models.ForeignKey(
        Pais, on_delete=models.PROTECT, related_name='terceros_pais', verbose_name="País", blank=True, null=True
    )
    tercero_departamento = models.ForeignKey(
        Departamento, on_delete=models.PROTECT, related_name='terceros_departamento', verbose_name="Departamento", blank=True, null=True
    )
    tercero_municipio = models.ForeignKey(
        Municipio, on_delete=models.PROTECT, related_name='terceros_municipio', verbose_name="Municipio", blank=True, null=True
    )

    tercero_obligado_facturar = models.BooleanField(default=False, verbose_name="Obligado a facturar", null=True)
    tercero_proveedor = models.BooleanField(default=False, verbose_name="Proveedor", null=True)
    tercero_tipo = models.ForeignKey(
        TipoTercero,
        on_delete=models.PROTECT,
        verbose_name="Tipo de tercero",
        blank=True, null=True
    )
    tercero_estado = models.BooleanField(default=True, verbose_name="Estado", null=True)

    def __str__(self):
        return self.tercero_nombre_completo or "Tercero sin nombre"


    class Meta:
        verbose_name = "Tercero"
        verbose_name_plural = "Terceros"
