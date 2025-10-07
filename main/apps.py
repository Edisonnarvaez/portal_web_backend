from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        """
        Método que se ejecuta cuando la app está lista.
        Aquí importamos las señales para que se registren.
        """
        import main.signals
