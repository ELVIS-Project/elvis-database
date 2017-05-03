from django.shortcuts import render, redirect
from django.core.cache import cache
from rest_framework import generics, permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from elvis.models import Piece, Composer, Movement
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer


# Render the home page
def home(request):
    return render(request, "home.html", {})


# Render the about page
def about(request):

    seconds_in_week = 604800

    # Count how many of these models we have, using the cache to store
    # the values for a week.
    model_counts = {Piece: None, Composer: None, Movement: None}
    for model in model_counts:
        cache_key = 'global_{}_count'.format(str(model))
        value = cache.get(cache_key)
        if value is None:
            value = model.objects.count()
            cache.set(cache_key, value, seconds_in_week)
        model_counts[model] = value

    return render(request, "about.html", {'piece_count': model_counts[Piece],
                                          'composer_count': model_counts[Composer],
                                          'movement_count': model_counts[Movement]})


class TOSHTMLRenderer(CustomHTMLRenderer):
    template_name = "terms_of_service.html"


# Render the TOS page.
class TOSPage(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer, TOSHTMLRenderer)

    def get(self, request, *args, **kwargs):
        data = {
            "error": {
                "message": "You must accept the terms of service to continue. "
                           "Use the HTML version of the website to do this.",
                "code": 403
            },
            "data": {
                "path": request.path,
                "accepted_tos": request.user.userprofile.accepted_tos
            }
        }
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, *args, **kwargs):
        accepted_tos = True if request.POST.get('accepts-TOS') == 'on' else False
        if not accepted_tos:
            return self.get(request, *args, **kwargs)

        user = request.user
        user.userprofile.accepted_tos = accepted_tos
        user.userprofile.save()
        request.session['ACCEPTED_TOS'] = accepted_tos
        return redirect('/')


# LM Render the query page
def queries(request):
    return render(request, "query.html", {})

def contact(request):
    return render(request, "contact.html", {})
