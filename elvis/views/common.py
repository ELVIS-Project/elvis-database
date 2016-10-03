from rest_framework import permissions
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from elvis.models import Collection, Piece, Movement
from django.apps import apps


"""Common behaviour for most views on the site are defined here.
This should make it easier to add/update security measures or
features to all views at once."""


class ElvisDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def determine_perms(self, request, *args, **kwargs):
        """Given a request, determine user's permissions in regards to
        the object in question.
        :return: A dict with'can_view' and 'can_edit' keys.
        """
        user = self.request.user
        model = apps.get_model('elvis', kwargs['model'])
        obj = model.objects.get(id=kwargs['pk'])

        if user.is_superuser or obj.creator == user:
            return {'can_edit': True, 'can_view': True}

        if not obj.__dict__.get('public', True):
            return {'can_edit': False, 'can_view': False}
        elif obj.__dict__.get('hidden', False):
            return {'can_edit': False, 'can_view': False}
        else:
            return {'can_edit': False, 'can_view': True}

    def if_can_edit(self, request, *args, **kwargs):
        """Utility function which raises a PermissionDenied error if the
        user can not edit the object in question."""
        if self.determine_perms(self, request, *args, **kwargs)['can_edit']:
            return
        raise PermissionDenied

    def if_can_view(self, request, *args, **kwargs):
        """Utility function which raises a PermissionDenied error if the
        user can not view the object in question."""
        if self.determine_perms(self, request, *args, **kwargs)['can_view']:
            return
        raise PermissionDenied

    """Default GET behaviour across detail views implements
    a check to see if the user is allowed to edit the object,
    which is used in template rendering."""
    def get(self, request, *args, **kwargs):
        values = set(self.request.GET.getlist('values[]'))
        resp = super().get(request, *args, **kwargs)
        if not resp.data['can_view']:
            raise PermissionDenied

        if not values:
            return resp

        # Filter for requested values.
        data = resp.data
        new_data = {k: data.get(k) for k in values}
        resp.data = new_data
        return resp

    """Default DELETE/PATCH/PUT behaviour across detail views is to
    check if the user is allowed to edit the object,
    and raise a PermissionDenied exception if not."""
    def delete(self, request, *args, **kwargs):
        self.if_can_edit(self, request, *args, **kwargs)
        return super().delete(request, args, kwargs)

    def patch(self, request, *args, **kwargs):
        self.if_can_edit(self, request, *args, **kwargs)
        return super().patch(request, args, kwargs)

    def put(self, request, *args, **kwargs):
        self.if_can_edit(self, request, *args, **kwargs)
        return super().put(request, args, kwargs)

    """This just saves one from having to define the queryset
    in every single view"""
    def get_queryset(self):
        model = apps.get_model('elvis', self.kwargs['model'])
        return model.objects.all()


class ElvisListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny, )

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        values = set(self.request.GET.getlist('values[]'))
        resp = super().get(self, request, *args, **kwargs)
        if not values:
            return resp
        data = resp.data.get('results')
        for i, item in enumerate(data):
            data[i] = {k: item.get(k) for k in values}
        return resp

    def get_queryset(self):
        model = apps.get_model('elvis', self.kwargs['model'])
        user = None if self.request.user.is_anonymous() else self.request.user
        Qlist = []

        creator = self.request.GET.get('creator')
        if creator:
            Qlist.append(Q(creator__username=creator))

        startswith = self.request.GET.get('startswith')
        if startswith:
            Qlist.append(Q(title__istartswith=startswith))

        if model == Collection:
            Qlist.append((Q(public=True) | Q(creator=user)))

        if model == Piece or model == Movement:
            Qlist.append((Q(hidden=False) | Q(creator=user)))

        if Qlist:
            return model.objects.filter(*Qlist)
        else:
            return model.objects.all()
