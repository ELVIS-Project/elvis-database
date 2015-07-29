import pdb
import json
import datetime
import pytz
from django.db.models import Q

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from elvis.models import Download
from elvis.forms.create import CollectionForm
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from elvis.serializers.download import CartSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.collection import CollectionSerializer, CollectionListSerializer
from elvis.models.collection import Collection


class CollectionListHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_list.html"


class CollectionDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_detail.html"


class CollectionCurrentHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_current.html"


class CollectionList(generics.ListCreateAPIView):
    model = Collection
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CollectionListSerializer
    renderer_classes = (JSONRenderer, CollectionListHTMLRenderer)
    paginate_by = 10
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

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if 'make-private' in request.POST:
            collection = Collection.objects.get(id=request.POST['make-private'])
            collection.public = False
            collection.save()
            return HttpResponse(json.dumps({'url': "/collection/{0}".format(collection.id)}), content_type="json")
        elif 'make-public' in request.POST:
            collection = Collection.objects.get(id=request.POST['make-public'])
            collection.public = True
            collection.save()
            return HttpResponse(json.dumps({'url': "/collection/{0}".format(collection.id)}), content_type="json")
        elif 'delete' in request.POST:
            collection = Collection.objects.get(id=request.POST['delete'])
            collection.delete()
            return HttpResponse(json.dumps({'url': "/collections/"}), content_type="json")
        else:
            return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not request.user.is_active:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
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
    serializer_class = CollectionSerializer
    renderer_classes = (JSONRenderer, CollectionDetailHTMLRenderer)
    queryset = Collection.objects.filter(public=True)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous():
            return self.queryset
        else:
            return Collection.objects.filter(Q(public=True) | Q(creator=user))


class CollectionCurrent(generics.RetrieveUpdateDestroyAPIView):
    model = Download
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CartSerializer
    renderer_classes = (JSONRenderer, CollectionCurrentHTMLRenderer)
    queryset = Download.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            obj = Download.objects.filter(user=user).latest("created")
            return obj
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        if User.is_authenticated(request.user):
            return self.retrieve(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)