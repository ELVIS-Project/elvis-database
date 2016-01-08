import json

from celery.result import AsyncResult
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from elvis import tasks
from elvis.models.collection import Collection
from elvis.models.composer import Composer
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers import PieceEmbedSerializer, MovementEmbedSerializer
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from collections import defaultdict
import uuid
from django.core.exceptions import ObjectDoesNotExist


class DownloadCartHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download_cart.html"


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
        cart_copy = cart.copy()
        data = {"pieces": [], "movements": []}
        ext_count = defaultdict(int)
        for key in cart_copy.keys():
            if key.startswith("P"):
                tmp = self._retrieve_piece(key, request, ext_count)
                if tmp:
                    data['pieces'].append(tmp)
            if key.startswith("M"):
                tmp = self._retrieve_movement(key, request, ext_count)
                if tmp:
                    data['movements'].append(tmp)

        ext_list = [{"extension":k, 'count':v} for k,v in ext_count.items() if k is not "total"]
        data['extension_counts'] = ext_list
        data['attachment_count'] = ext_count['total']
        return data

    def _retrieve_piece(self, pid, request, exts):
        """Use cache to speed up retrieving use cart contents.

        :param pid: The id stored in the session for carts (P-[numbers])
        :param request: The request object (for serialization)
        :return: A serialized dict representing the Piece.
        """
        p_uuid = pid[2:]
        p = cache.get("EMB-" + p_uuid)
        if not p:
            tmp = self._try_get(Piece, p_uuid)
            if not tmp:
                del(request.session['cart'][pid])
                return None
            p = PieceEmbedSerializer(tmp, context={'request': request}).data
            cache.set("EMB-" + p_uuid, p)

        for a in p['attachments']:
            exts[a['extension']] += 1
            exts['total'] += 1

        for m in p['movements']:
            for a in m['attachments']:
                exts[a['extension']] += 1
                exts['total'] += 1

        return p

    def _retrieve_movement(self, mid, request, exts):
        """Use cache to speed up retrieving use cart contents.

        :param pid: The id stored in the session for carts (M-[numbers])
        :param request: The request object (for serialization)
        :return: A serialized dict representing the Movement.
        """
        m_uuid = mid[2:]
        m = cache.get("EMB-" + m_uuid)
        if not m:
            tmp = self._try_get(Movement, m_uuid)
            if not tmp:
                del(request.session['cart'][mid])
                return None
            m = MovementEmbedSerializer(tmp, context={'request': request}).data
            cache.set("EMB-" + m_uuid, m)

        for a in m['attachments']:
            exts[a['extension']] += 1
            exts['total'] += 1

        return m

    def _try_get(self, model, obj_id):
        """ Tries to get an object out of the database. Returns None if
        the object no longer exists. It is the caller's responsibility to
        handle this situation."""
        tmp = None
        try:
            tmp = model.objects.get(uuid=obj_id)
        except ObjectDoesNotExist:
            pass
        return tmp

    def _check_in_cart(self, request):
        items = json.loads(request.GET['check_in_cart'])
        cart = request.session.get('cart', {})
        results = {}
        for key in items.keys():
            if items[key]['type'] == "elvis_composer":
                back = cart.get("COM-" + key, False)
            elif items[key]['type'] == "elvis_collection":
                back = cart.get("COL-" + key, False)
            elif items[key]['type'] == "elvis_piece":
                back = cart.get("P-" + key, False)
            elif items[key]['type'] == "elvis_movement":
                mov = self._try_get(Movement, key)
                if mov and cart.get(mov.parent_cart_id, False):
                    back = "Piece"
                else:
                    back = cart.get("M-" + key, False)
            front = items[key]['in_cart']
            if front == back:
                continue
            results[key] = {"in_cart": back}
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
            item_type = item.get('item_type')
            item_uuid = item.get('id')
            action = item.get('action')
            if action == 'add':
                self.add_item(item_type, item_uuid, cart)
            if action == 'remove':
                self.remove_item(item_type, item_uuid, cart)

        item_type = request.POST.get('item_type')
        item_uuid = request.POST.get('id')
        action = request.POST.get('action')
        if action == 'add':
            self.add_item(item_type, item_uuid, cart)
        if action == 'remove':
            self.remove_item(item_type, item_uuid, cart)

        request.session['cart'] = cart
        jresults = json.dumps({'count': len(cart)})
        return HttpResponse(content=jresults, content_type="json")

    def add_item(self, item_type, item_uuid, cart):
        if item_type == "elvis_movement":
            cart["M-" + item_uuid] = True
        elif item_type == "elvis_piece":
            cart["P-" + item_uuid] = True
            piece = self._try_get(Piece, item_uuid)
            if piece:
                for mov in piece.movements.all():
                    self.remove_item("elvis_movement", str(mov.uuid), cart)
        elif item_type == "elvis_collection":
            cart["COL-" + item_uuid] = True
            coll = Collection.objects.filter(uuid=item_uuid)[0]
            for piece in coll.pieces.all():
                cart["P-" + str(piece.uuid)] = True
            for mov in coll.movements.all():
                parent = mov.piece
                if not parent or not cart.get("P-" + str(parent.uuid)):
                    cart["M-" + str(mov.uuid)] = True
        elif item_type == "elvis_composer":
            cart["COM-" + item_uuid] = True
            comp = Composer.objects.filter(uuid=item_uuid)[0]
            for piece in comp.pieces.all():
                cart["P-" + str(piece.uuid)] = True
            for mov in comp.movements.all():
                parent = mov.piece
                if not parent or not cart.get("P-" + str(parent.uuid)):
                    cart["M-" + str(mov.uuid)] = True

    def remove_item(self, item_type, item_uuid, cart):
        if item_type == "elvis_movement":
            cart.pop("M-" + item_uuid, None)
        elif item_type == "elvis_piece":
            cart.pop("P-" + item_uuid, None)
            piece = self._try_get(Piece, item_uuid)
            if piece:
                for mov in piece.movements.all():
                    self.remove_item("elvis_movement", str(mov.uuid), cart)
        elif item_type == "elvis_collection":
            cart.pop("COL-" + item_uuid, None)
            coll = Collection.objects.filter(uuid=item_uuid)[0]
            for piece in coll.pieces.all():
                cart.pop("P-" + str(piece.uuid), None)
            for mov in coll.movements.all():
                cart.pop("M-" + str(mov.uuid), None)
        elif item_type == "elvis_composer":
            cart.pop("COM-" + item_uuid, None)
            comp = Composer.objects.filter(uuid=item_uuid)[0]
            for piece in comp.pieces.all():
                cart.pop("P-" + str(piece.uuid), None)
            for mov in comp.movements.all():
                cart.pop("M-" + str(mov.uuid), None)


class Downloading(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if request.GET.get('task'):
            task_id = request.GET['task']
            task = AsyncResult(task_id)
            if task.status == "PENDING":
                return Response({'ready': task.ready(), 'status': task.status, 'progress': 0})
            elif task.status == "SUCCESS":
                return Response({'ready': task.ready(), 'status': "SUCCESS", 'progress': 100, 'path': task.result})
            elif task.state == "FAILURE":
                return Response({'ready': task.ready(), 'status': "FAILURE"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                meta = task._get_task_meta()
                progress = meta.get('result', {}).get('progress', 0)
                return Response({'ready': task.ready(), 'progress': progress, 'status': "PROGRESS"})

        if request.GET.get('extensions[]'):
            extensions = request.GET.getlist('extensions[]')
            cart = request.session.get("cart", {})
            task_id = str(uuid.uuid4())
            tasks.zip_files.apply_async(args=[cart, extensions, request.user.username], task_id=task_id)
            return Response({"task": task_id}, status=status.HTTP_200_OK)


        return Response(status=status.HTTP_200_OK)

