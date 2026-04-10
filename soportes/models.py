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

    # ✅ NIVEL (TEMPORAL NULLABLE PARA MIGRACIÓN)
    nivel_aplica = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        null=True,
        blank=True,
        help_text='Nivel al que aplica este tipo de documento'
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

    # ✅ PRESTADOR - SIEMPRE REQUERIDO (base de toda la jerarquía)
    prestador = models.ForeignKey(
        'habilitacion.DatosPrestador',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='soportes_documentales',
        help_text='Prestador propietario de este documento soporte (REQUERIDO)'
    )

    nivel = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        help_text='Nivel del documento: EMPRESA, SEDE o SERVICIO'
    )

    # ✅ EMPRESA - SIEMPRE REQUERIDO (base jerárquica)
    empresa = models.ForeignKey(
        'companies.Company',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='soportes_documentales',
        help_text='Empresa matriz del documento (REQUERIDO)'
    )
    # ✅ SEDE - Requerido solo si nivel >= SEDE
    sede = models.ForeignKey(
        'companies.Headquarters',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='soportes_documentales',
        help_text='Sede física (requerido para nivel SEDE o SERVICIO)'
    )
    
    # ✅ SERVICIO - Requerido solo si nivel = SERVICIO
    servicio = models.ForeignKey(
        'habilitacion.ServicioSede',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='soportes_documentales',
        help_text='Servicio específico (requerido solo para nivel SERVICIO)'
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
        # ✅ ÍNDICES PARA FILTRADO CASCADA
        indexes = [
            models.Index(fields=['prestador', 'nivel', 'es_vigente']),
            models.Index(fields=['empresa', 'nivel', 'es_vigente']),
            models.Index(fields=['sede', 'es_vigente']),
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

        # ✅ VALIDACIONES BÁSICAS (siempre requeridas)
        if not self.prestador_id:
            raise ValidationError({'prestador': 'Debe seleccionar prestador.'})
        if not self.empresa_id:
            raise ValidationError({'empresa': 'Debe seleccionar empresa.'})
        if not self.nivel:
            raise ValidationError({'nivel': 'Debe seleccionar nivel.'})
        if not self.tipo_documento_id:
            raise ValidationError({'tipo_documento': 'Debe seleccionar tipo de documento.'})

        # ✅ VALIDAR TIPO DE DOCUMENTO APLICA A ESTE NIVEL
        if self.tipo_documento.nivel_aplica != self.nivel:
            raise ValidationError(
                f'Este tipo de documento aplica a nivel {self.tipo_documento.nivel_aplica}, no {self.nivel}.'
            )

        # ✅ VALIDACIONES POR NIVEL
        if self.nivel == 'EMPRESA':
            # EMPRESA: Solo empresa_id requerido
            if self.sede_id or self.servicio_id:
                raise ValidationError(
                    'Para nivel EMPRESA, no debe especificar sede ni servicio.'
                )

        elif self.nivel == 'SEDE':
            # SEDE: Empresa + Sede requeridos
            if not self.sede_id:
                raise ValidationError({'sede': 'Debe seleccionar sede para nivel SEDE.'})
            if self.servicio_id:
                raise ValidationError('Para nivel SEDE, no debe especificar servicio.')
            
            # ✅ VALIDAR CASCADA: Sede debe pertenece a Empresa
            sede = self.sede
            if sede.company_id != self.empresa_id:
                raise ValidationError(
                    {'sede': f'La sede seleccionada no pertenece a la empresa {self.empresa.name}.'}
                )

        elif self.nivel == 'SERVICIO':
            # SERVICIO: Empresa + Sede + Servicio requeridos
            if not self.sede_id:
                raise ValidationError({'sede': 'Debe seleccionar sede para nivel SERVICIO.'})
            if not self.servicio_id:
                raise ValidationError({'servicio': 'Debe seleccionar servicio para nivel SERVICIO.'})
            
            # ✅ VALIDAR CASCADA: Sede pertenece a Empresa
            sede = self.sede
            if sede.company_id != self.empresa_id:
                raise ValidationError(
                    {'sede': f'La sede no pertenece a la empresa {self.empresa.name}.'}
                )
            
            # ✅ VALIDAR CASCADA: Servicio pertenece a Prestador
            servicio = self.servicio
            if servicio.prestador_id != self.prestador_id:
                raise ValidationError(
                    {'servicio': f'El servicio no pertenece al prestador {self.prestador.nombre_prestador}.'}
                )
            
            # ✅ VALIDAR CASCADA: Prestador pertenece a Sede
            prestador = self.prestador
            if prestador.headquarters_id != self.sede_id:
                raise ValidationError(
                    {'sede': f'El prestador está registrado en otra sede, no en {sede.name}.'}
                )

        # ✅ VALIDACIÓN DE VENCIMIENTO
        if self.tipo_documento.requiere_vencimiento and not self.fecha_vencimiento:
            raise ValidationError(
                {'fecha_vencimiento': 'Este documento requiere fecha de vencimiento.'}
            )

    # ==============================
    # FILTRO DE CONTEXTO
    # ==============================
    def _scope_filter(self):
        """Filtra documentos previos del mismo tipo para versionamiento."""
        base_q = Q(
            prestador_id=self.prestador_id,
            tipo_documento_id=self.tipo_documento_id,
            nivel=self.nivel
        )

        if self.nivel == 'EMPRESA':
            return base_q & Q(empresa_id=self.empresa_id)

        if self.nivel == 'SEDE':
            return base_q & Q(empresa_id=self.empresa_id, sede_id=self.sede_id)

        return base_q & Q(empresa_id=self.empresa_id, sede_id=self.sede_id, servicio_id=self.servicio_id)

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

    # ✅ PRESTADOR (NUEVO) - Temporal nullable para migración
    prestador = models.ForeignKey(
        'habilitacion.DatosPrestador',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='soportes_requeridos',
        help_text='Prestador al cual se requiere este documento'
    )

    empresa = models.ForeignKey('companies.Company', null=True, blank=True, on_delete=models.CASCADE)
    sede = models.ForeignKey('companies.Headquarters', null=True, blank=True, on_delete=models.CASCADE)
    servicio = models.ForeignKey('habilitacion.ServicioSede', null=True, blank=True, on_delete=models.CASCADE)

    tipo_documento = models.ForeignKey(TipoDocumentoSoporte, on_delete=models.CASCADE)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    class Meta:
        db_table = 'soportes_soporterequerido'
        # ✅ INCLUIR PRESTADOR EN UNIQUE CONSTRAINT
        unique_together = ('prestador', 'empresa', 'sede', 'servicio', 'tipo_documento')

    def __str__(self):
        return f'{self.tipo_documento.nombre} - {self.estado}'