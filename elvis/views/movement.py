from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.movement import MovementSerializer, MovementListSerializer
from elvis.models.movement import Movement


class MovementListHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_list.html"


class MovementDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_detail.html"


class MovementList(generics.ListCreateAPIView):
    model = Movement
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = MovementListSerializer
    renderer_classes = (JSONRenderer,MovementListHTMLRenderer)
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 20
    queryset = Movement.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return super(MovementList, self).get(self, request)

        response = super(MovementList, self).get(self, request)
        user_download = request.user.downloads.all()[0]
        for i in range(len(response.data['results'])):
            mov_pk = response.data['results'][i]['item_id']
            if user_download.collection_movements.filter(pk=mov_pk):
                response.data['results'][i]['in_cart'] = True
            else:
                response.data['results'][i]['in_cart'] = False
        return response


class MovementDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Movement
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = MovementSerializer
    renderer_classes = (JSONRenderer, MovementDetailHTMLRenderer)
    queryset = Movement.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return super(MovementDetail, self).get(self, request)

        response = super(MovementDetail, self).get(self, request)
        user_download = request.user.downloads.all()[0]
        if (response.data['piece'] and user_download.collection_pieces.filter(pk=response.data['piece']['pk'])):
            response.data['in_cart'] = "Piece"
        elif user_download.collection_movements.filter(pk=response.data['item_id']):
            response.data['in_cart'] = True
        else:
            response.data['in_cart'] = False

        return response