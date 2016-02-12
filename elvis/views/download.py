import ujson as json
import uuid

from celery.result import AsyncResult
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from elvis import tasks
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from rest_framework import generics, permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from collections import Counter
from elvis.helpers.cache_helper import *


class DownloadCartHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download_cart.html"


def _check_in_cart(cart, items):
    """Create dict of differences between frontend/backend cart.

    :param cart: The user's cart stored in request.session['cart'].
    :param items: A dict of item's with the following format:
    {[uuid]:{'type': 'elvis_[type]', 'in_cart': bool}
    :return: A dict in the same format (minus 'type' key as it is
    unnecessary) of only the pieces who's 'in_cart' status is different.
    """
    results = {}
    for key in items.keys():
        if items[key]['type'] == "elvis_composer":
            back = cart.get("COM-" + key, False)
        elif items[key]['type'] == "elvis_collection":
            back = cart.get("COL-" + key, False)
        elif items[key]['type'] == "elvis_piece":
            back = cart.get("P-" + key, False)
        elif items[key]['type'] == "elvis_movement":
            mov = try_get(key, Movement)
            if mov and cart.get(mov.parent_cart_id, False):
                back = "Piece"
            else:
                back = cart.get("M-" + key, False)
        front = items[key]['in_cart']
        if front == back:
            continue
        results[key] = {"in_cart": back}
    return results


def remove_item(item_type, item_uuid, cart):
    """Remove item from a cart.

    :param item_type:
    :param item_uuid:
    :param cart:
    :return:
    """
    if item_type == "elvis_movement":
        cart.pop("M-" + item_uuid, None)
    elif item_type == "elvis_piece":
        cart.pop("P-" + item_uuid, None)
        piece = try_get(item_uuid, Piece)
        if piece:
            for mov in piece.movements.all():
                remove_item("elvis_movement", str(mov.uuid), cart)
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

    return cart


def add_item(item_type, item_uuid, cart):
    """Add item to a cart.

    :param item_type:
    :param item_uuid:
    :param cart:
    :return:
    """
    if item_type == "elvis_movement":
        cart["M-" + item_uuid] = True
    elif item_type == "elvis_piece":
        cart["P-" + item_uuid] = True
        piece = try_get(item_uuid, Piece)
        if piece:
            for mov in piece.movements.all():
                remove_item("elvis_movement", str(mov.uuid), cart)
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


def _append_ext_count(result, exts):
    """Append count of extensions of files related to the serialized item.

    :param result: A serialized object.
    :param exts: The dict of extensions being built.
    """
    if result.get('attachments'):
        for a in result['attachments']:
            exts[a['extension']] += 1
            exts['total'] += 1

    if result.get('movements'):
        for m in result['movements']:
            _append_ext_count(m, exts)


def get_ext_counts(cart_items):
    """Count the number of attachments with each extension currently in cart.

    :param cart_items: The dict produced by serialize_cart_items.
    :return: A Counter with the counts of different extension types.
    """
    c = Counter()
    for item in cart_items['pieces']:
        _append_ext_count(item, c)
    for item in cart_items['movements']:
        _append_ext_count(item, c)
    return c


class DownloadCart(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer, DownloadCartHTMLRenderer)

    def get(self, request, *args, **kwargs):
        """Serialize the items in the cart using the cache."""

        data = self.serialize_cart_items(request)
        ext_count = get_ext_counts(data)
        ext_list = [{"extension": k, 'count': v} for k, v in ext_count.items() if k is not "total"]
        data['extension_counts'] = ext_list
        data['attachment_count'] = ext_count['total']
        return Response(data, *args, **kwargs)

    @staticmethod
    def serialize_cart_items(request):
        cart = request.session.get('cart', {})
        cart_copy = cart.copy()
        data = {"pieces": [], "movements": []}
        for key in cart_copy.keys():
            tmp, model = retrieve_object(key, request)
            if tmp and model == Piece:
                data['pieces'].append(tmp)
            if tmp and model == Movement:
                data['movements'].append(tmp)

        return data

    @method_decorator(csrf_protect)
    def post(self, request):
        """Preforms a number of cart-related functions.

        :param request: A django request. The action to take will be determined
        by the presences of a key at the top level of the POST dict.
        :return: A json response with the number of items in the cart.
        """
        if 'clear-collection' in request.POST:
            request.session.pop('cart', None)
            jresults = json.dumps({'count': 0})
            return HttpResponse(content=jresults, content_type="application/json")
        elif 'check_in_cart' in request.POST:
            cart = request.session.get('cart', {})
            items = json.loads(request.POST['check_in_cart'])
            results = _check_in_cart(cart, items)
            jresults = json.dumps(results)
            return HttpResponse(jresults, content_type="application/json")
        elif 'get_ext_count' in request.POST:
            cart_items = self.serialize_cart_items(request)
            ext_count = get_ext_counts(cart_items)
            jresults = json.dumps(ext_count)
            return HttpResponse(jresults, content_type="application/json")
        else:
            return self.update_cart(request)

    @staticmethod
    def update_cart(request):
        """Process a request to update the cart in some way.

        :param request: A django request, with updates which follow this API:

            {'action': ['remove'|'add'],
             'id': [UUID],
             'item_type': 'elvis_'['piece'|'movement'|'collection'|'composer'],
             }

        Or, if multiple updates are being sent, a list of updates in the
        preceding format may be sent in as 'items'.

        :return: JSON response with new number of items in cart.
        """
        cart = request.session.get('cart', {})
        items = request.POST.get('items', [request.POST])
        for item in items:
            item_type = item.get('item_type')
            item_uuid = item.get('id')
            action = item.get('action')
            if action == 'add':
                add_item(item_type, item_uuid, cart)
            if action == 'remove':
                remove_item(item_type, item_uuid, cart)

        request.session['cart'] = cart
        jresults = json.dumps({'count': len(cart)})
        return HttpResponse(content=jresults, content_type="json")


class Downloading(generics.GenericAPIView):
    """Create and report on status of cart-zipping tasks."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """Start or report on a cart-zipping task.

        This method is expecting one of two possible query parameters:
            task=[uuid]: Return information on the status of a
            cart zipping task, including a path to download the zip
            if it is done.

            extensions[]: Start a new cart-zipping task for the requesting
            user. Return a task_id, which can be used in the above query.
        """
        if request.GET.get('task'):
            task_id = request.GET['task']
            task = AsyncResult(task_id)

            if task.status == "PENDING":
                return Response({'ready': task.ready(),
                                 'status': task.status,
                                 'progress': 0})

            elif task.status == "SUCCESS":
                return Response({'ready': task.ready(),
                                 'status': "SUCCESS",
                                 'progress': 100,
                                 'path': task.result})

            elif task.state == "FAILURE":
                server_error = status.HTTP_500_INTERNAL_SERVER_ERROR
                return Response({'ready': task.ready(),
                                 'status': "FAILURE"}, status=server_error)

            else:
                meta = task._get_task_meta()
                progress = meta.get('result', {}).get('progress', 0)
                return Response({'ready': task.ready(),
                                 'progress': progress,
                                 'status': "PROGRESS"})

        if request.GET.get('extensions[]'):
            extensions = request.GET.getlist('extensions[]')
            cart = request.session.get("cart", {})
            task_id = str(uuid.uuid4())
            tasks.zip_files.apply_async(args=[cart, extensions, request.user.username], task_id=task_id)
            return Response({"task": task_id}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

