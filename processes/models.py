from django.db import models
from django.core.exceptions import ValidationError
from companies.models.process import Process

# === Constantes para tipos y estados ===
TIPOS_DOCUMENTO = [
    ('FC', 'Ficha de caracterización'),
    ('MA', 'Matriz'),
    ('PR', 'Procedimiento'),
    ('DI', 'Documento interno'),
    ('GU', 'Guía'),
    ('PT', 'Protocolo'),
    ('PL', 'Plan'),
    ('IN', 'Instructivo'),
    ('FR', 'Formato'),
    ('DE', 'Documento externo'),
    ('RG', 'Registro'),
]

ESTADOS = [
    ('VIG', 'Vigente'),
    ('OBS', 'Obsoleto'),
]

# === Validaciones ===
def validar_archivo_oficial(file):
    ext = file.name.lower().split('.')[-1]
    if ext not in ['doc', 'docx', 'pdf', 'xls', 'xlsx']:
        raise ValidationError("El archivo oficial debe ser PDF o Excel (.xls, .xlsx)")

def validar_archivo_editable(file):
    ext = file.name.lower().split('.')[-1]
    if ext not in ['doc', 'docx', 'xls', 'xlsx']:
        raise ValidationError("El archivo editable debe ser Word o Excel (.doc, .docx, .xls, .xlsx)")

def validar_version(value):
    """Validar que la versión sea >= 0"""
    if value < 0:
        raise ValidationError("La versión debe ser mayor o igual a 0.")

# === Modelo principal ===
class Documento(models.Model):
    documento_padre = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='versiones'
    )
    codigo_documento = models.CharField(max_length=50)
    nombre_documento = models.CharField(max_length=255)
    proceso = models.ForeignKey(Process, on_delete=models.PROTECT)
    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOCUMENTO)
    version = models.IntegerField(validators=[validar_version])
    estado = models.CharField(max_length=3, choices=ESTADOS, default='VIG')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    archivo_oficial = models.FileField(
        upload_to='documentos/oficiales/',
        validators=[validar_archivo_oficial],
        null=False,
        blank=False
    )
    archivo_editable = models.FileField(
        upload_to='documentos/editables/',
        validators=[validar_archivo_editable],
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('codigo_documento', 'version')
        indexes = [
            models.Index(fields=['codigo_documento']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.codigo_documento} v{self.version} - {self.nombre_documento}"

    def save(self, *args, **kwargs):
        """
        Override del método save para manejar automáticamente el estado de documentos padre
        """
        # Si es un documento nuevo (no tiene pk) y tiene documento_padre
        if not self.pk and self.documento_padre:
            # Marcar el documento padre como obsoleto
            self.documento_padre.estado = 'OBS'
            self.documento_padre.save(update_fields=['estado', 'fecha_actualizacion'])
            
            # Asegurar que el nuevo documento esté vigente
            self.estado = 'VIG'
            
            # Auto-incrementar la versión basada en el documento padre
            if not self.version:
                self.version = self.documento_padre.version + 1

        # Si es un documento nuevo sin padre, asegurar que esté vigente
        elif not self.pk and not self.documento_padre:
            self.estado = 'VIG'
            if not self.version:
                self.version = 0

        super().save(*args, **kwargs)

    def crear_nueva_version(self, **datos_actualizados):
        """
        Método helper para crear una nueva versión del documento
        """
        nueva_version = Documento(
            documento_padre=self,
            codigo_documento=self.codigo_documento,
            nombre_documento=datos_actualizados.get('nombre_documento', self.nombre_documento),
            proceso=datos_actualizados.get('proceso', self.proceso),
            tipo_documento=datos_actualizados.get('tipo_documento', self.tipo_documento),
            version=self.version + 1,
            estado='VIG',
            archivo_oficial=datos_actualizados.get('archivo_oficial'),
            archivo_editable=datos_actualizados.get('archivo_editable', self.archivo_editable),
        )
        nueva_version.save()
        return nueva_version

    def get_ultima_version(self):
        """
        Obtiene la última versión del documento
        """
        return self.versiones.order_by('-version').first()

    def get_version_vigente(self):
        """
        Obtiene la versión vigente del documento
        """
        return self.versiones.filter(estado='VIG').first()

    @classmethod
    def get_documentos_vigentes(cls):
        """
        Obtiene todos los documentos que están vigentes
        """
        return cls.objects.filter(estado='VIG', activo=True)

