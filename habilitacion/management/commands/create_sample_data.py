"""
Django management command para crear datos de ejemplo
"""
from django.core.management.base import BaseCommand
from datetime import date, timedelta
from random import choice
from habilitacion.models import (
    DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento
)
from normativity.models import Criterio
from companies.models import Company, Headquarters


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para autoevaluaciones y cumplimientos'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write("  CREAR DATOS DE EJEMPLO")
        self.stdout.write("="*80 + "\n")

        # 1. Crear Company
        try:
            company = Company.objects.create(
                name="Clínica Integral de Salud",
                nit="9009876543",
                legalRepresentative="Dr. Carlos González",
                phone="+57 1 5551234",
                address="Cra 5 # 32-45, Bogotá",
                contactEmail="info@clinicaintegral.com",
                foundationDate=date(2010, 3, 15),
                status=True
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Company creada: {company.name}'))
        except Exception as e:
            company = Company.objects.get(nit="9009876543")
            self.stdout.write(self.style.WARNING(f'⚠️  Company ya existe: {company.name}'))

        # 2. Crear Headquarters
        try:
            headquarters = Headquarters.objects.create(
                company=company,
                habilitationCode="SEDE-PRINCIPAL-001",
                name="Sede Principal",
                departament="Bogotá",
                city="Bogotá",
                address="Cra 5 # 32-45",
                habilitationDate=date(2020, 1, 15),
                status=True
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Headquarters creada: {headquarters.name}'))
        except Exception as e:
            headquarters = Headquarters.objects.get(habilitationCode="SEDE-PRINCIPAL-001")
            self.stdout.write(self.style.WARNING(f'⚠️  Headquarters ya existe: {headquarters.name}'))

        # 3. Crear DatosPrestador
        try:
            datos_prestador = DatosPrestador.objects.create(
                headquarters=headquarters,
                codigo_reps="9009876543-001",
                clase_prestador="IPS",
                estado_habilitacion="HABILITADA",
                fecha_inscripcion=date(2020, 1, 15),
                fecha_renovacion=date(2024, 1, 15),
                fecha_vencimiento_habilitacion=date(2025, 12, 31),
                aseguradora_pep="Seguros La Confianza",
                numero_poliza="POL-2024-001234",
                vigencia_poliza=date(2025, 12, 31)
            )
            self.stdout.write(self.style.SUCCESS(f'✅ DatosPrestador creado: {datos_prestador.codigo_reps}'))
        except Exception as e:
            datos_prestador = DatosPrestador.objects.get(codigo_reps="9009876543-001")
            self.stdout.write(self.style.WARNING(f'⚠️  DatosPrestador ya existe: {datos_prestador.codigo_reps}'))

        # 4. Crear ServicioSede
        servicios_lista = [
            ("URGENCIAS", "Urgencias", "Servicio de emergencias 24/7"),
            ("LABORATORIO", "Laboratorio", "Análisis clínicos y diagnóstico"),
            ("IMAGENOLOGIA", "Imagenología", "Radiología, ecografía, tomografía")
        ]

        servicios_creados = []
        for codigo, nombre, descripcion in servicios_lista:
            try:
                servicio = ServicioSede.objects.create(
                    sede=headquarters,
                    codigo_servicio=codigo,
                    nombre_servicio=nombre,
                    descripcion=descripcion,
                    modalidad="INTRAMURAL",
                    complejidad="ALTA",
                    estado_habilitacion="HABILITADO"
                )
                servicios_creados.append(servicio)
                self.stdout.write(f"  ✅ Servicio: {servicio.nombre_servicio}")
            except Exception as e:
                try:
                    servicio = ServicioSede.objects.get(codigo_servicio=codigo, sede=headquarters)
                    servicios_creados.append(servicio)
                    self.stdout.write(f"  ⚠️  Servicio ya existe: {servicio.nombre_servicio}")
                except:
                    self.stdout.write(f"  ❌ Error en servicio {codigo}: {str(e)[:50]}")

        self.stdout.write(f"\nTotal servicios: {len(servicios_creados)}")

        # 5. Crear Autoevaluación
        try:
            autoevaluacion = Autoevaluacion.objects.create(
                datos_prestador=datos_prestador,
                periodo=2024,
                version=1,
                fecha_vencimiento=date(2024, 12, 31),
                estado='EN_CURSO'
            )
            self.stdout.write(self.style.SUCCESS(f'\n✅ Autoevaluación creada: {autoevaluacion.numero_autoevaluacion}'))
        except Exception as e:
            autoevaluaciones = Autoevaluacion.objects.filter(
                datos_prestador=datos_prestador,
                periodo=2024,
                version=1
            )
            if autoevaluaciones.exists():
                autoevaluacion = autoevaluaciones.first()
                self.stdout.write(self.style.WARNING(f'\n⚠️  Autoevaluación ya existe: {autoevaluacion.numero_autoevaluacion}'))
            else:
                self.stdout.write(self.style.ERROR(f'\n❌ Error creando autoevaluación: {e}'))
                raise

        # 6. Crear Cumplimientos
        criterios = Criterio.objects.all()
        if not criterios.exists():
            self.stdout.write(self.style.WARNING(
                "\n⚠️  No hay criterios en la base de datos.\n"
                "   Ejecuta primero: python manage.py cargar_estandares"
            ))
        else:
            cumplimientos_creados = 0
            resultados = ['CUMPLE', 'NO_CUMPLE', 'PARCIALMENTE', 'NO_APLICA']
            
            self.stdout.write(f"Creando cumplimientos para {len(servicios_creados)} servicios y {criterios.count()} criterios...")
            
            for servicio in servicios_creados:
                for criterio in criterios:
                    try:
                        cumplimiento, created = Cumplimiento.objects.get_or_create(
                            autoevaluacion=autoevaluacion,
                            servicio_sede=servicio,
                            criterio=criterio,
                            defaults={
                                'cumple': choice(resultados),
                                'responsable': "Dr. Carlos González",
                                'fecha_compromiso': date.today() + timedelta(days=30)
                            }
                        )
                        if created:
                            cumplimientos_creados += 1
                    except Exception as e:
                        pass

            self.stdout.write(self.style.SUCCESS(f"\n✅ Cumplimientos creados: {cumplimientos_creados}"))

        # 7. Resumen final
        self.stdout.write("\n" + "="*80)
        self.stdout.write("  RESUMEN DE DATOS CREADOS")
        self.stdout.write("="*80)
        self.stdout.write(f"Company: {company.name} (NIT: {company.nit})")
        self.stdout.write(f"Headquarters: {headquarters.name} ({headquarters.departament})")
        self.stdout.write(f"DatosPrestador: {datos_prestador.codigo_reps} ({datos_prestador.estado_habilitacion})")
        self.stdout.write(f"Servicios: {len(servicios_creados)}")
        self.stdout.write(f"Autoevaluación: {autoevaluacion.numero_autoevaluacion}")
        self.stdout.write(f"Cumplimientos: {Cumplimiento.objects.filter(autoevaluacion=autoevaluacion).count()}")
        self.stdout.write("="*80 + "\n")
