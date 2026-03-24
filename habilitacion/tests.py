"""
habilitacion/tests.py

Tests unitarios para la app habilitacion.
Cobertura: Models, Serializers y Views
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from datetime import timedelta

from .models import (
    DatosPrestador,
    ServicioSede,
    Autoevaluacion,
    Cumplimiento,
    NovedadREPS,
    RequisitoDocumental,
    ChecklistVerificacion,
    ChecklistItem,
    EvidenciaChecklist,
)
from companies.models import Company, Headquarters
from normativity.models import Estandar, Criterio

User = get_user_model()


class DatosPrestadorModelTests(TestCase):
    """Tests para el modelo DatosPrestador"""
    
    def setUp(self):
        self.company = Company.objects.create(
            name='Hospital Centro',
            nit='123456789',
            foundationDate='2020-01-15'
        )
        self.headquarters = Headquarters.objects.create(
            company=self.company,
            name='Sede Centro',
            address='Cra 1 # 1-1'
        )
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001234567',
            clase_prestador='IPS',
            estado_habilitacion='EN_PROCESO',
            fecha_vencimiento_habilitacion=timezone.now().date() + timedelta(days=150)
        )
    
    def test_prestador_creation(self):
        """Verificar creación de prestador"""
        self.assertEqual(self.prestador.codigo_reps, '110001234567')
        self.assertEqual(self.prestador.clase_prestador, 'IPS')
    
    def test_dias_para_vencimiento(self):
        """Verificar cálculo de días para vencimiento"""
        dias = self.prestador.dias_para_vencimiento()
        self.assertIsNotNone(dias)
        self.assertGreater(dias, 140)
    
    def test_esta_proxima_a_vencer(self):
        """Verificar si está próxima a vencer"""
        is_proxima = self.prestador.esta_proxima_a_vencer(dias=200)
        self.assertTrue(is_proxima)
    
    def test_esta_vencida(self):
        """Verificar si está vencida"""
        prestador_vencido = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001234568',
            fecha_vencimiento_habilitacion=timezone.now().date() - timedelta(days=10)
        )
        self.assertTrue(prestador_vencido.esta_vencida())
    
    def test_prestador_string_representation(self):
        """Verificar representación en string"""
        expected = f"{self.prestador.codigo_reps} - {self.headquarters.name}"
        self.assertEqual(str(self.prestador), expected)
    
    def test_prestador_multiple_per_headquarters(self):
        """Verificar que múltiples prestadores pueden existir en una sede"""
        # Crear segundo prestador en la misma sede
        prestador2 = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001234568',
            clase_prestador='PROF'
        )
        # Ambos deben existir
        retrieved = DatosPrestador.objects.filter(headquarters=self.headquarters).count()
        self.assertEqual(retrieved, 2)


class ServicioSedeModelTests(TestCase):
    """Tests para el modelo ServicioSede"""
    
    def setUp(self):
        self.company = Company.objects.create(name='Hospital Centro', foundationDate='2020-01-15')
        self.sede = Headquarters.objects.create(
            name='Sede Principal',
            company=self.company,
            address='Cra 1 # 1-1'
        )
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.sede,
            codigo_reps='110001234567',
            clase_prestador='IPS'
        )
        self.servicio = ServicioSede.objects.create(
            prestador=self.prestador,
            codigo_servicio='SVC-001',
            nombre_servicio='Urgencias',
            modalidad='URGENCIAS',
            complejidad='ALTA',
            fecha_vencimiento=timezone.now().date() + timedelta(days=200)
        )
    
    def test_servicio_creation(self):
        """Verificar creación de servicio"""
        self.assertEqual(self.servicio.codigo_servicio, 'SVC-001')
        self.assertEqual(self.servicio.complejidad, 'ALTA')
    
    def test_servicio_vencimiento(self):
        """Verificar cálculo de vencimiento"""
        dias = self.servicio.dias_para_vencimiento()
        self.assertIsNotNone(dias)
        self.assertGreater(dias, 190)
    
    def test_servicio_unique_with_prestador(self):
        """Verificar que código + prestador es único"""
        with self.assertRaises(Exception):
            ServicioSede.objects.create(
                prestador=self.prestador,
                codigo_servicio='SVC-001',
                nombre_servicio='Otro servicio'
            )
    
    def test_servicio_string_representation(self):
        """Verificar representación en string"""
        expected = f"{self.servicio.codigo_servicio} - {self.servicio.nombre_servicio}"
        self.assertEqual(str(self.servicio), expected)


class AutoevaluacionModelTests(TestCase):
    """Tests para el modelo Autoevaluacion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='evaluador',
            password='test123'
        )
        self.company = Company.objects.create(
            name='Hospital Test',
            nit='222222222',
            foundationDate='2020-01-15'
        )
        self.headquarters = Headquarters.objects.create(
            company=self.company,
            name='Sede Test',
            address='Cra 1'
        )
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001234567'
        )
        self.autoevaluacion = Autoevaluacion.objects.create(
            datos_prestador=self.prestador,
            periodo=2024,
            version=1,
            fecha_vencimiento=timezone.now().date() + timedelta(days=365),
            estado='BORRADOR',
            usuario_responsable=self.user
        )
    
    def test_autoevaluacion_creation(self):
        """Verificar creación de autoevaluación"""
        self.assertEqual(self.autoevaluacion.periodo, 2024)
        self.assertEqual(self.autoevaluacion.version, 1)
    
    def test_autoevaluacion_unique_together(self):
        """Verificar que período + versión es único por prestador"""
        with self.assertRaises(Exception):
            Autoevaluacion.objects.create(
                datos_prestador=self.prestador,
                periodo=2024,
                version=1,
                fecha_vencimiento=timezone.now().date()
            )
    
    def test_porcentaje_cumplimiento_empty(self):
        """Verificar cálculo de porcentaje sin cumplimientos"""
        porcentaje = self.autoevaluacion.porcentaje_cumplimiento()
        self.assertEqual(porcentaje, 0)
    
    def test_esta_vigente(self):
        """Verificar si está vigente"""
        self.assertTrue(self.autoevaluacion.esta_vigente())
    
    def test_autoevaluacion_string_representation(self):
        """Verificar representación en string"""
        expected = f"AUT-{self.prestador.codigo_reps}-{self.autoevaluacion.periodo} v{self.autoevaluacion.version}"
        self.assertIn('AUT-', str(self.autoevaluacion))


class CumplimientoModelTests(TestCase):
    """Tests para el modelo Cumplimiento"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='evaluador', password='test123')
        self.company = Company.objects.create(
            name='Hospital Test',
            nit='555555555',
            foundationDate='2020-01-15'
        )
        self.sede = Headquarters.objects.create(
            name='Sede Principal',
            company=self.company,
            address='Cra 1'
        )
        
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.sede,
            codigo_reps='110001234567'
        )
        self.autoevaluacion = Autoevaluacion.objects.create(
            datos_prestador=self.prestador,
            periodo=2024,
            version=1,
            fecha_vencimiento=timezone.now().date() + timedelta(days=365),
            usuario_responsable=self.user
        )
        self.servicio = ServicioSede.objects.create(
            prestador=self.prestador,
            codigo_servicio='SVC-001',
            nombre_servicio='Urgencias',
            modalidad='URGENCIAS',
            complejidad='ALTA'
        )
        
        self.estandar = Estandar.objects.create(
            codigo='SA',
            nombre='Seguridad',
            version_resolucion='3100/2019'
        )
        self.criterio = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.1',
            nombre='Protocolos',
            complejidad='ALTA'
        )
        
        self.cumplimiento = Cumplimiento.objects.create(
            autoevaluacion=self.autoevaluacion,
            servicio_sede=self.servicio,
            criterio=self.criterio,
            cumple='CUMPLE'
        )
    
    def test_cumplimiento_creation(self):
        """Verificar creación de cumplimiento"""
        self.assertEqual(self.cumplimiento.cumple, 'CUMPLE')
    
    def test_cumplimiento_unique_together(self):
        """Verificar que la combinación es única"""
        with self.assertRaises(Exception):
            Cumplimiento.objects.create(
                autoevaluacion=self.autoevaluacion,
                servicio_sede=self.servicio,
                criterio=self.criterio,
                cumple='NO_CUMPLE'
            )
    
    def test_tiene_plan_mejora(self):
        """Verificar si tiene plan de mejora"""
        self.assertFalse(self.cumplimiento.tiene_plan_mejora())
        
        self.cumplimiento.plan_mejora = 'Plan de acción'
        self.cumplimiento.save()
        self.assertTrue(self.cumplimiento.tiene_plan_mejora())
    
    def test_mejora_vencida(self):
        """Verificar si la mejora está vencida"""
        self.assertFalse(self.cumplimiento.mejora_vencida())
        
        self.cumplimiento.fecha_compromiso = timezone.now().date() - timedelta(days=10)
        self.cumplimiento.save()
        self.assertTrue(self.cumplimiento.mejora_vencida())


class ChecklistVerificacionModelTests(TestCase):
    """Tests para generación automática de ítems de checklist."""

    def setUp(self):
        self.user = User.objects.create_user(username='validador', password='test123')
        self.company = Company.objects.create(
            name='Hospital Checklist',
            nit='777777777',
            foundationDate='2020-01-15'
        )
        self.headquarters = Headquarters.objects.create(
            company=self.company,
            name='Sede Checklist',
            address='Cra 1 # 1-1'
        )
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001237777',
            nombre_prestador='Hospital Checklist IPS',
            clase_prestador='IPS',
        )
        self.servicio = ServicioSede.objects.create(
            prestador=self.prestador,
            codigo_servicio='SVC-CHK-001',
            nombre_servicio='Consulta Externa',
            modalidad='AMBULATORIA',
            complejidad='BAJA',
        )

    def test_crea_items_desde_requisitos_novedad(self):
        RequisitoDocumental.objects.create(
            codigo='NOV-BAS-001',
            nombre='Requisito novedad 1',
            tipo_tramite='NOVEDAD',
            obligatorio=True,
        )
        RequisitoDocumental.objects.create(
            codigo='NOV-BAS-002',
            nombre='Requisito novedad 2',
            tipo_tramite='NOVEDAD',
            obligatorio=False,
        )
        RequisitoDocumental.objects.create(
            codigo='INS-T-001',
            nombre='Requisito inscripcion',
            tipo_tramite='INSCRIPCION',
            obligatorio=True,
        )

        novedad = NovedadREPS.objects.create(
            codigo_novedad='NOV-TEST-001',
            tipo_novedad='SERVICIO',
            subtipo_novedad='OTRA',
            datos_prestador=self.prestador,
            servicio_sede=self.servicio,
            creado_por=self.user,
        )

        checklist = ChecklistVerificacion.objects.create(
            codigo_checklist='CHK-TEST-001',
            novedad=novedad,
            servicio_sede=self.servicio,
            responsable=self.user,
        )

        self.assertEqual(checklist.items.count(), 2)
        self.assertEqual(ChecklistItem.objects.filter(checklist=checklist).count(), 2)
        self.assertTrue(
            ChecklistItem.objects.filter(checklist=checklist, requisito__codigo='NOV-BAS-001').exists()
        )
        self.assertFalse(
            ChecklistItem.objects.filter(checklist=checklist, requisito__codigo='INS-T-001').exists()
        )

    def test_apertura_modalidad_incluye_visita_certificacion_y_base_novedad(self):
        RequisitoDocumental.objects.create(
            codigo='NOV-BAS-001',
            nombre='Base novedad',
            tipo_tramite='NOVEDAD',
            obligatorio=True,
        )
        RequisitoDocumental.objects.create(
            codigo='VC-001',
            nombre='Visita certificacion',
            tipo_tramite='VISITA_CERTIFICACION',
            obligatorio=True,
        )

        novedad = NovedadREPS.objects.create(
            codigo_novedad='NOV-TEST-002',
            tipo_novedad='SERVICIO',
            subtipo_novedad='APERTURA_MODALIDAD',
            datos_prestador=self.prestador,
            servicio_sede=self.servicio,
            creado_por=self.user,
        )

        checklist = ChecklistVerificacion.objects.create(
            codigo_checklist='CHK-TEST-002',
            novedad=novedad,
            servicio_sede=self.servicio,
            responsable=self.user,
        )

        self.assertTrue(
            ChecklistItem.objects.filter(checklist=checklist, requisito__codigo='NOV-BAS-001').exists()
        )
        self.assertTrue(
            ChecklistItem.objects.filter(checklist=checklist, requisito__codigo='VC-001').exists()
        )

    def test_cambio_contacto_filtra_requisitos_especificos(self):
        RequisitoDocumental.objects.create(
            codigo='NOV-BAS-001',
            nombre='Base novedad',
            tipo_tramite='NOVEDAD',
            obligatorio=True,
        )
        RequisitoDocumental.objects.create(
            codigo='NOV-CON-001',
            nombre='Novedad contacto',
            tipo_tramite='NOVEDAD',
            obligatorio=True,
        )
        RequisitoDocumental.objects.create(
            codigo='NOV-TS-001',
            nombre='Novedad traslado',
            tipo_tramite='NOVEDAD',
            obligatorio=True,
        )

        novedad = NovedadREPS.objects.create(
            codigo_novedad='NOV-TEST-003',
            tipo_novedad='SEDE',
            subtipo_novedad='CAMBIO_CONTACTO',
            datos_prestador=self.prestador,
            sede=self.headquarters,
            creado_por=self.user,
        )

        checklist = ChecklistVerificacion.objects.create(
            codigo_checklist='CHK-TEST-003',
            novedad=novedad,
            responsable=self.user,
        )

        self.assertTrue(
            ChecklistItem.objects.filter(checklist=checklist, requisito__codigo='NOV-BAS-001').exists()
        )
        self.assertTrue(
            ChecklistItem.objects.filter(checklist=checklist, requisito__codigo='NOV-CON-001').exists()
        )
        self.assertFalse(
            ChecklistItem.objects.filter(checklist=checklist, requisito__codigo='NOV-TS-001').exists()
        )


class DatosPrestadorAPITests(APITestCase):
    """Tests para endpoints de DatosPrestador"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.company = Company.objects.create(
            name='Hospital Test',
            nit='444444444',
            foundationDate='2020-01-15'
        )
        self.headquarters = Headquarters.objects.create(
            company=self.company,
            name='Sede Test',
            address='Cra 1'
        )
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001234567',
            clase_prestador='IPS'
        )
    
    def test_list_prestadores(self):
        """Verificar listado de prestadores"""
        response = self.client.get('/api/habilitacion/prestadores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)
    
    def test_create_prestador(self):
        """Verificar creación de prestador"""
        data = {
            'headquarters_id': self.headquarters.id,
            'codigo_reps': '110001234568',
            'clase_prestador': 'PROF'
        }
        response = self.client.post('/api/habilitacion/prestadores/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_retrieve_prestador(self):
        """Verificar detalle de prestador"""
        response = self.client.get(f'/api/habilitacion/prestadores/{self.prestador.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo_reps'], '110001234567')
    
    def test_proximos_a_vencer_action(self):
        """Verificar acción proximos_a_vencer"""
        # Crear prestador próximo a vencer
        prestador_vencer = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001234569',
            fecha_vencimiento_habilitacion=timezone.now().date() + timedelta(days=60),
            estado_habilitacion='HABILITADA'
        )
        
        response = self.client.get('/api/habilitacion/prestadores/proximos_a_vencer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_authentication_required(self):
        """Verificar que requiere autenticación"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/habilitacion/prestadores/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AutoevaluacionAPITests(APITestCase):
    """Tests para endpoints de Autoevaluacion"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='evaluador',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.company = Company.objects.create(
            name='Hospital Test',
            nit='333333333',
            foundationDate='2020-01-15'
        )
        self.headquarters = Headquarters.objects.create(
            company=self.company,
            name='Sede Test',
            address='Cra 1'
        )
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001234567'
        )
        self.autoevaluacion = Autoevaluacion.objects.create(
            datos_prestador=self.prestador,
            periodo=2024,
            version=1,
            fecha_vencimiento=timezone.now().date() + timedelta(days=365),
            usuario_responsable=self.user
        )
    
    def test_list_autoevaluaciones(self):
        """Verificar listado"""
        response = self.client.get('/api/habilitacion/autoevaluaciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_autoevaluacion(self):
        """Verificar creación"""
        data = {
            'datos_prestador_id': self.prestador.id,
            'periodo': 2025,
            'version': 1,
            'fecha_vencimiento': (timezone.now().date() + timedelta(days=365)).isoformat(),
            'estado': 'BORRADOR'
        }
        response = self.client.post('/api/habilitacion/autoevaluaciones/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_resumen_action(self):
        """Verificar acción resumen"""
        response = self.client.get(f'/api/habilitacion/autoevaluaciones/{self.autoevaluacion.id}/resumen/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_cumplimientos', response.data)
    
    def test_validar_action(self):
        """Verificar acción validar"""
        response = self.client.post(f'/api/habilitacion/autoevaluaciones/{self.autoevaluacion.id}/validar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el estado cambió
        self.autoevaluacion.refresh_from_db()
        self.assertEqual(self.autoevaluacion.estado, 'VALIDADA')
    
    def test_duplicar_action(self):
        """Verificar acción duplicar (renovación anual)"""
        response = self.client.post(f'/api/habilitacion/autoevaluaciones/{self.autoevaluacion.id}/duplicar/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['periodo'], 2025)


class CumplimientoAPITests(APITestCase):
    """Tests para endpoints de Cumplimiento"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='evaluador',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Setup de datos relacionados
        self.company = Company.objects.create(
            name='Hospital Test',
            nit='666666666',
            foundationDate='2020-01-15'
        )
        self.sede = Headquarters.objects.create(
            name='Sede Principal',
            company=self.company,
            address='Cra 1'
        )
        
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.sede,
            codigo_reps='110001234567'
        )
        self.autoevaluacion = Autoevaluacion.objects.create(
            datos_prestador=self.prestador,
            periodo=2024,
            version=1,
            fecha_vencimiento=timezone.now().date() + timedelta(days=365),
            usuario_responsable=self.user
        )
        self.servicio = ServicioSede.objects.create(
            prestador=self.prestador,
            codigo_servicio='SVC-001',
            nombre_servicio='Urgencias',
            modalidad='URGENCIAS',
            complejidad='ALTA'
        )
        
        self.estandar = Estandar.objects.create(
            codigo='SA',
            nombre='Seguridad',
            version_resolucion='3100/2019'
        )
        self.criterio = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.1',
            nombre='Protocolos'
        )
        
        self.cumplimiento = Cumplimiento.objects.create(
            autoevaluacion=self.autoevaluacion,
            servicio_sede=self.servicio,
            criterio=self.criterio,
            cumple='CUMPLE'
        )
    
    def test_list_cumplimientos(self):
        """Verificar listado"""
        response = self.client.get('/api/habilitacion/cumplimientos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_cumplimiento(self):
        """Verificar creación"""
        # Crear otro criterio para prueba
        criterio2 = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.2',
            nombre='Reporte eventos'
        )
        
        data = {
            'autoevaluacion_id': self.autoevaluacion.id,
            'servicio_sede_id': self.servicio.id,
            'criterio_id': criterio2.id,
            'cumple': 'NO_CUMPLE',
            'hallazgo': 'Test hallazgo'
        }
        response = self.client.post('/api/habilitacion/cumplimientos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_sin_cumplir_action(self):
        """Verificar acción sin_cumplir"""
        # Crear uno que no cumple
        criterio2 = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.3',
            nombre='Identificación'
        )
        Cumplimiento.objects.create(
            autoevaluacion=self.autoevaluacion,
            servicio_sede=self.servicio,
            criterio=criterio2,
            cumple='NO_CUMPLE'
        )
        
        response = self.client.get('/api/habilitacion/cumplimientos/sin_cumplir/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_mejoras_vencidas_action(self):
        """Verificar acción mejoras_vencidas"""
        # Crear cumplimiento con fecha vencida
        criterio2 = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.4',
            nombre='Riesgos'
        )
        cumpl_vencido = Cumplimiento.objects.create(
            autoevaluacion=self.autoevaluacion,
            servicio_sede=self.servicio,
            criterio=criterio2,
            cumple='NO_CUMPLE',
            plan_mejora='Mejorar',
            fecha_compromiso=timezone.now().date() - timedelta(days=10)
        )
        
        response = self.client.get('/api/habilitacion/cumplimientos/mejoras_vencidas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_con_plan_mejora_action(self):
        """Verificar acción con_plan_mejora"""
        criterio2 = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.5',
            nombre='Seguimiento mejora'
        )
        Cumplimiento.objects.create(
            autoevaluacion=self.autoevaluacion,
            servicio_sede=self.servicio,
            criterio=criterio2,
            cumple='NO_CUMPLE',
            plan_mejora='Plan formal'
        )

        response = self.client.get('/api/habilitacion/cumplimientos/con_plan_mejora/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class NuevosEndpointsAPITests(APITestCase):
    """Pruebas de regresión para novedad/checklist/evidencias y acciones de mejora."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apiuser', password='test123')
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(
            name='Hospital API',
            nit='999999999',
            foundationDate='2020-01-15'
        )
        self.headquarters = Headquarters.objects.create(
            company=self.company,
            name='Sede API',
            address='Cra 10 # 10-10'
        )
        self.prestador = DatosPrestador.objects.create(
            headquarters=self.headquarters,
            codigo_reps='110001239999',
            nombre_prestador='Hospital API IPS',
            clase_prestador='IPS',
        )
        self.servicio = ServicioSede.objects.create(
            prestador=self.prestador,
            codigo_servicio='SVC-API-001',
            nombre_servicio='Consulta General',
            modalidad='AMBULATORIA',
            complejidad='BAJA',
        )

        RequisitoDocumental.objects.create(
            codigo='NOV-BAS-001',
            nombre='Base novedad',
            tipo_tramite='NOVEDAD',
            obligatorio=True,
        )
        RequisitoDocumental.objects.create(
            codigo='NOV-CON-001',
            nombre='Cambio contacto',
            tipo_tramite='NOVEDAD',
            obligatorio=True,
        )
        RequisitoDocumental.objects.create(
            codigo='VP-001',
            nombre='Visita previa',
            tipo_tramite='VISITA_PREVIA',
            obligatorio=True,
        )

    def test_novedad_create_checklist_avance_and_evidencia_upload(self):
        payload_novedad = {
            'codigo_novedad': 'NOV-API-001',
            'tipo_novedad': 'SEDE',
            'subtipo_novedad': 'CAMBIO_CONTACTO',
            'estado': 'BORRADOR',
            'datos_prestador': self.prestador.id,
            'sede': self.headquarters.id,
            'servicio_sede': self.servicio.id,
            'requiere_visita_previa': True,
            'descripcion': 'Cambio de contacto y visita previa',
        }
        resp_novedad = self.client.post('/api/habilitacion/novedades-reps/', payload_novedad)
        self.assertEqual(resp_novedad.status_code, status.HTTP_201_CREATED)
        novedad_id = resp_novedad.data['id']

        payload_checklist = {
            'codigo_checklist': 'CHK-API-001',
            'estado': 'BORRADOR',
            'novedad': novedad_id,
            'servicio_sede': self.servicio.id,
            'observaciones': 'Checklist API',
        }
        resp_checklist = self.client.post('/api/habilitacion/checklists-verificacion/', payload_checklist)
        self.assertEqual(resp_checklist.status_code, status.HTTP_201_CREATED)
        checklist_id = resp_checklist.data['id']

        checklist = ChecklistVerificacion.objects.get(id=checklist_id)
        self.assertGreaterEqual(checklist.items.count(), 2)

        resp_avance = self.client.get(f'/api/habilitacion/checklists-verificacion/{checklist_id}/avance/')
        self.assertEqual(resp_avance.status_code, status.HTTP_200_OK)
        self.assertIn('porcentaje_avance', resp_avance.data)

        item = checklist.items.first()
        self.assertIsNotNone(item)

        resp_item_update = self.client.patch(
            f'/api/habilitacion/checklist-items/{item.id}/',
            {'cumple': True, 'observaciones': 'Cumple con soporte'},
            format='json'
        )
        self.assertEqual(resp_item_update.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.verificado_por, self.user)

        archivo_pdf = SimpleUploadedFile('evidencia.pdf', b'%PDF-1.4 evidencia', content_type='application/pdf')
        resp_evidencia = self.client.post(
            '/api/habilitacion/evidencias-checklist/',
            {
                'checklist_item': item.id,
                'tipo': 'DOCUMENTO',
                'archivo': archivo_pdf,
            },
            format='multipart'
        )
        self.assertEqual(resp_evidencia.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EvidenciaChecklist.objects.filter(checklist_item=item).count(), 1)

    def test_evidencia_rechaza_extension_no_permitida(self):
        novedad = NovedadREPS.objects.create(
            codigo_novedad='NOV-API-002',
            tipo_novedad='SERVICIO',
            subtipo_novedad='OTRA',
            datos_prestador=self.prestador,
            servicio_sede=self.servicio,
            creado_por=self.user,
        )
        checklist = ChecklistVerificacion.objects.create(
            codigo_checklist='CHK-API-002',
            novedad=novedad,
            servicio_sede=self.servicio,
            responsable=self.user,
        )
        item = checklist.items.first()

        archivo_invalido = SimpleUploadedFile('malicioso.exe', b'MZP', content_type='application/octet-stream')
        resp = self.client.post(
            '/api/habilitacion/evidencias-checklist/',
            {
                'checklist_item': item.id,
                'tipo': 'DOCUMENTO',
                'archivo': archivo_invalido,
            },
            format='multipart'
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class IntegrationTests(APITestCase):
    """Tests de integración de flujos completos"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='director',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.company = Company.objects.create(
            name='Hospital Integración',
            nit='987654321',
            foundationDate='2020-01-15'
        )
        self.headquarters = Headquarters.objects.create(
            company=self.company,
            name='Sede Integración',
            address='Cra 1'
        )
    
    def test_complete_habilitacion_flow(self):
        """Test del flujo completo: crear prestador → servicio → autoevaluación → cumplimientos"""
        
        # 1. Crear prestador
        data_prestador = {
            'headquarters_id': self.headquarters.id,
            'codigo_reps': '110001234567',
            'clase_prestador': 'IPS'
        }
        resp_prestador = self.client.post('/api/habilitacion/prestadores/', data_prestador)
        self.assertEqual(resp_prestador.status_code, status.HTTP_201_CREATED)
        prestador_id = resp_prestador.data['id']
        
        # 2. Crear sede
        self.sede = Headquarters.objects.create(
            name='Sede Test',
            company=self.company,
            address='Cra 1'
        )
        
        # 3. Crear autoevaluación
        data_autoevaluacion = {
            'datos_prestador_id': prestador_id,
            'periodo': 2024,
            'version': 1,
            'fecha_vencimiento': (timezone.now().date() + timedelta(days=365)).isoformat(),
            'estado': 'BORRADOR'
        }
        resp_autoevaluacion = self.client.post(
            '/api/habilitacion/autoevaluaciones/',
            data_autoevaluacion
        )
        self.assertEqual(resp_autoevaluacion.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el flujo se completó
        self.assertIsNotNone(prestador_id)
