from django.apps import AppConfig


class ActivityLogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activity_log'
    verbose_name = 'Journal d\'activité'
    
    def ready(self):
        """Importer les signaux au démarrage de l'application"""
        import activity_log.signals
