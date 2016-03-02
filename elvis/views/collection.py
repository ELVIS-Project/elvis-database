import ujson as json
import datetime
import pytz

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from elvis.forms.create import CollectionForm
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers import CollectionFullSerializer, CollectionListSerializer
from elvis.views.common import ElvisListCreateView, ElvisDetailView
from elvis.models import Collection, Piece, Movement


class CollectionListHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_list.html"


class CollectionDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_detail.html"


class CollectionCreateHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_create.html"


class CollectionUpdateHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_update.html"


class CollectionList(ElvisListCreateView):
    model = Collection
    serializer_class = CollectionListSerializer
    renderer_classes = (CollectionListHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        form = CollectionForm(request.POST)
        if not form.is_valid():
            data = json.dumps({"errors": form.errors})
            return HttpResponse(data, content_type="json",
                                status=status.HTTP_400_BAD_REQUEST)
        clean_form = form.cleaned_data
        new_collection = Collection(title=clean_form['title'],
                                    comment=clean_form['comment'],
                                    creator=request.user,
                                    created=datetime.datetime.now(pytz.utc),
                                    updated=datetime.datetime.now(pytz.utc))
        new_collection.save()
        if clean_form['permission'] == "Public":
            new_collection.public = True
        else:
            new_collection.public = False
        # If the collection is not empty, populate it from
        if not clean_form["initialize_empty"]:
            # Grab the pieces and movements from the cart
            pieces, movements = self.get_cart_pieces_and_movements(request)
            # Add the pieces and movements to the collection
            for piece in pieces:
                new_collection.pieces.add(piece)
            for movement in movements:
                new_collection.movements.add(movement)
        new_collection.save()
        return HttpResponseRedirect("/collection/{0}".format(new_collection.id))

    @staticmethod
    def get_cart_pieces_and_movements(request):
        """
        Get the pieces and movements currently in the cart.
        :param request:
        :return: Pieces and movements lists
        """
        pieces = []
        movements = []
        cart = request.session.get("cart", {})
        for key in cart:
            if key.startswith("P"):
                try:
                    tmp = Piece.objects.get(uuid=key[2:])
                except ObjectDoesNotExist:
                    continue
                pieces.append(tmp)
            if key.startswith("M"):
                try:
                    tmp = Movement.objects.get(uuid=key[2:])
                except ObjectDoesNotExist:
                    continue
                movements.append(tmp)
        return pieces, movements


class CollectionDetail(ElvisDetailView):
    model = Collection
    serializer_class = CollectionFullSerializer
    renderer_classes = (CollectionDetailHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

    def patch(self, request, *args, **kwargs):
        if self.determine_perms(request, *args, **kwargs)['can_edit']:
            return collection_update(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def determine_perms(self, request, *args, **kwargs):
        """
        Collections have curators, which introduces unique
        permission considerations.

        :param args:
        :param kwargs:
        :return:
        """
        if hasattr(request, "user") and request.user in Collection.objects.get(id=kwargs['pk']).curators.all():
            # The user is a curator, so they can view and edit
            return {"can_edit": True, "can_view": True}
        else:
            # The default inherited permission system
            return super().determine_perms(request, *args, **kwargs)


class CollectionCreate(generics.RetrieveAPIView):
    renderer_classes = (CollectionCreateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return Response(status=status.HTTP_200_OK)
        else:
            return HttpResponseRedirect('/login/?error=upload')


class CollectionUpdate(generics.RetrieveAPIView):
    serializer_class = CollectionFullSerializer
    renderer_classes = (CollectionUpdateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)
    queryset = Collection.objects.all()


def collection_update(request, *args, **kwargs):
    """
    Given a PATCH request, update a collection.

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    patch_data = request.data
    # Extract form data and validate
    form = CollectionForm(patch_data)
    if not form.is_valid():
        data = json.dumps({"errors": form.errors})
        return HttpResponse(content=data, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)
    # Update the collection
    collection = Collection.objects.get(id=int(kwargs['pk']))
    if "title" in patch_data:
        collection.title = patch_data["title"]
    if "permission" in patch_data:
        collection.public = patch_data["permission"] == "Public"
    if "comment" in patch_data:
        collection.comment = patch_data["comment"]
    collection.save()
    # Prepare a response
    data = json.dumps({'success': True, 'id': collection.id, 'url': "/collection/{0}".format(collection.id)})
    return HttpResponse(data, content_type="json")
