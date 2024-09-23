#
# encoding: utf-8
from django.conf import settings
from django.contrib.sites.models import Site
      
def params(request):
    site = Site.objects.filter(id=settings.SITE_ID).first()
    return {
        'APP_TITLE': settings.APP_TITLE,
        'APP_TITLE': settings.APP_TITLE,
        'APP_SUB_TITLE': settings.APP_SUB_TITLE,
        'APP_MENU_TABS': settings.APP_MENU_TABS,        
        'SITE_NAME': f'{site.name}',
        'SITE_DOMAIN': f'{site.domain}',
        'is_leaflet': settings.IS_LEAFLET,
        'self_url': request.build_absolute_uri(),
    }
    
        