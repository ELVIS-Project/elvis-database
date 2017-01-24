from django.shortcuts import render, redirect
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
    return render(request, "about.html", {'piece_count': Piece.objects.all().count(),
                                          'composer_count': Composer.objects.all().count(),
                                          'movement_count': Movement.objects.all().count()})


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
