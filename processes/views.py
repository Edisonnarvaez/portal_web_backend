from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
import mimetypes
import os

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Documento
from .serializers import DocumentoSerializer
from django.http import FileResponse

class DocumentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Documento.objects.all().order_by('-fecha_actualizacion')
    serializer_class = DocumentoSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    @action(detail=True, methods=['get'])
    @method_decorator(xframe_options_sameorigin)
    def preview(self, request, pk=None):
        """Endpoint para previsualizar documentos"""
        # Manejar autenticación por token en query params
        token = request.GET.get('token')
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                request.user = user
            except Exception:
                return HttpResponse('Token inválido', status=401)
        
        documento = self.get_object()
        
        # Determinar qué archivo mostrar
        tipo_archivo = request.GET.get('tipo', 'oficial')
        if tipo_archivo == 'editable' and documento.archivo_editable:
            archivo = documento.archivo_editable
        else:
            archivo = documento.archivo_oficial
        
        if not archivo:
            return HttpResponse('No hay archivo disponible', status=404)
        
        try:
            # Determinar el tipo de contenido
            content_type, _ = mimetypes.guess_type(archivo.name)
            
            # Leer el archivo
            file_data = archivo.read()
            
            response = HttpResponse(file_data, content_type=content_type)
            response['X-Frame-Options'] = 'SAMEORIGIN'
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(archivo.name)}"'
            
            return response
            
        except Exception as e:
            return HttpResponse(f'Error al acceder al archivo: {str(e)}', status=500)

    from django.http import FileResponse

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Endpoint para descargar documentos"""
        token = request.GET.get('token')
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                request.user = user
            except Exception:
                return HttpResponse('Token inválido', status=401)

        documento = self.get_object()
        
        tipo_archivo = request.GET.get('tipo', 'oficial')
        if tipo_archivo == 'editable' and documento.archivo_editable:
            archivo = documento.archivo_editable
        else:
            archivo = documento.archivo_oficial

        if not archivo:
            return HttpResponse('No hay archivo disponible', status=404)
        
        try:
            # Mapping manual de MIME types
            MIME_TYPES = {
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xls': 'application/vnd.ms-excel',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                '.pdf': 'application/pdf',
            }

            filename = os.path.basename(archivo.name)
            ext = os.path.splitext(filename)[1].lower()
            content_type = MIME_TYPES.get(ext, 'application/octet-stream')

            response = FileResponse(archivo, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            return HttpResponse(f'Error al acceder al archivo: {str(e)}', status=500)



        @action(detail=False, methods=['get'])
        def vigentes(self, request):
            """Endpoint para obtener solo los documentos vigentes"""
            documentos_vigentes = Documento.get_documentos_vigentes()
            serializer = self.get_serializer(documentos_vigentes, many=True)
            return Response(serializer.data)

        @action(detail=True, methods=['post'])
        def crear_nueva_version(self, request, pk=None):
            """Endpoint para crear una nueva versión de un documento"""
            documento_padre = self.get_object()
            
            # Crear una nueva versión
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                # El documento padre se establece automáticamente
                serializer.save(documento_padre=documento_padre)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)