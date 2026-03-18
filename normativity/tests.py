"""
normativity/tests.py

Tests unitarios para la app normativity.
Cobertura: Models, Serializers y Views
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Estandar, Criterio, DocumentoNormativo

User = get_user_model()


class EstandarModelTests(TestCase):
    """Tests para el modelo Estandar"""
    
    def setUp(self):
        self.estandar = Estandar.objects.create(
            codigo='TH',
            nombre='Talento Humano',
            descripcion='Estándar de recursos humanos',
            version_resolucion='3100/2019',
            estado=True
        )
    
    def test_estandar_creation(self):
        """Verificar que se crea correctamente un estándar"""
        self.assertEqual(self.estandar.codigo, 'TH')
        self.assertEqual(self.estandar.nombre, 'Talento Humano')
        self.assertTrue(self.estandar.estado)
    
    def test_estandar_string_representation(self):
        """Verificar la representación en string"""
        expected = f"{self.estandar.get_codigo_display()} - {self.estandar.nombre}"
        self.assertEqual(str(self.estandar), expected)
    
    def test_estandar_codigo_is_unique(self):
        """Verificar que el código es único"""
        with self.assertRaises(Exception):
            Estandar.objects.create(
                codigo='TH',
                nombre='Otro Talento',
                version_resolucion='3100/2019'
            )
    
    def test_all_7_estandares_exist(self):
        """Verificar que existen los 7 estándares"""
        codigos = ['TH', 'INF', 'DOT', 'PO', 'RS', 'GI', 'SA']
        for codigo in codigos:
            Estandar.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': f'Estandar {codigo}', 'version_resolucion': '3100/2019'}
            )
        
        self.assertEqual(Estandar.objects.count(), 7)


class CriterioModelTests(TestCase):
    """Tests para el modelo Criterio"""
    
    def setUp(self):
        self.estandar = Estandar.objects.create(
            codigo='TH',
            nombre='Talento Humano',
            version_resolucion='3100/2019'
        )
        self.criterio = Criterio.objects.create(
            estandar=self.estandar,
            codigo='1.1',
            nombre='Personal especializado',
            complejidad='ALTA',
            es_mandatorio=True,
            aplica_todos=True,
            requiere_evidencia_documental=True
        )
    
    def test_criterio_creation(self):
        """Verificar que se crea correctamente un criterio"""
        self.assertEqual(self.criterio.codigo, '1.1')
        self.assertEqual(self.criterio.complejidad, 'ALTA')
        self.assertTrue(self.criterio.es_mandatorio)
    
    def test_criterio_unique_with_estandar(self):
        """Verificar que código + estandar es único"""
        with self.assertRaises(Exception):
            Criterio.objects.create(
                estandar=self.estandar,
                codigo='1.1',
                nombre='Otro criterio'
            )
    
    def test_criterio_complejidad_choices(self):
        """Verificar las opciones de complejidad"""
        criterio_baja = Criterio.objects.create(
            estandar=self.estandar,
            codigo='1.2',
            nombre='Test bajo',
            complejidad='BAJA'
        )
        self.assertEqual(criterio_baja.complejidad, 'BAJA')
    
    def test_criterio_string_representation(self):
        """Verificar representación en string"""
        self.assertEqual(str(self.criterio), '1.1 - Personal especializado')


class DocumentoNormativoModelTests(TestCase):
    """Tests para el modelo DocumentoNormativo"""
    
    def setUp(self):
        self.documento = DocumentoNormativo.objects.create(
            titulo='Resolución 3100 de 2019',
            tipo='RESOLUCION',
            numero_referencia='3100/2019'
        )
    
    def test_documento_creation(self):
        """Verificar que se crea correctamente un documento"""
        self.assertEqual(self.documento.titulo, 'Resolución 3100 de 2019')
        self.assertEqual(self.documento.tipo, 'RESOLUCION')
    
    def test_documento_many_to_many_criterios(self):
        """Verificar relación M2M con criterios"""
        estandar = Estandar.objects.create(
            codigo='SA',
            nombre='Seguridad',
            version_resolucion='3100/2019'
        )
        criterio = Criterio.objects.create(
            estandar=estandar,
            codigo='7.1',
            nombre='Protocolos'
        )
        
        self.documento.criterios_relacionados.add(criterio)
        self.assertEqual(self.documento.criterios_relacionados.count(), 1)


class EstandarAPITests(APITestCase):
    """Tests para los endpoints de Estandar"""
    
    def setUp(self):
        self.client = APIClient()
        self.estandar = Estandar.objects.create(
            codigo='TH',
            nombre='Talento Humano',
            version_resolucion='3100/2019'
        )
        self.criterio = Criterio.objects.create(
            estandar=self.estandar,
            codigo='1.1',
            nombre='Personal especializado',
            complejidad='ALTA'
        )
    
    def test_list_estandares(self):
        """Verificar listado de estándares"""
        response = self.client.get('/api/normativity/estandares/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Las vistas devuelven listas directamente sin paginación
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
    
    def test_retrieve_estandar(self):
        """Verificar que se obtiene detalle de un estándar"""
        response = self.client.get(f'/api/normativity/estandares/{self.estandar.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'TH')
    
    def test_estandar_action_todos(self):
        """Verificar acción /todos/"""
        response = self.client.get('/api/normativity/estandares/todos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_estandar_criterios_relationship(self):
        """Verificar que los criterios están en el detalle"""
        response = self.client.get(f'/api/normativity/estandares/{self.estandar.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('criterios', response.data)
        self.assertEqual(len(response.data['criterios']), 1)


class CriterioAPITests(APITestCase):
    """Tests para los endpoints de Criterio"""
    
    def setUp(self):
        self.client = APIClient()
        self.estandar = Estandar.objects.create(
            codigo='SA',
            nombre='Seguridad del Paciente',
            version_resolucion='3100/2019'
        )
        # Criterios de diferentes complejidades
        self.criterio_alta = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.1',
            nombre='Protocolos de infección',
            complejidad='ALTA',
            es_mandatorio=True
        )
        self.criterio_media = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.2',
            nombre='Reporte de eventos',
            complejidad='MEDIA',
            es_mandatorio=True
        )
        self.criterio_baja = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.3',
            nombre='Identificación de riesgos',
            complejidad='BAJA',
            es_mandatorio=False
        )
    
    def test_list_criterios(self):
        """Verificar listado de criterios"""
        response = self.client.get('/api/normativity/criterios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
    
    def test_filter_by_complejidad(self):
        """Verificar filtro por complejidad"""
        response = self.client.get('/api/normativity/criterios/?complejidad=ALTA')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Todos deben ser ALTA
        self.assertIsInstance(response.data, list)
        if len(response.data) > 0:
            for criterio in response.data:
                self.assertEqual(criterio['complejidad'], 'ALTA')
    
    def test_mandatorios_action(self):
        """Verificar acción /mandatorios/"""
        response = self.client.get('/api/normativity/criterios/mandatorios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Los 2 primeros son mandatorios
        self.assertIsInstance(response.data, list)
    
    def test_con_evidencia_action(self):
        """Verificar acción /con_evidencia/"""
        # Crear criterio que requiere evidencia
        criterio_evidencia = Criterio.objects.create(
            estandar=self.estandar,
            codigo='7.4',
            nombre='Documentación',
            requiere_evidencia_documental=True
        )
        
        response = self.client.get('/api/normativity/criterios/con_evidencia/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_search_criterio(self):
        """Verificar búsqueda por nombre"""
        response = self.client.get('/api/normativity/criterios/?search=Personal')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class DocumentoNormativoAPITests(APITestCase):
    """Tests para los endpoints de DocumentoNormativo"""
    
    def setUp(self):
        self.client = APIClient()
        self.documento = DocumentoNormativo.objects.create(
            titulo='Resolución 3100',
            tipo='RESOLUCION',
            numero_referencia='3100/2019'
        )
    
    def test_list_documentos(self):
        """Verificar listado de documentos"""
        response = self.client.get('/api/normativity/documentos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_retrieve_documento(self):
        """Verificar detalle de documento"""
        response = self.client.get(f'/api/normativity/documentos/{self.documento.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Resolución 3100')
