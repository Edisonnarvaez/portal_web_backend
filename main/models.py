from django.db import models
from companies.models.headquarters import Headquarters

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Funcionario(TimeStampedModel):
    documento = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    cargo = models.CharField(max_length=100)
    sede = models.ForeignKey(Headquarters, on_delete=models.PROTECT, related_name='sede_funcionarios')
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)
    foto = models.ImageField(upload_to='fotosFuncionarios/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class ContenidoInformativo(TimeStampedModel):
    TIPO_CHOICES = (
        ('noticia', 'Noticia'),
        ('comunicado', 'Comunicado'),
    )
    titulo = models.CharField(max_length=200)
    fecha = models.DateField()
    contenido = models.TextField()
    enlace = models.URLField(blank=True, null=True)
    urgente = models.BooleanField(default=False)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    imagen = models.ImageField(upload_to='imagenContenidoInformativo/', null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} - {self.tipo}"

class Evento(TimeStampedModel):
    titulo = models.CharField(max_length=200)
    fecha = models.DateField()
    hora = models.TimeField()
    detalles = models.TextField()
    es_virtual = models.BooleanField(default=False)
    enlace = models.URLField(blank=True, null=True)
    lugar = models.CharField(max_length=255, blank=True, null=True)
    importante = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

class FelicitacionCumpleanios(TimeStampedModel):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    mensaje = models.TextField()

    def __str__(self):
        return f"Feliz cumpleaños {self.funcionario.nombres}!"
    
class Reconocimiento(TimeStampedModel):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="reconocimientos")
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateField()
    tipo = models.CharField(max_length=100, blank=True, null=True)
    publicar = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titulo} - {self.funcionario.nombres} {self.funcionario.apellidos}"

