from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q, Max


# ==============================
# CATEGORÍA DE SOPORTE
# ==============================
class CategoriaSoporte(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'soportes_categoriasoporte'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==============================
# TIPO DE DOCUMENTO SOPORTE
# ==============================
class TipoDocumentoSoporte(models.Model):

    NIVEL_EMPRESA = 'EMPRESA'
    NIVEL_SEDE = 'SEDE'
    NIVEL_SERVICIO = 'SERVICIO'

    NIVEL_CHOICES = [
        (NIVEL_EMPRESA, 'Empresa'),
        (NIVEL_SEDE, 'Sede'),
        (NIVEL_SERVICIO, 'Servicio'),
    ]

    categoria = models.ForeignKey(
        CategoriaSoporte,
        on_delete=models.PROTECT,
        related_name='tipos_documento',
    )

    nombre = models.CharField(max_length=120)

    # 🔥 NIVEL PRO
    nivel_aplica = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        null=True,      # 🔥 TEMPORAL
        blank=True      # 🔥 TEMPORAL
    )

    es_obligatorio = models.BooleanField(default=True)
    requiere_vencimiento = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'soportes_tipodocumentosoporte'
        unique_together = ('categoria', 'nombre')
        ordering = ['categoria__nombre', 'nombre']

    def __str__(self):
        return f'{self.categoria.nombre} - {self.nombre}'


# ==============================
# SOPORTE DOCUMENTAL (ARCHIVO)
# ==============================
class SoporteDocumental(models.Model):

    NIVEL_CHOICES = TipoDocumentoSoporte.NIVEL_CHOICES

    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES)

    empresa = models.ForeignKey(
        'companies.Company',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='soportes_documentales',
    )
    sede = models.ForeignKey(
        'companies.Headquarters',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='soportes_documentales',
    )
    servicio = models.ForeignKey(
        'habilitacion.ServicioSede',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='soportes_documentales',
    )

    tipo_documento = models.ForeignKey(
        TipoDocumentoSoporte,
        on_delete=models.PROTECT,
        related_name='soportes',
    )

    archivo = models.FileField(upload_to='habilitacion/soportes/')

    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

    version = models.PositiveIntegerField(default=1)
    es_vigente = models.BooleanField(default=True)

    fecha_carga = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'soportes_soportedocumental'
        ordering = ['-fecha_carga']
        indexes = [
            models.Index(fields=['nivel', 'es_vigente']),
            models.Index(fields=['tipo_documento', 'es_vigente']),
            models.Index(fields=['fecha_vencimiento']),
        ]

    def __str__(self):
        objetivo = self.empresa_id or self.sede_id or self.servicio_id
        return f'{self.tipo_documento.nombre} - {self.nivel} #{objetivo} v{self.version}'

    # ==============================
    # VALIDACIONES
    # ==============================
    def clean(self):
        super().clean()

        relaciones = [self.empresa_id, self.sede_id, self.servicio_id]
        relaciones_set = sum(1 for rel in relaciones if rel)

        if relaciones_set != 1:
            raise ValidationError(
                'Debe asociar exactamente una relación: empresa, sede o servicio.'
            )

        if self.nivel == 'EMPRESA' and not self.empresa_id:
            raise ValidationError({'empresa': 'Debe seleccionar empresa.'})

        if self.nivel == 'SEDE' and not self.sede_id:
            raise ValidationError({'sede': 'Debe seleccionar sede.'})

        if self.nivel == 'SERVICIO' and not self.servicio_id:
            raise ValidationError({'servicio': 'Debe seleccionar servicio.'})

        # 🔥 VALIDACIÓN PRO
        if self.tipo_documento.nivel_aplica != self.nivel:
            raise ValidationError(
                f'Este tipo de documento aplica a nivel {self.tipo_documento.nivel_aplica}'
            )

        # 🔥 VALIDACIÓN DE VENCIMIENTO
        if self.tipo_documento.requiere_vencimiento and not self.fecha_vencimiento:
            raise ValidationError(
                {'fecha_vencimiento': 'Este documento requiere fecha de vencimiento.'}
            )

    # ==============================
    # FILTRO DE CONTEXTO
    # ==============================
    def _scope_filter(self):
        if self.nivel == 'EMPRESA':
            return Q(nivel='EMPRESA', empresa_id=self.empresa_id)

        if self.nivel == 'SEDE':
            return Q(nivel='SEDE', sede_id=self.sede_id)

        return Q(nivel='SERVICIO', servicio_id=self.servicio_id)

    # ==============================
    # VERSIONAMIENTO AUTOMÁTICO
    # ==============================
    def save(self, *args, **kwargs):
        self.full_clean()

        with transaction.atomic():

            scope_q = self._scope_filter() & Q(tipo_documento_id=self.tipo_documento_id)

            existing = SoporteDocumental.objects.select_for_update().filter(scope_q)

            if self._state.adding:
                max_version = existing.aggregate(max_v=Max('version')).get('max_v') or 0
                self.version = max_version + 1

                if self.es_vigente:
                    existing.filter(es_vigente=True).update(es_vigente=False)

            else:
                if self.es_vigente:
                    existing.exclude(pk=self.pk).filter(es_vigente=True).update(es_vigente=False)

            super().save(*args, **kwargs)


# ==============================
# CHECKLIST AUTOMÁTICO
# ==============================
class SoporteRequerido(models.Model):

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CARGADO', 'Cargado'),
        ('VENCIDO', 'Vencido'),
    ]

    empresa = models.ForeignKey('companies.Company', null=True, blank=True, on_delete=models.CASCADE)
    sede = models.ForeignKey('companies.Headquarters', null=True, blank=True, on_delete=models.CASCADE)
    servicio = models.ForeignKey('habilitacion.ServicioSede', null=True, blank=True, on_delete=models.CASCADE)

    tipo_documento = models.ForeignKey(TipoDocumentoSoporte, on_delete=models.CASCADE)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    class Meta:
        db_table = 'soportes_soporterequerido'
        unique_together = ('empresa', 'sede', 'servicio', 'tipo_documento')

    def __str__(self):
        return f'{self.tipo_documento.nombre} - {self.estado}'