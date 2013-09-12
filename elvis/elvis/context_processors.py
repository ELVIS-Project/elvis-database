from django.conf import settings 

def render_static_url(request):
    return {'STATIC_URL': settings.STATIC_URL}