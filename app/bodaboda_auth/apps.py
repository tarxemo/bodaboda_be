from django.apps import AppConfig

class BodabodaAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bodaboda_auth'

    def ready(self):
        import bodaboda_auth.signals
