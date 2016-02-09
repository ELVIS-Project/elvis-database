from django.conf.urls import patterns, include, url, static
from django.conf import settings

import os

from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# temporary views for these pages
from elvis.views.main import home, about, contact
from elvis.views.views import solr_suggest
from elvis.views.auth import LoginFormView, logout_view
from elvis.views.search import SearchView, SearchAndAddToCartView
from elvis.views.download import DownloadCart, Downloading
from elvis.views.piece import PieceList, PieceDetail, PieceCreate, PieceUpdate, MyPieces
from elvis.views.user import UserAccount, UserUpdate
from elvis.views.movement import MovementList, MovementDetail
from elvis.views.composer import ComposerList, ComposerDetail
from elvis.views.collection import CollectionList, CollectionDetail, \
        CollectionCreate
from elvis.views.media import MediaServeView
from django.contrib.auth import views as auth_views
import django.views.static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

media_path = os.path.realpath('media/attachments/')
urlpatterns = []

urlpatterns.extend([
        url(r'^$', home, name='home'),

        url(r'^search/$', SearchView.as_view(), name="search-view"),
        url(r'^search/add-to-cart/$', SearchAndAddToCartView.as_view(), name="search-and-add-to-cart-view"),

        url(r'^account/$', UserAccount.as_view(), name="user-account"),
        url(r'^register/$', UserAccount.as_view(), name="user-account"),
        url(r'^account/update/$', UserUpdate.as_view(), name="user-update"),
        url(r'^account/password_change/$', auth_views.password_change, {'template_name': 'user/password_change.html'}, name='password_change'),
        url(r'^account/password_change_done/$', auth_views.password_change_done, {'template_name': 'user/password_change_done.html'}, name='password_change_done'),
        url(r'^login/$', LoginFormView.as_view(), name="login-form"),
        url(r'^logout/$', logout_view),
        url(r'^register/$', UserAccount.as_view(), name='register-form'),


        #Password resettting won't work until server emails are up.
        url(r'^password/reset/$', auth_views.password_reset, {'template_name': 'user/password_reset.html'}, name='password_reset'),
        url(r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'user/password_reset_done.html'}, name='password_reset_done'),
        url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {'template_name': 'user/password_reset_confirm.html'}, name='password_reset_confirm'),
        url(r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'user/password_reset_complete.html'}, name='password_reset_complete'),

        url(r'^downloading/$', Downloading.as_view(), name="downloading"),
        url(r'^download-cart/$', DownloadCart.as_view(), name="download-cart"),


        url(r'^pieces/upload/$', PieceCreate.as_view(), name="piece-create", kwargs={'model': "Piece"}),
        url(r'^pieces/$', PieceList.as_view(), name="piece-list", kwargs={'model': "Piece"}),
        url(r'^piece/(?P<pk>[0-9]+)/$', PieceDetail.as_view(), name="piece-detail", kwargs={'model': "Piece"}),
        url(r'^piece/(?P<pk>[0-9]+)/update/$', PieceUpdate.as_view(), name="piece-update", kwargs={'model': "Piece"}),
        url(r'^pieces/mine$', MyPieces.as_view(), name="my-pieces", kwargs={'model': "Piece"}),

        url(r'^collections/$', CollectionList.as_view(), name="collection-list", kwargs={'model': "Collection"}),
        url(r'^collection/(?P<pk>[0-9]+)/$', CollectionDetail.as_view(), name="collection-detail", kwargs={'model': "Collection"}),
        url(r'^collection/create/', CollectionCreate.as_view(), name="collection-create", kwargs={'model': "Collection"}),

        url(r'^composers/$', ComposerList.as_view(), name="composer-list", kwargs={'model': "Composer"}),
        url(r'^composer/(?P<pk>[0-9]+)/$', ComposerDetail.as_view(), name="composer-detail", kwargs={'model': "Composer"}),

        url(r'^movements/$', MovementList.as_view(), name="movement-list", kwargs={'model': "Movement"}),
        url(r'^movement/(?P<pk>[0-9]+)/$', MovementDetail.as_view(), name="movement-detail", kwargs={'model': "Movement"}),

        url(r'^about/$', about, name='about'),

        url(r'^contact/$', contact, name="contact"),

        url(r'^suggest/$', solr_suggest),

        url(r'^media/(?P<pk>.*)$', MediaServeView.as_view(), name="media"),
        ]
)

# Serving static files
urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()


# Only add admin if it's enabled
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^admin/', include(admin.site.urls)))
