from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AutomationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = _('Automation')    
    name = 'automation'

    def ready(self):
        import automation.signals  # noqa