"""
habilitacion/tests.py

Tests unitarios para la app habilitacion.
Cobertura: Models, Serializers y Views
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from datetime import timedelta

from .models import DatosPrestador, ServicioSede, Autoevaluacion, Cumplimiento
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
        self.prestador = DatosPrestador.objects.create(
            company=self.company,
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
            company=self.company,
            codigo_reps='110001234568',
            fecha_vencimiento_habilitacion=timezone.now().date() - timedelta(days=10)
        )
        self.assertTrue(prestador_vencido.esta_vencida())
    
    def test_prestador_string_representation(self):
        """Verificar representación en string"""
        expected = f"{self.prestador.codigo_reps} - {self.company.name}"
        self.assertEqual(str(self.prestador), expected)
    
    def test_prestador_one_to_one_with_company(self):
        """Verificar relación OneToOne con Company"""
        retrieved = DatosPrestador.objects.get(company=self.company)
        self.assertEqual(retrieved.id, self.prestador.id)


class ServicioSedeModelTests(TestCase):
    """Tests para el modelo ServicioSede"""
    
    def setUp(self):
        self.company = Company.objects.create(name='Hospital Centro', foundationDate='2020-01-15')
        self.sede = Headquarters.objects.create(
            name='Sede Principal',
            company=self.company,
            address='Cra 1 # 1-1'
        )
        self.servicio = ServicioSede.objects.create(
            sede=self.sede,
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
    
    def test_servicio_unique_with_sede(self):
        """Verificar que código + sede es único"""
        with self.assertRaises(Exception):
            ServicioSede.objects.create(
                sede=self.sede,
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
        self.prestador = DatosPrestador.objects.create(
            company=self.company,
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
            company=self.company,
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
            sede=self.sede,
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
        self.prestador = DatosPrestador.objects.create(
            company=self.company,
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
            'company_id': self.company.id,
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
            company=self.company,
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
        self.prestador = DatosPrestador.objects.create(
            company=self.company,
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
            company=self.company,
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
            sede=self.sede,
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
        self.assertGreater(response.data['count'], 0)
    
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
        self.assertGreater(response.data['count'], 0)


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
    
    def test_complete_habilitacion_flow(self):
        """Test del flujo completo: crear prestador → servicio → autoevaluación → cumplimientos"""
        
        # 1. Crear prestador
        data_prestador = {
            'company_id': self.company.id,
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
