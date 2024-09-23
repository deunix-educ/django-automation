from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReservesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reserves'
    verbose_name = _('Reserves in stock')

