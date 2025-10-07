from rest_framework import serializers
from .models import Funcionario, ContenidoInformativo, Evento, FelicitacionCumpleanios, Reconocimiento
from companies.models.headquarters import Headquarters

class HeadquartersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarters
        fields = ['id', 'name', 'habilitationCode', 'city', 'address']

class FuncionarioSerializer(serializers.ModelSerializer):
    sede = HeadquartersSerializer(read_only=True)
    sede_id = serializers.PrimaryKeyRelatedField(
        queryset=Headquarters.objects.all(), source="sede", write_only=True
    )
    
    class Meta:
        model = Funcionario
        fields = '__all__'

class ContenidoInformativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContenidoInformativo
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'

class FelicitacionCumpleaniosSerializer(serializers.ModelSerializer):
    funcionario = FuncionarioSerializer(read_only=True)
    fecha_nacimiento = serializers.SerializerMethodField()
    mes_cumpleanos = serializers.SerializerMethodField()
    dias_hasta_cumpleanos = serializers.SerializerMethodField()

    class Meta:
        model = FelicitacionCumpleanios
        fields = '__all__'
    
    def get_fecha_nacimiento(self, obj):
        """Retorna la fecha de nacimiento del funcionario"""
        return obj.funcionario.fecha_nacimiento
    
    def get_mes_cumpleanos(self, obj):
        """Retorna el mes de cumpleaños (1-12)"""
        return obj.funcionario.fecha_nacimiento.month
    
    def get_dias_hasta_cumpleanos(self, obj):
        """Calcula cuántos días faltan para el cumpleaños"""
        from datetime import date
        today = date.today()
        fecha_nac = obj.funcionario.fecha_nacimiento
        
        # Crear la fecha de cumpleaños de este año
        cumpleanos_este_ano = date(today.year, fecha_nac.month, fecha_nac.day)
        
        # Si ya pasó el cumpleaños este año, calcular para el próximo año
        if cumpleanos_este_ano < today:
            cumpleanos_este_ano = date(today.year + 1, fecha_nac.month, fecha_nac.day)
        
        # Calcular diferencia en días
        diferencia = cumpleanos_este_ano - today
        return diferencia.days

class ReconocimientoSerializer(serializers.ModelSerializer):
    funcionario = FuncionarioSerializer(read_only=True)
    funcionario_id = serializers.PrimaryKeyRelatedField(
        queryset=Funcionario.objects.all(), source="funcionario", write_only=True
    )

    class Meta:
        model = Reconocimiento
        fields = '__all__'
