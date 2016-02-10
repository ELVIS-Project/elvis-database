from rest_framework import generics
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.exceptions import NotFound
from elvis.models import Attachment
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import os
import uuid


class MediaServeView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/?error=download-file")

        val = kwargs.get('pk')
        if not val:
            raise NotFound

        try:
            val_is_uuid = uuid.UUID(val)
        except ValueError:
            val_is_uuid = None

        if val_is_uuid:
            try:
                att = Attachment.objects.get(uuid=val)
            except ObjectDoesNotExist:
                raise NotFound
            path = att.attachment.name
            name = att.file_name
        else:
            path = os.path.join(settings.MEDIA_ROOT, val)
            name = os.path.split(path)[-1]

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=%s' % name
        if settings.SETTING_TYPE != "local":
            response['X-Accel-Redirect'] = path
        else:
            if not os.path.exists(path):
                raise NotFound
            with open(path, 'rb') as file:
                response.content = file
        return response
