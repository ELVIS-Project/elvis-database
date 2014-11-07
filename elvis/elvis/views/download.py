# LM: TODO lots of cleaning up; make modular methods
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
from elvis.models.attachment import Attachment
from elvis.models.collection import Collection
from elvis.models.tag import Tag
from elvis.models.composer import Composer

from elvis.helpers.solrsearch import SolrSearch

from django.core.exceptions import ObjectDoesNotExist

from elvis.settings import ELVIS_EXTENSIONS

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
    permission_classes = (permissions.IsAuthenticated,)
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

    # Method to alter user's download object based on a singular attachment id
    def _patch_downloads(self, request):
        if not request.user.is_authenticated():
            raise Http404
        user_download = request.user.downloads.all()[0]
        add_attachments = request.POST.getlist('a_ids')

        #add_attachments is a list of ids
        for a in add_attachments:
            a_object = Attachment.objects.filter(pk=a).all()[0]
            user_download.attachments.add(a_object)

        user_download.save()
        return HttpResponseRedirect(request.POST.get('this_url'))

    # Method to help recursive-alteration of user's download object
    def _download_helper(self, item, user_download):
        if hasattr(item, 'attachments') and not item.attachments is None:
            for a_object in item.attachments.all():
                user_download.attachments.add(a_object)
            user_download.save()
        if hasattr(item, 'pieces') and not item.pieces is None:
            for piece in item.pieces.all():
                self._download_helper(piece, user_download)
        if hasattr(item, 'movements') and not item.movements is None:
            for movement in item.movements.all():
                self._download_helper(movement, user_download)

    # Choose the right model based on request, again to help recursive-patching
    def _type_selector(self, item_type, item_id, user_download):
        if item_type == "elvis_movement":
            item = Movement.objects.filter(pk=item_id).all()[0]
        elif item_type == "elvis_piece":
            item = Piece.objects.filter(pk=item_id).all()[0]
        elif item_type == "elvis_composer":
            item = Composer.objects.filter(pk=item_id).all()[0]
        elif item_type == "elvis_collection":
            item = Collection.objects.filter(pk=item_id).all()[0]
        elif item_type == "elvis_tag":
            item = Tag.objects.filter(pk=item_id).all()[0]
        else:
            raise TypeError("Item type '"+ item_type +"' passed not found in database.")

        self._download_helper(item, user_download)

    # Recursive version of the flat-downloads
    def _recursive_patch_downloads(self, request):
        if not request.user.is_authenticated:
            raise Http404
        user_download = request.user.downloads.all()[0]
        this_url = request.POST.get('this_url')

        # If we are saving all the attachments in the search results
        if request.POST.get("search_query"):
            from django.test.client import RequestFactory
            # Make a dummy get request (because we're requerying without pagination)
            dummy_request = RequestFactory().get(request.POST.get("search_query") + "&rows=20000000")
            s = SolrSearch(dummy_request)
            search_results = s.search()
            for result in search_results.results:
                self._type_selector(result.get("type"), result.get("item_id"), user_download)
        else:
            item_type = request.POST.getlist('item_type')
            item_id = request.POST.getlist('item_id')
            for i in range(len(item_type)):
                self._type_selector(item_type[i], item_id[i], user_download)
            
        return HttpResponseRedirect(this_url)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        # If attachment ids are sent in via request, then add attachments to downloads
        # Else recursively add all children attachments to downloads
        if request.POST.get('a_ids'):
            return self._patch_downloads(request)
        return self._recursive_patch_downloads(request)

# LM: New view 2, was original view but updated with post-only view below
class Downloading(APIView):
    permission_classes = (permissions.IsAuthenticated,)
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

    def get(self, request, *args, **kwargs):
        """ A view to report the progress to the user """
        try:
            task_id = request.GET['task']
            task = AsyncResult(task_id)
        except Exception:
            return Response({"None" : "None"}, status=status.HTTP_400_BAD_REQUEST)

        if "path" in task.result and 'service' in request.GET:
            path = task.result["path"]
            file_name = os.path.basename(path)
            response = HttpResponse(FileWrapper(file(path, "r")), content_type='application/zip')
            # Required for download responses 
            response["Content-Length"] = os.path.getsize(path)
            response["Content-Disposition"] = 'attachment; filename=%s' % file_name
            return response
        elif "path" in task.result:
            # to detect the download, set a cookie for an hour
            response = Response({"None" : "None"}, status=status.HTTP_200_OK)
            cookie_age = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=3600), "%a, %d-%b-%Y %H:%M:%S GMT")
            response.set_cookie(task_id, "downloading", max_age=600, expires=cookie_age, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)  
            return response
        
        data = task.info
        return Response(data, status=status.HTTP_200_OK)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        # Download selected
        if 'download-all' in request.POST:
            # get attachment ids 
            a_ids = request.POST.getlist('a_ids')

            items = []
            for a_id in a_ids:
                a_object = Attachment.objects.filter(pk=a_id).all()[0]
                a_path = os.path.join(a_object.attachment_path, a_object.file_name)

                items.append(a_path)

            # get checked extensions, add in equivalent extensions
            extensions = request.POST.getlist('extension')

            others_check = False
            
            if '.midi' in extensions:
                extensions.append('.mid')
            if '.xml' in extensions:
                extensions.append('.mxl')
            if 'OTHERS' in extensions:
                others_check = True


            # If user checks all exts except .abc, he would expect everything else but .abc
            # -> need a list of everything that could have been left unchecked
            # EDIT IF download.html IS CHANGED
            default_exts = ['.mei', '.xml', '.midi', '.pdf', '.krn', '.mid', '.mxl']

            # Check for two conditions. Either:
            # 1) requested file is in selected extensions
            # 2) file is not in available extensions (i.e. its extension was not rejected) and OTHERS was checked
            files = []
            for item in items:
                fileName, fileExt = os.path.splitext(item)
                if ((fileExt in extensions) or ((not (fileExt in default_exts)) and others_check)):
                    files.append(item)

            # Call celery tasks with our parsed files
            zip_task = tasks.zip_files.delay(files, request.user.username)


            return HttpResponseRedirect('?task=' + zip_task.id)

        # Remove selected
        elif 'remove-all' in request.POST:
            # get ids
            a_ids = request.POST.getlist('a_ids')
            # get user
            user_download = request.user.downloads.all()[0]
            # get extensions
            extensions = request.POST.getlist('extension')

            # do the extensions thing above
            others_check = False
            
            if '.midi' in extensions:
                extensions.append('.mid')
            if '.xml' in extensions:
                extensions.append('.mxl')
            if 'OTHERS' in extensions:
                others_check = True

            default_exts = ['.mei', '.xml', '.midi', '.pdf', '.krn', '.mid', '.mxl']

            for a_id in a_ids:
                a_object = Attachment.objects.filter(pk=a_id).all()[0]
                fileName, fileExt = os.path.splitext(a_object.file_name)
                if ((fileExt in extensions) or ((not (fileExt in default_exts)) and others_check)):
                    user_download.attachments.remove(a_object)

            return HttpResponseRedirect('/downloads/')

        # Optimize user downloads to contain the best file format for elvis
        elif 'select-elvis' in request.POST:
            user_download = request.user.downloads.all()[0]

            # Do this for all the attachments in the user's downloads cart
            for a_object in user_download.attachments.all():
                try:
                    parent_p = a_object.pieces.all()[0]
                    ranked_remover(parent_p, user_download)
                except Exception as e:
                    parent_p = None
                try:
                    parent_m = a_object.movements.all()[0]
                    ranked_remover(parent_m, user_download)
                except Exception as e:
                    parent_m = None
                    
            return HttpResponseRedirect('/downloads/')


            
def ranked_remover(parent, user_download):
    # Create a ranking for the attachments based on ELVIS_EXTENSIONS
    # Find the best sibling attachment to keep
    # Remove the sibling if its file type isn't supported
    # Else, add it to the ranking list in the right location 
    ranking_list = [None] * len(ELVIS_EXTENSIONS)
    for sibling_a in parent.attachments.all():
        fileName, fileExt = os.path.splitext(sibling_a.file_name)
        if not fileExt in ELVIS_EXTENSIONS:
            user_download.attachments.remove(sibling_a)
        else:
            # To handle repeat file types... which there shouldnt be
            try:
                ranking_list.insert(ELVIS_EXTENSIONS.index(fileExt), sibling_a)
            except Exception:
                ranking_list.append(sibling_a)
    # Now, go through the ranking list and insert the first sibling attachment into the user's downloads.
    # Remove all the other sibling attachments
    chosen_a_file = False
    for sibling_a in ranking_list:
        if sibling_a is None:
            continue
        elif chosen_a_file is False:
            chosen_a_file = True
            user_download.attachments.add(sibling_a)
        else:
            user_download.attachments.remove(sibling_a)




