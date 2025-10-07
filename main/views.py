from django.shortcuts import render
from django.utils import timezone
from datetime import datetime

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Funcionario, ContenidoInformativo, Evento, FelicitacionCumpleanios, Reconocimiento
from .serializers import (
    FuncionarioSerializer,
    ContenidoInformativoSerializer,
    EventoSerializer,
    FelicitacionCumpleaniosSerializer,
    ReconocimientoSerializer
)

class FuncionarioViewSet(viewsets.ModelViewSet):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer

class ContenidoInformativoViewSet(viewsets.ModelViewSet):
    queryset = ContenidoInformativo.objects.all()
    serializer_class = ContenidoInformativoSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

class FelicitacionCumpleaniosViewSet(viewsets.ModelViewSet):
    queryset = FelicitacionCumpleanios.objects.all()
    serializer_class = FelicitacionCumpleaniosSerializer
    
    def get_queryset(self):
        """
        Filtra las felicitaciones basado en los parámetros de la query.
        - mes=actual: Muestra solo los que cumplen años en el mes actual
        - mes=N: Muestra solo los que cumplen años en el mes N (1-12)
        """
        queryset = FelicitacionCumpleanios.objects.all()
        mes_param = self.request.query_params.get('mes', None)
        
        if mes_param:
            if mes_param == 'actual':
                # Obtener el mes actual
                mes_actual = timezone.now().month
                # Filtrar por funcionarios que cumplen años en el mes actual
                queryset = queryset.filter(funcionario__fecha_nacimiento__month=mes_actual)
            elif mes_param.isdigit():
                # Filtrar por mes específico (1-12)
                mes = int(mes_param)
                if 1 <= mes <= 12:
                    queryset = queryset.filter(funcionario__fecha_nacimiento__month=mes)
        
        return queryset.select_related('funcionario')
    
    @action(detail=False, methods=['get'])
    def cumpleanos_mes_actual(self, request):
        """
        Endpoint personalizado para obtener todos los cumpleaños del mes actual
        URL: /api/main/felicitaciones/cumpleanos_mes_actual/
        """
        mes_actual = timezone.now().month
        felicitaciones = FelicitacionCumpleanios.objects.filter(
            funcionario__fecha_nacimiento__month=mes_actual
        ).select_related('funcionario')
        
        serializer = self.get_serializer(felicitaciones, many=True)
        return Response({
            'mes': mes_actual,
            'total_cumpleanos': felicitaciones.count(),
            'felicitaciones': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def cumpleanos_hoy(self, request):
        """
        Endpoint personalizado para obtener los cumpleaños de hoy
        URL: /api/main/felicitaciones/cumpleanos_hoy/
        """
        hoy = timezone.now()
        felicitaciones = FelicitacionCumpleanios.objects.filter(
            funcionario__fecha_nacimiento__month=hoy.month,
            funcionario__fecha_nacimiento__day=hoy.day
        ).select_related('funcionario')
        
        serializer = self.get_serializer(felicitaciones, many=True)
        return Response({
            'fecha': hoy.date(),
            'total_cumpleanos_hoy': felicitaciones.count(),
            'felicitaciones': serializer.data
        })

class ReconocimientoViewSet(viewsets.ModelViewSet):
    queryset = Reconocimiento.objects.all().order_by('-fecha')
    serializer_class = ReconocimientoSerializer
    
    def get_queryset(self):
        """
        Filtra los reconocimientos basado en los parámetros de la query.
        - publicar=true: Muestra solo los reconocimientos publicados
        - publicar=false: Muestra solo los reconocimientos no publicados
        """
        queryset = Reconocimiento.objects.all().order_by('-fecha')
        publicar_param = self.request.query_params.get('publicar', None)
        
        if publicar_param is not None:
            if publicar_param.lower() == 'true':
                queryset = queryset.filter(publicar=True)
            elif publicar_param.lower() == 'false':
                queryset = queryset.filter(publicar=False)
        
        return queryset.select_related('funcionario')
    
    @action(detail=False, methods=['get'])
    def publicados(self, request):
        """
        Endpoint personalizado para obtener solo los reconocimientos publicados
        URL: /api/main/reconocimientos/publicados/
        """
        reconocimientos = Reconocimiento.objects.filter(publicar=True).order_by('-fecha')
        serializer = self.get_serializer(reconocimientos, many=True)
        return Response({
            'total_publicados': reconocimientos.count(),
            'reconocimientos': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def no_publicados(self, request):
        """
        Endpoint personalizado para obtener solo los reconocimientos no publicados
        URL: /api/main/reconocimientos/no_publicados/
        """
        reconocimientos = Reconocimiento.objects.filter(publicar=False).order_by('-fecha')
        serializer = self.get_serializer(reconocimientos, many=True)
        return Response({
            'total_no_publicados': reconocimientos.count(),
            'reconocimientos': serializer.data
        })

# para el manejo de roles de aplicación
#from rest_framework.permissions import BasePermission

#class HasAppRole(BasePermission):
#    def has_permission(self, request, view):
#        required_role = getattr(view, 'required_role', None)
#        app_name = getattr(view, 'app_name', None)
#        if not required_role or not app_name:
#            return True
#        return request.user.roles.filter(name=required_role, app__name=app_name).exists()