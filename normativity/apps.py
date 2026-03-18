"""
normativity/apps.py

Configuración de la app normativity.
"""

from django.apps import AppConfig


class NormativityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'normativity'
    verbose_name = 'Normativity - Datos Maestros de Resolución 3100'
