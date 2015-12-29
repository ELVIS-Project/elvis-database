from rest_framework import permissions
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from elvis.models import Collection
from django.db.models.loading import get_model


"""Common behaviour for most views on the site are defined here.
This should make it easier to add/update security measures or
features to all views at once."""


class ElvisDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def is_authorized(self, request, *args, **kwargs):
        model = get_model('elvis', kwargs['model'])
        obj = model.objects.get(id=kwargs['pk'])
        user = self.request.user

        if user.is_superuser or obj.creator == user:
            return {'can_edit': True, 'can_view': True}

        if not obj.__dict__.get('public', True):
            return {'can_edit': False, 'can_view': False}
        else:
            return {'can_edit': False, 'can_view': True}

    """
    Default GET behaviour across detail views implements
    a check to see if the user is allowed to edit the object,
    which is used in template rendering.
    """
    def get(self, request, *args, **kwargs):
        auth = self.is_authorized(request, *args, **kwargs)
        if not auth['can_view']:
            raise PermissionDenied

        response = super().get(request, *args, **kwargs)
        response.data['can_edit'] = auth['can_edit']
        return response

    """
    Default DELETE/PATCH behaviour across detail views is to
    check if the user is allowed to edit the object,
    and raise a PermissionDenied exception if not.
    """
    def delete(self, request, *args, **kwargs):
        auth = self.is_authorized(request, *args, **kwargs)
        if not auth['can_edit']:
            raise PermissionDenied
        else:
            return super().delete(request, args, kwargs)

    def patch(self, request, *args, **kwargs):
        auth = self.is_authorized(request, *args, **kwargs)
        if not auth['can_edit']:
            raise PermissionDenied
        else:
            return super().patch(request, args, kwargs)

    def get_queryset(self):
        model = get_model('elvis', self.kwargs['model'])
        return model.objects.all()

class ElvisListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    def get_queryset(self):
        model = get_model('elvis', self.kwargs['model'])
        user = self.request.user
        Qlist = []

        creator = self.request.GET.get('creator')
        if creator:
            Qlist.append(Q(creator__username=creator))

        startswith = self.request.GET.get('startswith')
        if startswith:
            Qlist.append(Q(title__istartswith=startswith))

        if model == Collection:
            Qlist.append((Q(public=True) | Q(creator=user)))

        if Qlist:
            return model.objects.filter(*Qlist)
        else:
            return model.objects.all()
