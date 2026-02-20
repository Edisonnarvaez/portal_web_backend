from django.apps import AppConfig


class MejorasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mejoras'
    verbose_name = 'Planes de Mejora y Hallazgos'

    def ready(self):
        """Registrar signals al iniciar la app."""
        import mejoras.signals  # noqa: F401
