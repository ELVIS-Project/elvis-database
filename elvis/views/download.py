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
from elvis.helpers.cache_helper import *


class DownloadCartHTMLRenderer(CustomHTMLRenderer):
    template_name = "download/download_cart.html"


class DownloadCart(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (JSONRenderer, DownloadCartHTMLRenderer)

    def get(self, request, *args, **kwargs):
        """Serialize the items in the cart using the cache."""
        cart = ElvisCart(request)
        data = cart.serialize_cart_items(exts=True)
        return Response(data, *args, **kwargs)

    @method_decorator(csrf_protect)
    def post(self, request):
        """Preforms a number of cart-related functions.

        :param request: A django request. The action to take will be determined
        by the presences of a key at the top level of the POST dict.
        :return: A json response with the number of items in the cart.
        """

        cart = ElvisCart(request)

        if 'clear-collection' in request.POST:
            cart.clear()
            cart.save()
            jresults = json.dumps({'count': 0})
            return HttpResponse(content=jresults, content_type="application/json")
        elif 'check_in_cart' in request.POST:
            items = json.loads(request.POST['check_in_cart'])
            results = self._check_in_cart(cart, items)
            jresults = json.dumps(results)
            return HttpResponse(jresults, content_type="application/json")
        else:
            items = request.POST.get('items', [request.POST.dict()])
            return self._update_cart(cart, items)

    def _update_cart(self, cart, items):
        """Process a request to update the cart in some way.

        :param request: A django request, with updates which follow this API:

            {'action': ['remove'|'add'],
             'item_type': 'elvis_'['piece'|'movement'|'collection'|'composer'],
             }

        Or, if multiple updates are being sent, a list of updates in the
        preceding format may be sent in as 'items'.

        :return: JSON response with new number of items in cart.
        """
        for item in items:
            action = item.get('action')
            if action == 'add':
                cart.add_item(item)
            if action == 'remove':
                cart.remove_item(item)
        jresults = json.dumps({'count': len(cart)})
        cart.save()
        return HttpResponse(content=jresults, content_type="json")

    def _check_in_cart(self, cart, items):
        """Create dict of differences between frontend/backend cart.

        :param cart: The user's cart stored in request.session['cart'].
        :param items: A list of item's with the following format:
        [{'item_type': 'elvis_[type]', 'in_cart': bool, 'id':[uuid]}]
        :return: A dict in the same format (minus 'type' key as it is
        unnecessary) of only the pieces who's 'in_cart' status is different.
        """
        results = {}
        for item in items:
            if item['item_type'] == "elvis_movement":
                mov = try_get(item['id'], Movement)
                if mov.parent_cart_id in cart:
                    back = "Piece"
                else:
                    back = item in cart
            else:
                back = item in cart
            front = item['in_cart']
            if front == back:
                continue
            results[item['id']] = {"in_cart": back}
        return results


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
            make_dirs = request.GET.get('make_dirs')
            if make_dirs == 'false':
                make_dirs = False
            else:
                make_dirs = True
                
            cart = request.session.get("cart", {})
            task_id = str(uuid.uuid4())
            tasks.zip_files.apply_async(args=[cart, extensions, request.user.username, make_dirs], task_id=task_id)
            return Response({"task": task_id}, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

