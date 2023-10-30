from django.apps import AppConfig


class HealthworkerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'healthworker'


    def ready(self):
        import healthworker.signals