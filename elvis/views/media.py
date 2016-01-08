from rest_framework import generics
from django.http import HttpResponse, HttpResponseRedirect
from elvis.models import Attachment

class MediaServeView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/?error=download-file")

        att = Attachment.objects.get(uuid=kwargs.get('pk'))
        if att:
            resp = HttpResponse(att.attachment, content_type='application/force-download')
            resp['Content-Disposition'] = 'attachment; filename=%s' % att.title
            return resp
