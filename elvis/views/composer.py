from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.composer import ComposerSerializer, ComposerListSerializer
from elvis.models.composer import Composer


class ComposerListHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_list.html"


class ComposerDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_detail.html"


class ComposerList(generics.ListCreateAPIView):
    model = Composer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ComposerListSerializer
    renderer_classes = (JSONRenderer, ComposerListHTMLRenderer)
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    queryset = Composer.objects.all()

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            return self.queryset.filter(title=query)
        else:
            return self.queryset

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return super(ComposerList, self).get(self, request)

        response = super(ComposerList, self).get(self, request)
        user_download = request.user.downloads.all()[0]
        for i in range(len(response.data['results'])):
            com_pk = response.data['results'][i]['item_id']
            if user_download.collection_composers.filter(pk=com_pk):
                response.data['results'][i]['in_cart'] = True
            else:
                response.data['results'][i]['in_cart'] = False
        return response

class ComposerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Composer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ComposerSerializer
    renderer_classes = (JSONRenderer, ComposerDetailHTMLRenderer)
    queryset = Composer.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return super(ComposerDetail, self).get(self, request)

        response = super(ComposerDetail, self).get(self, request)
        user_download = request.user.downloads.all()[0]
        if user_download.collection_composers.filter(pk=response.data['item_id']):
            response.data['in_cart'] = True
        else:
            response.data['in_cart'] = False

        for i in range(len(response.data['pieces'])):
            com_pk = response.data['pieces'][i]['item_id']
            if user_download.collection_pieces.filter(pk=com_pk):
                response.data['pieces'][i]['in_cart'] = True
            else:
                response.data['pieces'][i]['in_cart'] = False
        for i in range(len(response.data['free_movements'])):
            com_pk = response.data['free_movements'][i]['item_id']
            if user_download.collection_movements.filter(pk=com_pk):
                response.data['free_movements'][i]['in_cart'] = True
            else:
                response.data['free_movements'][i]['in_cart'] = False
        return response