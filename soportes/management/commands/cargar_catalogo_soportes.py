from django.core.management.base import BaseCommand
from django.db import transaction

from soportes.models import CategoriaSoporte, TipoDocumentoSoporte


class Command(BaseCommand):
    help = 'Carga el catálogo inicial de soportes documentales (Resolución 3100)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando carga de catálogo...'))

        with transaction.atomic():

            catalogo = [
                {
                    "categoria": "Infraestructura",
                    "tipos": [
                        {"nombre": "Certificado uso de suelo", "nivel": "SEDE", "requiere_vencimiento": False},
                        {"nombre": "Licencia de construcción", "nivel": "SEDE", "requiere_vencimiento": False},
                        {"nombre": "Certificado RETIE", "nivel": "SEDE", "requiere_vencimiento": True},
                        {"nombre": "Planos arquitectónicos", "nivel": "SEDE", "requiere_vencimiento": False},
                    ]
                },
                {
                    "categoria": "Condiciones locativas",
                    "tipos": [
                        {"nombre": "Concepto sanitario", "nivel": "SEDE", "requiere_vencimiento": True},
                        {"nombre": "Certificado de fumigación", "nivel": "SEDE", "requiere_vencimiento": True},
                        {"nombre": "Plan de mantenimiento locativo", "nivel": "SEDE", "requiere_vencimiento": True},
                    ]
                },
                {
                    "categoria": "Gestión ambiental",
                    "tipos": [
                        {"nombre": "PGIRASA", "nivel": "SEDE", "requiere_vencimiento": True},
                        {"nombre": "Contrato recolección residuos", "nivel": "SEDE", "requiere_vencimiento": True},
                        {"nombre": "Actas de recolección", "nivel": "SEDE", "requiere_vencimiento": True},
                    ]
                },
                {
                    "categoria": "Seguridad del paciente",
                    "tipos": [
                        {"nombre": "Plan de emergencias", "nivel": "SEDE", "requiere_vencimiento": True},
                        {"nombre": "Actas de simulacros", "nivel": "SEDE", "requiere_vencimiento": True},
                        {"nombre": "Listado brigadas emergencia", "nivel": "SEDE", "requiere_vencimiento": True},
                    ]
                },
                {
                    "categoria": "Talento humano",
                    "tipos": [
                        {"nombre": "Tarjeta profesional", "nivel": "SERVICIO", "requiere_vencimiento": False},
                        {"nombre": "Certificado RETHUS", "nivel": "SERVICIO", "requiere_vencimiento": True},
                        {"nombre": "Certificados académicos", "nivel": "SERVICIO", "requiere_vencimiento": False},
                    ]
                },
                {
                    "categoria": "Legal",
                    "tipos": [
                        {"nombre": "Cámara de comercio", "nivel": "EMPRESA", "requiere_vencimiento": True},
                        {"nombre": "RUT", "nivel": "EMPRESA", "requiere_vencimiento": False},
                        {"nombre": "Póliza responsabilidad civil", "nivel": "EMPRESA", "requiere_vencimiento": True},
                    ]
                },
                {
                    "categoria": "Dotación biomédica",
                    "tipos": [
                        {"nombre": "Inventario equipos biomédicos", "nivel": "SERVICIO", "requiere_vencimiento": True},
                        {"nombre": "Registros mantenimiento equipos", "nivel": "SERVICIO", "requiere_vencimiento": True},
                        {"nombre": "Certificados calibración", "nivel": "SERVICIO", "requiere_vencimiento": True},
                    ]
                },
            ]

            niveles_validos = dict(TipoDocumentoSoporte.NIVEL_CHOICES).keys()

            for item in catalogo:
                categoria_obj, _ = CategoriaSoporte.objects.get_or_create(
                    nombre=item["categoria"],
                    defaults={
                        "descripcion": item["categoria"],
                        "activo": True
                    }
                )

                for tipo in item["tipos"]:

                    # 🔒 VALIDACIÓN DE NIVEL
                    if tipo["nivel"] not in niveles_validos:
                        raise ValueError(f'Nivel inválido: {tipo["nivel"]} en {tipo["nombre"]}')

                    obj, created = TipoDocumentoSoporte.objects.get_or_create(
                        categoria=categoria_obj,
                        nombre=tipo["nombre"],
                        defaults={
                            "nivel_aplica": tipo["nivel"],
                            "es_obligatorio": True,
                            "requiere_vencimiento": tipo["requiere_vencimiento"],
                            "activo": True
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'✔ Creado: {obj}'))
                    else:
                        # 🔥 ACTUALIZA SI YA EXISTE
                        cambios = False

                        if obj.nivel_aplica != tipo["nivel"]:
                            obj.nivel_aplica = tipo["nivel"]
                            cambios = True

                        if obj.requiere_vencimiento != tipo["requiere_vencimiento"]:
                            obj.requiere_vencimiento = tipo["requiere_vencimiento"]
                            cambios = True

                        if not obj.es_obligatorio:
                            obj.es_obligatorio = True
                            cambios = True

                        if not obj.activo:
                            obj.activo = True
                            cambios = True

                        if cambios:
                            obj.save()
                            self.stdout.write(self.style.WARNING(f'↺ Actualizado: {obj}'))
                        else:
                            self.stdout.write(f'-- Sin cambios: {obj}')

        self.stdout.write(self.style.SUCCESS('✅ Catálogo cargado correctamente'))