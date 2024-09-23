from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DevicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = _('Devices')
    name = 'devices'

    def ready(self):
        import devices.signals  # noqa