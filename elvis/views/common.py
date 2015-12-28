from rest_framework import permissions
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from django.db.models.loading import get_model

class ElvisList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ElvisDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    """
    Default GET behaviour across detail views implements
    a check to see if the user is allowed to edit the object,
    which is used in template rendering.
    """
    def get(self, request, *args, **kwargs):
        model = get_model('elvis', kwargs['model'])
        obj = model.objects.get(id=kwargs['pk'])
        user = self.request.user

        response = super().get(request, *args, **kwargs)
        if obj.creator == user or user.is_superuser:
            response.data['can_edit'] = True
        else:
            response.data['can_edit'] = False
        return response

    """
    Default DELETE behaviour across detail views is to
    check if the user is allowed to edit the object,
    and raise a PermissionDenied exception if not.
    """
    def delete(self, request, *args, **kwargs):
        model = get_model('elvis', kwargs['model'])
        obj = model.objects.get(id=kwargs['pk'])
        user = self.request.user
        if not(obj.creator == user or user.is_superuser):
            raise PermissionDenied
        else:
            return super().delete(request, args, kwargs)


class ElvisModifyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    """
    Default dispatch (all http verbs) behaviour any modification
    view is to raise a PermissionDenied exception if the user
    is not allowed to edit the object.
    """
    def dispatch(self, request, *args, **kwargs):
        model = get_model('elvis', kwargs['model'])
        obj = model.objects.get(id=kwargs['pk'])
        user = self.request.user

        if not (obj.creator == user or user.is_superuser):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
