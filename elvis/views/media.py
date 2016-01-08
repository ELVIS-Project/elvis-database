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
            resp = HttpResponse(att.attachment, content_type='application/force-download')
            resp['Content-Disposition'] = 'attachment; filename=%s' % att.title
            return resp
        else:
            path = os.path.join(settings.MEDIA_ROOT, val)
            if not os.path.exists(path):
                raise NotFound
            with open(path, 'rb') as file:
                resp = HttpResponse(file, content_type='application/force-download')
                return resp
