from rest_framework import generics
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.exceptions import NotFound

from django.conf import settings

import os


class MediaServeView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/?error=download-file")

        path = kwargs.get('pk')
        name = os.path.split(path)[-1]
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        if settings.SETTING_TYPE != "local":
            response['X-Accel-Redirect'] = os.path.join("/media_serve/", path)
        else:
            if not os.path.exists(path):
                raise NotFound
            with open(path, 'rb') as file:
                response.content = file
        return response
