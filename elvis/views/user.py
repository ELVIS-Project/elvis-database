import urllib.request, urllib.error, urllib.parse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.db.models import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.serializers import UserFullSerializer
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from elvis.models.collection import Collection
from elvis.models.piece import Piece
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.forms import UserForm, UserChangeForm


class UserAccountHTMLRenderer(CustomHTMLRenderer):
    template_name = "user/user_account.html"


class UserAccount(generics.CreateAPIView):
    model = User
    serializer_class = UserFullSerializer
    renderer_classes = (JSONRenderer, UserAccountHTMLRenderer)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return render(request, "register.html")
        else:
            return render(request, "user/user_account.html")
            
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous():
            form = UserForm(data=request.POST)
            if form.is_valid():
                #Verify captcaha
                if not request.POST['g-recaptcha-response']:
                    form.add_error(None, "You must complete the reCaptcha to register!")
                    return render(request, "register.html", {'form': form})

                captcha_data = urllib.parse.urlencode({
                    'secret': settings.RECAPTCHA_PRIVATE_KEY,
                    'response': request.POST['g-recaptcha-response']})
                captcha_data = captcha_data.encode('utf-8')

                res = urllib.request.urlopen(
                    "https://www.google.com/recaptcha/api/siteverify",
                    captcha_data)
                res = res.read().decode('utf-8')
                if 'false' in res:
                    form.add_error(None, "You are a robot!")
                    return render(request, "register.html", {'form': form})

                user = form.save()        
                user = authenticate(username=request.POST['username'], password=request.POST['password1'])
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                return render(request, "register.html", {'form': form})
        else:
            form = UserChangeForm(data=request.POST, instance=request.user)
            if not form.is_valid():
                return render(request, "user/user_update.html", {'form': form})

            clean_form = form.cleaned_data
            if clean_form['email']:
                user.email = clean_form['email']
            if clean_form['first_name']:
                user.first_name = clean_form['first_name']
            if clean_form['last_name']:
                user.last_name = clean_form['last_name']
            user.save()

            return HttpResponseRedirect("/account")


class UserUpdate(generics.CreateAPIView):
    model = User
    serializer_class = UserFullSerializer
    renderer_classes = (JSONRenderer, UserAccountHTMLRenderer)

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return render(request, "register.html")
        else:
            return render(request, "user/user_update.html")


@receiver(user_logged_out)
def save_cart(sender, request, user, **kwargs):
    cart = request.session.get('cart', {})
    pieces = []
    movements = []
    collections = []
    composers = []

    for key in cart.keys():
        if key.startswith("M"):
            m_id = key[2:]
            try:
                mov = Movement.objects.get(uuid=m_id)
            except ObjectDoesNotExist:
                continue
            movements.append(mov)
        elif key.startswith("P"):
            p_id = key[2:]
            try:
                p = Piece.objects.get(uuid=p_id)
            except ObjectDoesNotExist:
                continue
            pieces.append(p)
        elif key.startswith("COL"):
            col_id = key[4:]
            try:
                col = Collection.objects.get(uuid=col_id)
            except ObjectDoesNotExist:
                continue
            collections.append(col)
        elif key.startswith("COM"):
            com_id = key[4:]
            try:
                com = Composer.objects.get(uuid=com_id)
            except ObjectDoesNotExist:
                continue
            composers.append(com)

    user_download = request.user.downloads.first()
    user_download.collection_movements.clear()
    user_download.collection_movements.add(*movements)
    user_download.collection_pieces.clear()
    user_download.collection_pieces.add(*pieces)
    user_download.collection_collections.clear()
    user_download.collection_collections.add(*collections)
    user_download.collection_composers.clear()
    user_download.collection_composers.add(*composers)
    user_download.save()


@receiver(user_logged_in)
def load_cart(sender, request, user, **kwargs):
    """
    Cart gets dumped to or loaded from database when a user logs in or logs out.

    :param sender:
    :param request:
    :param user:
    :param kwargs:
    :return:
    """
    user_download = user.downloads.first()
    cart = {}
    cart.update({"M-" + str(k.uuid): True for k in user_download.collection_movements.all()})
    cart.update({"P-" + str(k.uuid): True for k in user_download.collection_pieces.all()})
    cart.update({"COL-" + str(k.uuid): True for k in user_download.collection_collections.all()})
    cart.update({"COM-" + str(k.uuid): True for k in user_download.collection_composers.all()})
    request.session['cart'] = cart
