from elvis.models.attachment import Attachment
from elvis.serializers import AttachmentFullSerializer
from elvis.forms.create import JsymbolicForm
from rest_framework import generics
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.exceptions import NotFound

from django.conf import settings

import os
import shutil


class MediaServeView(generics.RetrieveUpdateAPIView):

    queryset = Attachment.objects.all()

    serializer_class = AttachmentFullSerializer

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/?error=download-file")

        path = kwargs.get('pk')
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        if settings.SETTING_TYPE is not settings.LOCAL:
            response['X-Accel-Redirect'] = os.path.join("/media_serve/", path)
        else:
            local_path = os.path.join(settings.MEDIA_ROOT, path)
            if not os.path.exists(local_path):
                raise NotFound
            with open(local_path, 'rb') as file:
                response.content = file

        return response

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/?error=download-file")
        if request.method == "PUT" and request.FILES is not None:
            # original_name = ((request.data['file_name'].replace(request.data['file_name'].split(".")[-1], "midi")).replace("_values","")).replace("_definitions","")
                with open(os.path.join(settings.MEDIA_ROOT,'temp/', kwargs['pk'], request.data['file_name']), 'wb+') as destination:
                    for chunk in request.FILES['files'].chunks():
                        destination.write(chunk)
                original_name = request.data['file_name']+'.midi'
                total_attachment = Attachment.objects.get(attachment=kwargs['pk']+original_name)
                if request.data['file_name'].split(".")[-1]=="xml":
                        if "_values" in request.data['file_name']:
                            total_attachment.attach_jsymbolic(request.data['file_path'], request.data['file_name'], request.FILES, 3)
                        else:
                            total_attachment.attach_jsymbolic(request.data['file_path'], request.data['file_name'], request.FILES,4)
                if request.data['file_name'].split(".")[-1]=="csv":
                        total_attachment.attach_jsymbolic(request.data['file_path'], request.data['file_name'], request.FILES, 1)
                if request.data['file_name'].split(".")[-1]=="arff":
                        total_attachment.attach_jsymbolic(request.data['file_path'], request.data['file_name'], request.FILES, 2)
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT,'temp/', kwargs['pk']))
                print(total_attachment)
                return HttpResponse(total_attachment)


