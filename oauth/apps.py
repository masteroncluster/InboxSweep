from django.apps import AppConfig

class OauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oauth'
    
    def ready(self):
        # Import signal handlers
        import oauth.signals