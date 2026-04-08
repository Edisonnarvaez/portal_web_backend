from django.apps import AppConfig


class SoportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soportes'

    def ready(self):
        import soportes.signals