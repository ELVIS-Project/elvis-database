from django.conf.urls import patterns, include, url, static
from django.conf import settings

import os

from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# temporary views for these pages
from elvis.views.main import home, about, queries, temp
from elvis.views.views import solr_suggest, upload_files, query_db
from elvis.views.auth import LoginFormView, logout_view
from elvis.views.search import SearchView
from elvis.views.project import ProjectList, ProjectDetail
from elvis.views.download import DownloadDetail, Downloading
from elvis.views.piece import PieceList, PieceDetail, PieceCreate
from elvis.views.create import CreatePiece
from elvis.views.user import UserList, UserDetail, UserAccount
from elvis.views.userprofile import UserProfileList, UserProfileDetail
from elvis.views.movement import MovementList, MovementDetail
from elvis.views.composer import ComposerList, ComposerDetail
from elvis.views.collection import CollectionList, CollectionDetail
from elvis.views.tag import TagList, TagDetail
from elvis.views.attachment import AttachmentList, AttachmentDetail
from elvis.views.create import CreatePiece

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
        url(r'^account/', UserAccount.as_view(), name = "user-account"),
        url(r'^login/?', LoginFormView.as_view(), name="login-form"),
        url(r'^logout/?', logout_view),

        url(r'^downloads/$', DownloadDetail.as_view(), name="download-detail"),
        url(r'^downloading/$', Downloading.as_view(), name="downloading"),

        url(r'^pieces/create/$', PieceCreate.as_view(), name="piece-create"),
        url(r'^pieces/$', PieceList.as_view(), name="piece-list"),
        url(r'^piece/(?P<pk>[0-9]+)/$', PieceDetail.as_view(), name="piece-detail"),

        url(r'^collections/$', CollectionList.as_view(), name="collection-list"),
        url(r'^collection/(?P<pk>[0-9]+)/$', CollectionDetail.as_view(), name="collection-detail"),

        url(r'^composers/$', ComposerList.as_view(), name="composer-list"),
        url(r'^composer/(?P<pk>[0-9]+)/$', ComposerDetail.as_view(), name="composer-detail"),

        url(r'^movements/$', MovementList.as_view(), name="movement-list"),
        url(r'^movement/(?P<pk>[0-9]+)/$', MovementDetail.as_view(), name="movement-detail"),

        url(r'^attachments/$', AttachmentList.as_view(), name="attachment-list"),
        url(r'^attachment/(?P<pk>[0-9]+)/$', AttachmentDetail.as_view(), name="attachment-detail"),

        url(r'^tag/(?P<pk>[0-9]+)/$', TagDetail.as_view(), name="tag-detail"),

        url(r'^about/', about, name='about'),

        url(r'^temp/', temp, name="temp"),

        url(r'^suggest/$', solr_suggest),
        url(r'^query_db/$', query_db),


       url(r'^upload/$', upload_files),

        #TEMPORARY
        url(r'^create/piece$', CreatePiece.as_view()),


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
