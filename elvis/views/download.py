from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from celery.result import AsyncResult
from elvis.elvis import tasks
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers import PieceEmbedSerializer, MovementEmbedSerializer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.collection import Collection
from elvis.models.composer import Composer
from django.core.cache import cache
import json

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
        p = PieceEmbedSerializer(tmp, context={'request': request}).data
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
        m = MovementEmbedSerializer(tmp, context={'request': request}).data
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
            cart["M-" + item['id']] = True
        elif elvis_type == "elvis_piece":
            cart["P-" + item['id']] = True
        elif elvis_type == "elvis_collection":
            cart["COL-" + item['id']] = True
            coll = Collection.objects.filter(id=item['id'])[0]
            for piece in coll.pieces.all():
                cart["P-" + str(piece.id)] = True
            for mov in coll.movements.all():
                parent = mov.piece
                if not parent or not cart.get("P-" + str(parent.id)):
                    cart["M-" + str(mov.id)] = True
        elif elvis_type == "elvis_composer":
            cart["COM-" + item['id']] = True
            comp = Composer.objects.filter(id=item['id'])[0]
            for piece in comp.pieces.all():
                cart["P-" + str(piece.id)] = True
            for mov in comp.movements.all():
                parent = mov.piece
                if not parent or not cart.get("P-" + str(parent.id)):
                    cart["M-" + str(mov.id)] = True

    def remove_item(self, item, cart):
        elvis_type = item.get('item_type')
        if elvis_type == "elvis_movement":
            cart.pop("M-" + item['id'], None)
        elif elvis_type == "elvis_piece":
            cart.pop("P-" + item['id'], None)
        elif elvis_type == "elvis_collection":
            cart.pop("COL-" + item['id'], None)
            coll = Collection.objects.filter(id=item['id'])[0]
            for piece in coll.pieces.all():
                cart.pop("P-" + str(piece.id), None)
            for mov in coll.movements.all():
                cart.pop("M-" + str(mov.id), None)
        elif elvis_type == "elvis_composer":
            cart.pop("COM-" + item['id'], None)
            comp = Composer.objects.filter(id=item['id'])[0]
            for piece in comp.pieces.all():
                cart.pop("P-" + str(piece.id), None)
            for mov in comp.movements.all():
                cart.pop("M-" + str(mov.id), None)

class Downloading(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer, DownloadingHTMLRenderer)

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

        if request.GET.get('extensions[]'):
            extensions = request.GET.getlist('extensions[]')
            tasks.zip_files(request, extensions)


        return Response(status=status.HTTP_200_OK)

