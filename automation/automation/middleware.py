from django.conf import settings

def SetDefaultLangMiddleware(get_response):

    def middleware(request):
        if not request.COOKIES.get('django_language'):
            request.COOKIES['django_language'] = settings.LANGUAGE_CODE
        response = get_response(request)
        return response
    return middleware
