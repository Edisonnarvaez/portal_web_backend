"""
habilitacion/apps.py

Configuración de la aplicación Django para habilitación de servicios de salud.
"""

from django.apps import AppConfig


class HabilitacionConfig(AppConfig):
    """
    Configuración de la app habilitación.
    
    Módulo para gestionar habilitación de servicios de salud conforme
    a la Resolución 3100 de 2019 de Colombia.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'habilitacion'
    verbose_name = 'Habilitación - Servicios de Salud'
