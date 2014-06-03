# LM: TODO lots of cleaning up
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer, JSONPRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from django.core.files import File
from django.core.servers.basehttp import FileWrapper

from celery.result import AsyncResult
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse

from django.template import RequestContext
from django.shortcuts import render_to_response
from elvis import tasks
import os, json

from time import sleep

import datetime

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.download import DownloadSerializer, DownloadingSerializer
from elvis.models.download import Download
from elvis.models.piece import Piece
from elvis.models.movement import Movement

from django.core.exceptions import ObjectDoesNotExist

class DownloadListHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download_list.html"


class DownloadDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download.html"

class DownloadingHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/downloading.html"

class DownloadList(generics.ListCreateAPIView):
    model = Download
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DownloadSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, DownloadListHTMLRenderer)

    def get_queryset(self):
        user = self.request.user
        return Download.objects.filter(user=user)


class DownloadDetail(generics.RetrieveUpdateAPIView):
    model = Download
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DownloadSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, DownloadDetailHTMLRenderer)

    def get_object(self):
        user = self.request.user
        
        try:
            obj = Download.objects.filter(user=user).latest("created")
            return obj
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # print("I AM BEING PATCHED");
        itype = request.DATA.get("type", None)
        item_id = request.DATA.get('item_id', None)

        if itype not in ('piece', 'movement'):
            return Response({'message': "You must supply either piece or movement"}, status=status.HTTP_400_BAD_REQUEST)

        if itype == 'piece':
            obj = Piece.objects.get(pk=item_id)
        elif itype == 'movement':
            obj = Movement.objects.get(pk=item_id)

        if not obj:
            return Response({'message': "The item with id {0} was not found".format(item_id)}, status=status.HTTP_404_NOT_FOUND)
       
        dlobj = self.get_object()
        
        for attachment in obj.attachments.all():
            dlobj.attachments.add(attachment)

        d = DownloadSerializer(dlobj).data
        return Response(d)

        # return self.partial_update(request, *args, **kwargs)

# LM: New view 2, was original view but updated with post-only view below
class Downloading(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DownloadingSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, DownloadingHTMLRenderer)
        
        # LM: Things needed:
        # 1. Parse request to extract path to all requested files
        # 2. Create subprocess - Celery
        # 3. Get files and copy into dummy directory
        # 4. Zip directory
        # 5. Track subprocess
        # 6. Serve
        # 7. Remove dummy directory and zipped file - do this daily
        # 

    def get(self, request, *args, **kwargs):
        """ A view to report the progress to the user """
        if 'task' in request.GET:
            task_id = request.GET['task']
        else:
            # TODO change to appropriate response type
            return Response({"None" : "None"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            task = AsyncResult(task_id)
        except Exception:
            return Response({"None" : "None"}, status=status.HTTP_400_BAD_REQUEST)

        if task.result and hasattr(task, 'result') and "path" in task.result:
            path = task.result["path"]
            #print('path', path)
            file_name = os.path.basename(path)
            #print('file_name', file_name)
        ##    zipped_file = File(open(path, "r"))
            #response = Response(task.result, status=status.HTTP_200_OK)
            try:
                # Doesn't work with Response for some reason, even though it works in the console. Has to be HttpResponse 
                response = HttpResponse(FileWrapper(file(path, "r")), content_type='application/zip')
            except Exception as e:
                print e
            
            response["Content-Length"] = os.path.getsize(path)
            #print("Content-Length", os.path.getsize(path)) 
            response["Content-Disposition"] = 'attachment; filename=%s' % file_name
            #print("Content-Disposition", 'attachment; filename=%s' %file_name)

            # to detect the download, set a cookie for an hour
            cookie_age = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=3600), "%a, %d-%b-%Y %H:%M:%S GMT")
            response.set_cookie(task_id, "downloading", max_age=600, expires=cookie_age, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)  
            
            return response
        
        data = task.result or task.state
        #print data
        return Response(data, status=status.HTTP_200_OK)


    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        c = {}

        # LM TODO cleanup

        #print(request)

        items = request.POST.getlist('item')
        #print('items', items)

        extensions = request.POST.getlist('extension')
        #print('types', types)

        others_check = False
        
        if '.midi' in extensions:
            extensions.append('.mid')
        if '.xml' in extensions:
            extensions.append('.mxl')
        if 'OTHERS' in extensions:
            others_check = True

        print('extensions', extensions)


        # If user checks all exts except .abc, he would expect everything else but .abc
        # -> need a list of everything that could have been left unchecked
        # EDIT IF download.html IS CHANGED
        default_exts = ['.mei', '.xml', '.midi', '.pdf', '.krn', '.mid', '.mxl']

        #print('default_exts', default_exts)

        # Check for two conditions. Either:
        # 1) requested file is in selected extensions
        # 2) file is not in available extensions (i.e. its extension was not rejected) and OTHERS was checked
        files = []
        for item in items:
            fileName, fileExt = os.path.splitext(item)
            print(fileExt)
            if (fileExt in extensions):
                files.append(item)
            elif((not (fileExt in default_exts)) and others_check):
                files.append(item)
                print 'appended'
            else:
                pass

        print('files', files)

        #print('user', request.user.username)

        # Call celery tasks with our parsed files
        zip_task = tasks.zip_files.delay(files, request.user.username)
        #zip_status = tasks.zip_status_check.delay(zip_task.id)
        #print('zip_task', zip_task, type(zip_task))
        #print('ready', zip_task.ready())
        #print('get', zip_task.get(timeout=None, propagate=True, interval=0.5, no_ack=True, follow_parents=True))

        #c.update(csrf(request))
        return HttpResponseRedirect('?task=' + zip_task.id)
        #return render_to_response("download/downloading.html", RequestContext(request, {}))







