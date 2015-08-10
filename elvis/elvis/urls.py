from django.conf.urls import patterns, include, url, static
from django.conf import settings

import os

from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# temporary views for these pages
from elvis.views.main import home, about, contact
from elvis.views.views import solr_suggest
from elvis.views.auth import LoginFormView, logout_view
from elvis.views.search import SearchView
from elvis.views.download import DownloadDetail, Downloading
from elvis.views.piece import PieceList, PieceDetail, PieceCreate
from elvis.views.user import  UserDetail, UserAccount, UserUpdate
from elvis.views.movement import MovementList, MovementDetail
from elvis.views.composer import ComposerList, ComposerDetail
from elvis.views.collection import CollectionList, CollectionDetail, CollectionCurrent
from elvis.views.tag import TagDetail
from elvis.views.attachment import AttachmentList, AttachmentDetail
from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

media_path = os.path.realpath('media/attachments/')
urlpatterns = []

urlpatterns += format_suffix_patterns(
    patterns('',
        url(r'^$', home, name='home'),

        url(r'^search/', SearchView.as_view(), name="search-view"),

        #url(r'^users/$', UserList.as_view(), name="user-list"),
        url(r'^user/(?P<pk>[0-9]+)/$', UserDetail.as_view(), name="user-detail"),
        url(r'^account/$', UserAccount.as_view(), name="user-account"),
        url(r'^register/$', UserAccount.as_view(), name="user-account"),
        url(r'^account/update/$', UserUpdate.as_view(), name="user-update"),
        url(r'^account/password_change/$', auth_views.password_change, {'template_name': 'user/password_change.html'}, name='password_change'),
        url(r'^account/password_change_done/$', auth_views.password_change_done, {'template_name': 'user/password_change_done.html'}, name='password_change_done'),
        url(r'^login/?', LoginFormView.as_view(), name="login-form"),
        url(r'^logout/?', logout_view),
        url(r'^register/?', UserAccount.as_view(), name='register-form'),


        #Password resettting won't work until server emails are up.
        url(r'^password/reset/$', auth_views.password_reset, {'template_name': 'user/password_reset.html'}, name='password_reset'),
        url(r'^password/reset/done/$', auth_views.password_reset_done, {'template_name': 'user/password_reset_done.html'}, name='password_reset_done'),
        url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {'template_name': 'user/password_reset_confirm.html'}, name='password_reset_confirm'),
        url(r'^password/reset/complete/$', auth_views.password_reset_complete, {'template_name': 'user/password_reset_complete.html'}, name='password_reset_complete'),

        url(r'^downloads/$', DownloadDetail.as_view(), name="download-detail"),
        url(r'^downloading/$', Downloading.as_view(), name="downloading"),

        url(r'^pieces/upload/$', PieceCreate.as_view(), name="piece-create"),
        url(r'^pieces/$', PieceList.as_view(), name="piece-list"),
        url(r'^piece/(?P<pk>[0-9]+)/$', PieceDetail.as_view(), name="piece-detail"),

        url(r'^collections/$', CollectionList.as_view(), name="collection-list"),
        url(r'^collection/(?P<pk>[0-9]+)/$', CollectionDetail.as_view(), name="collection-detail"),
        url(r'^download/cart/$', CollectionCurrent.as_view(), name="collection-create"),

        url(r'^composers/$', ComposerList.as_view(), name="composer-list"),
        url(r'^composer/(?P<pk>[0-9]+)/$', ComposerDetail.as_view(), name="composer-detail"),

        url(r'^movements/$', MovementList.as_view(), name="movement-list"),
        url(r'^movement/(?P<pk>[0-9]+)/$', MovementDetail.as_view(), name="movement-detail"),

        url(r'^attachments/$', AttachmentList.as_view(), name="attachment-list"),
        url(r'^attachment/(?P<pk>[0-9]+)/$', AttachmentDetail.as_view(), name="attachment-detail"),

        url(r'^tag/(?P<pk>[0-9]+)/$', TagDetail.as_view(), name="tag-detail"),

        url(r'^about/', about, name='about'),

        url(r'^contact/', contact, name="contact"),

        url(r'^suggest/$', solr_suggest),

        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
)

# Serving static files

# Media stuff
urlpatterns += patterns('', 
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()


# Only add admin if it's enabled
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )
