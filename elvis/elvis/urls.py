from django.conf.urls import patterns, include, url
#from django.conf.urls import static
from django.conf import settings

import os

from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from elvis.views.main import home, user_login, request_permission
from elvis.views.user import user_profiles, user_view
from elvis.views.user import registration, setPermissions
from elvis.views.project import projects_list, project_view, project_participants, project_discussions, discussion_view
from elvis.views.lists import corpora_list, corpora_list_min
from elvis.views.lists import composer_list, composer_list_min
from elvis.views.lists import piece_list, piece_list_min 
from elvis.views.lists import movement_list, movement_list_min
from elvis.views.lists import tag_list, tag_tree
from elvis.views.lists import download_list
from elvis.views.details import corpus_view, composer_view, movement_view, piece_view

from elvis.views.forms import create_composer, create_corpus, create_corpus_large, create_project
from elvis.views.forms import create_piece, create_movement
from elvis.views.forms import upload_file, delete_model
from elvis.views.forms import download_piece, save_piece, download_movement, save_movement
from elvis.views.forms import inviteUsersToProject, deleteProject

from elvis.views.search import search


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

media_path = os.path.realpath('media/attachments/')

urlpatterns = []

urlpatterns += format_suffix_patterns(
    patterns('',
        
        url(r'^$', home, name='home'),
        url(r'^login/$', user_login, name="login"),
        url(r'^permission/$', request_permission, name="permission"),
        url(r'^registration/$', registration, name="registration"),
        url(r'^registration/permissions/$', setPermissions, name="registration"),

        # Users
        url(r'^userprofiles/$', user_profiles, name="userprofile-list"),
        url(r'^userprofiles/(?P<pk>[0-9]+)/$', user_view, name="userprofile-detail"),

        # Projects
        url(r'^projects/$', projects_list, name="projects-list"),
        url(r'^projects/(?P<pk>[0-9]+)/$', project_view, name="project-detail"),
        url(r'^projects/(?P<pk>[0-9]+)/participants$', project_participants, name="project-participants"),
        url(r'^projects/(?P<pk>[0-9]+)/discussions$', project_discussions, name="project-discussions"),
        url(r'^projects/(?P<pk>[0-9]+)/discussions/(?P<did>[0-9]+)$', discussion_view, name="project-discussions"),
        url(r'^projects/invite', inviteUsersToProject, name="invite-project"),
        url(r'^projects/delete', deleteProject, name="delete-project"),

        # Pieces
        url(r'^pieces/$', piece_list_min, name="piece-list"),
        url(r'^piecesmin/$', piece_list, name="piece-list-min"),
        url(r'^pieces/(?P<pk>[0-9]+)/$', piece_view, name="piece-detail"),

        # Corpora
        url(r'^corpora/$', corpora_list_min, name="corpus-list"),
        url(r'^corporamin/$', corpora_list, name="corpus-list-min"),
        url(r'^corpora/(?P<pk>[0-9]+)/$', corpus_view, name="corpus-detail"),

        # Composers
        url(r'^composers/$', composer_list_min, name="composer-list"),
        url(r'^composersmin/$', composer_list, name="composer-list-min"),
        url(r'^composers/(?P<pk>[0-9]+)/$', composer_view, name="composer-detail"),
        url(r'^addcomposer/$', create_composer, name="create-composer"),
        url(r'^addcorpus/$', create_corpus, name="create-corpus"),

        # Movements
        url(r'^movements/$', movement_list_min, name="movement-list"),
        url(r'^movementsmin/$', movement_list, name="movement-list-min"),
        url(r'^movements/(?P<pk>[0-9]+)/$', movement_view, name="movement-detail"),

        # Tags
        url(r'^tags/$', tag_list, name="tag-list"),
        url(r'^tagtree/$', tag_tree, name="tag-tree"),

        # Upload stuff
        url(r'^upload/corpus/$', create_corpus_large, name="create-corpus-large"),
        url(r'^upload/piece/$', create_piece, name="create-piece"),
        url(r'^upload/movement/$', create_movement, name="create-movement"),
        url(r'^upload/project/$', create_project, name="create-project"),
        url(r'^upload/$', upload_file, name="upload"),

        # Delete a model
        url(r'^(?P<entity>[a-z_]+)/(?P<pk>[0-9]+)/delete/', delete_model, name="delete-model"),

        # Download stuff
        url(r'^downloads/$', download_list, name="download-list"),
        url(r'^pieces/(?P<pk>[0-9]+)/download/$', download_piece, name="download-piece"),
        url(r'^pieces/(?P<pk>[0-9]+)/save/$', save_piece, name="save-piece"),
        url(r'^movements/(?P<pk>[0-9]+)/download/$', download_movement, name="download-movement"),
        url(r'^movements/(?P<pk>[0-9]+)/save/$', save_movement, name="save-movement"),

        # Search stuff
        url(r'^search/$', search, name="search"),
        
        #url(r'^attachments/$', AttachmentList.as_view(), name="attachment-list"),
        #url(r'^attachment/(?P<pk>[0-9]+)/$', AttachmentDetail.as_view(), name="attachment-detail"),

        (r'^media/attachments/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
)

# Serving static files
#urlpatterns += staticfiles_urlpatterns()

# Media stuff
urlpatterns += patterns('', 
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += staticfiles_urlpatterns()

# Only add admin if it's enabled
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )


# For serving stuff under MEDIA_ROOT in debug mode only
# if settings.DEBUG:
#     urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
