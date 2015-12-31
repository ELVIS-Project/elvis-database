import json
import datetime
import pytz


from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from elvis.forms.create import CollectionForm
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers import CollectionFullSerializer, CollectionListSerializer
from elvis.views.common import ElvisListCreateView, ElvisDetailView
from elvis.models.collection import Collection


class CollectionListHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_list.html"


class CollectionDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_detail.html"


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


class CollectionDetail(ElvisDetailView):
    model = Collection
    serializer_class = CollectionFullSerializer
    renderer_classes = (CollectionDetailHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)
    queryset = Collection.objects.all()


