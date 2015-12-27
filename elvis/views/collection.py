import json
import datetime
import pytz
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import MethodNotAllowed

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from elvis.forms.create import CollectionForm
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers import CollectionFullSerializer, CollectionListSerializer
from elvis.models.collection import Collection


class CollectionListHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_list.html"


class CollectionDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_detail.html"


class CollectionList(generics.ListCreateAPIView):
    model = Collection
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CollectionListSerializer
    renderer_classes = (JSONRenderer, CollectionListHTMLRenderer)
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    queryset = Collection.objects.filter(public=True)

    def get_queryset(self):
        query = self.request.GET.get('creator', None)
        user = self.request.user
        if user.is_anonymous():
            if query:
                return self.queryset.filter(creator__username=query)
            else:
                return self.queryset
        else:
            if query:
                return Collection.objects.filter(Q(creator__username=query) & (Q(public=True) | Q(creator=user)))
            else:
                return Collection.objects.filter(Q(public=True) | Q(creator=user))

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return super(CollectionList, self).get(self, request)

        response = super(CollectionList, self).get(self, request)
        user_download = request.user.downloads.all()[0]
        for i in range(len(response.data['results'])):
            col_pk = response.data['results'][i]['id']
            if user_download.collection_collections.filter(pk=col_pk):
                response.data['results'][i]['in_cart'] = True
            else:
                response.data['results'][i]['in_cart'] = False
        return response

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if not request.user.is_active:
            raise NotAuthenticated
        if 'action' in request.POST:
            return self._modify_collection(request)
        else:
            return self.create(request, *args, **kwargs)

    def _modify_collection(self, request):
        collection = Collection.objects.get(id=request.POST['id'])
        action = request.POST['action']
        if not (request.user == collection.creator or request.user.is_superuser):
            raise PermissionDenied

        if action == 'make-private':
            collection.public = False
            collection.save()
        elif action == 'make-public':
            collection.public = True
            collection.save()
        elif action == 'delete':
            collection.delete()
        else:
            raise MethodNotAllowed
        return Response(status=status.HTTP_202_ACCEPTED)

    def create(self, request, *args, **kwargs):
        form = CollectionForm(request.POST)

        if not form.is_valid():
            data = json.dumps({"errors": form.errors})
            return HttpResponse(data, content_type="json")
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

        user_download = request.user.downloads.all()[0]
        for piece in user_download.collection_pieces.all():
            piece.collections.add(new_collection)
        for movement in user_download.collection_movements.all():
            movement.collections.add(new_collection)

        new_collection.save()
        return HttpResponseRedirect("/collection/{0}".format(new_collection.id))


class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Collection
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CollectionFullSerializer
    renderer_classes = (JSONRenderer, CollectionDetailHTMLRenderer)
    queryset = Collection.objects.all()

    def get(self, request, *args, **kwargs):
        response = super(CollectionDetail, self).get(self, request)
        collection = Collection.objects.get(id=response.data['id'])
        user = self.request.user
        if not collection.public and not (collection.creator == user or user.is_superuser):
            raise PermissionDenied
        if user.is_anonymous():
            return super(CollectionDetail, self).get(self, request)

        user_download = request.user.downloads.all()[0]
        if user_download.collection_collections.filter(id=response.data['id']):
            response.data['in_cart'] = True
        else:
            response.data['in_cart'] = False
        for i in range(len(response.data['pieces'])):
            col_id = response.data['pieces'][i]['id']
            if user_download.collection_pieces.filter(id=col_id):
                response.data['pieces'][i]['in_cart'] = True
            else:
                response.data['pieces'][i]['in_cart'] = False
        for i in range(len(response.data['movements'])):
            col_id = response.data['movements'][i]['id']
            if user_download.collection_movements.filter(id=col_id):
                response.data['movements'][i]['in_cart'] = True
            elif response.data['movements'][i]['piece'] and user_download.collection_pieces.filter(id=response.data['movements'][i]['piece']['id']):
                response.data['movements'][i]['in_cart'] = "Piece"
            else:
                response.data['movements'][i]['in_cart'] = False
        return response

