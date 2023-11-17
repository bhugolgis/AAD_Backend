from django.apps import AppConfig


class DoctorsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doctorsApp'



    def ready(self):
        import doctorsApp.signals
