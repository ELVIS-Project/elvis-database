# LM: TODO lots of cleaning up; make modular methods
import json
import os
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from celery.result import AsyncResult
from elvis.elvis import tasks
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.download import DownloadingSerializer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.attachment import Attachment
from elvis.models.collection import Collection
from elvis.models.composer import Composer
from elvis.serializers.download import DownloadPieceSerializer, DownloadMovementSerializer
from django.core.cache import cache

class DownloadListHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download_list.html"


class DownloadCartHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download_cart.html"


class DownloadingHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/downloading.html"


class DownloadCart(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer, DownloadCartHTMLRenderer)

    def get(self, request, *args, **kwargs):
        if 'check_in_cart' in request.GET:
            results = self._check_in_cart(request)
            jresults = json.dumps(results)
            return HttpResponse(jresults, content_type="application/json")

        data = self.make_cart_response(request)
        return Response(data, *args, **kwargs)

    def make_cart_response(self, request):
        cart = request.session.get('cart', {})
        data = {"pieces": [], "movements": []}
        for key in cart.keys():
            if key.startswith("P"):
                data['pieces'].append(self.retrieve_piece(key, request))
            if key.startswith("M"):
                data['movements'].append(self.retrieve_movement(key, request))
        return data

    def retrieve_piece(self, pid, request):
        """Use cache to speed up retrieving use cart contents.

        :param pid: The id stored in the session for carts (P-[numbers])
        :param request: The request object (for serialization)
        :return: A serialized dict representing the Piece.
        """
        p = cache.get("cart-" + pid)
        if p:
            return p
        tmp = Piece.objects.get(id=pid[2:])
        p = DownloadPieceSerializer(tmp, context={'request': request}).data
        cache.set("cart-" + pid, p, timeout=None)
        return p

    def retrieve_movement(self, mid, request):
        """Use cache to speed up retrieving use cart contents.

        :param pid: The id stored in the session for carts (M-[numbers])
        :param request: The request object (for serialization)
        :return: A serialized dict representing the Movement.
        """
        m = cache.get("cart-" + mid)
        if m:
            return m
        tmp = Movement.objects.get(id=mid[2:])
        m = DownloadMovementSerializer(tmp, context={'request': request}).data
        cache.set("cart-" + mid, m, timeout=None)
        return m


    def _check_in_cart(self, request):
        item_list = json.loads(request.GET['check_in_cart'])
        cart = request.session.get('cart', {})
        results = []
        for item in item_list:
            if item['type'] == "elvis_composer":
                if cart.get("COM-" + item['id']):
                    results.append({'id': item['id'], 'in_cart': True})
                else:
                    results.append({'id': item['id'], 'in_cart': False})
                continue
            if item['type'] == "elvis_collection":
                if cart.get("COL-" + item['id']):
                    results.append({'id': item['id'], 'in_cart': True})
                else:
                    results.append({'id': item['id'], 'in_cart': False})
                continue
            if item['type'] == "elvis_piece":
                if cart.get("P-" + item['id']):
                    results.append({'id': item['id'], 'in_cart': True})
                else:
                    results.append({'id': item['id'], 'in_cart': False})
                continue
            if item['type'] == "elvis_movement":
                piece = Movement.objects.get(pk=item['id']).piece
                if piece and cart.get("P-" + item['id']):
                    results.append({'id': item['id'], 'in_cart': 'Piece'})
                elif cart.get("M-" + item['id']):
                    results.append({'id': item['id'], 'in_cart': True})
                else:
                    results.append({'id': item['id'], 'in_cart': False})
        return results

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if 'clear-collection' in request.POST:
            user_download = request.user.downloads.all()[0]
            user_download.attachments.clear()
            user_download.collection_movements.clear()
            user_download.collection_pieces.clear()
            user_download.collection_collections.clear()
            user_download.collection_composers.clear()
            user_download.save()
            request.session.pop('cart', None)
            jresults = json.dumps({'count': 0})
            return HttpResponse(content=jresults, content_type="json")
        else:
            return self.update_cart(request)

    def update_cart(self, request):
        cart = request.session.get('cart', {})
        items = request.POST.get('items', [])
        for item in items:
            action = item.get('action')
            if action == 'add':
                self.add_item(item, cart)
            if action == 'remove':
                self.remove_item(item, cart)

        action = request.POST.get('action')
        if action == 'add':
            self.add_item(request.POST, cart)
        elif action == 'remove':
            self.remove_item(request.POST, cart)

        request.session['cart'] = cart
        jresults = json.dumps({'count': len(cart)})
        return HttpResponse(content=jresults, content_type="json")

    def add_item(self, item, cart):
        elvis_type = item.get('item_type')
        if elvis_type == "elvis_movement":
            cart["M-" + item['item_id']] = True
        elif elvis_type == "elvis_piece":
            cart["P-" + item['item_id']] = True
        elif elvis_type == "elvis_collection":
            cart["COL-" + item['item_id']] = True
            coll = Collection.objects.filter(id=item['item_id'])[0]
            for piece in coll.pieces.all():
                cart["P-" + str(piece.id)] = True
            for mov in coll.movements.all():
                parent = mov.piece
                if not parent or not cart.get("P-" + str(parent.id)):
                    cart["M-" + str(mov.id)] = True
        elif elvis_type == "elvis_composer":
            cart["COM-" + item['item_id']] = True
            comp = Composer.objects.filter(id=item['item_id'])[0]
            for piece in comp.pieces.all():
                cart["P-" + str(piece.id)] = True
            for mov in comp.movements.all():
                parent = mov.piece
                if not parent or not cart.get("P-" + str(parent.id)):
                    cart["M-" + str(mov.id)] = True

    def remove_item(self, item, cart):
        elvis_type = item.get('item_type')
        if elvis_type == "elvis_movement":
            cart.pop("M-" + item['item_id'], None)
        elif elvis_type == "elvis_piece":
            cart.pop("P-" + item['item_id'], None)
        elif elvis_type == "elvis_collection":
            cart.pop("COL-" + item['item_id'], None)
            coll = Collection.objects.filter(id=item['item_id'])[0]
            for piece in coll.pieces.all():
                cart.pop("P-" + str(piece.id), None)
            for mov in coll.movements.all():
                cart.pop("M-" + str(mov.id), None)
        elif elvis_type == "elvis_composer":
            cart.pop("COM-" + item['item_id'], None)
            comp = Composer.objects.filter(id=item['item_id'])[0]
            for piece in comp.pieces.all():
                cart.pop("P-" + str(piece.id), None)
            for mov in comp.movements.all():
                cart.pop("M-" + str(mov.id), None)

# LM: New view 2, was original view but updated with post-only view below
class Downloading(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DownloadingSerializer
    renderer_classes = (JSONRenderer, DownloadingHTMLRenderer)

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
        if request.GET.get('format') == 'json' and request.GET.get('task'):
            try:
                task_id = request.GET['task']
                task = AsyncResult(task_id)
                if task.ready():
                    return Response(
                        {'ready': task.ready(), 'state': task.status, 'path': task.result['path'], 'info': task.info})
                else:
                    return Response({'ready': task.ready(), 'state': task.status, 'info': task.info})
            except Exception:
                return Response({'state': "FAILED"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

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
        elif 'remove-selected' in request.POST:
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

            return HttpResponseRedirect('/download-cart/')

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

            return HttpResponseRedirect('/download-cart/')


def ranked_remover(parent, user_download):
    # Create a ranking for the attachments based on ELVIS_EXTENSIONS
    # Find the best sibling attachment to keep
    # Remove the sibling if its file type isn't supported
    # Else, add it to the ranking list in the right location 
    ranking_list = [None] * len(settings.ELVIS_EXTENSIONS)
    for sibling_a in parent.attachments.all():
        fileName, fileExt = os.path.splitext(sibling_a.file_name)
        if not fileExt in settings.ELVIS_EXTENSIONS:
            user_download.attachments.remove(sibling_a)
        else:
            # To handle repeat file types... which there shouldnt be
            try:
                ranking_list.insert(settings.ELVIS_EXTENSIONS.index(fileExt), sibling_a)
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
