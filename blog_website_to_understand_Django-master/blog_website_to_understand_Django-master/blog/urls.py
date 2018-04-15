from django.conf.urls import  url
from . import views


urlpatterns = [
    url(r'^$', views.PostListView.as_view(), name='post_list'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    # name means the NAME of this urls, which can be indexe using url template {% url 'appname:about'%}
    # in later template, views, models files
    url(r'^post/(?P<pk>\d+)$',views.PostDetailView.as_view(), name='post_detail'),  # show a post when clicking one
    #  (showing primary key)
    url(r'^post/new/$',views.CreatePostView.as_view(), name='post_new'),  # new post view
    url(r'^post/(?P<pk>\d+)/edit/$', views.PostUpdateView.as_view(), name='post_edit'),  # edit view
    url(r'^post/(?P<pk>\d+)/remove/', views.PostDeleteView.as_view(), name='post_remove'),
    # (1) update views (2) Update the corresponding urls
    url(r'^drafts/$',views.DraftListView.as_view(), name='post_draft_list'),
    url(r'^post/(?P<pk>\d+)/comment/$', views.add_comment_to_post, name = 'add_comment_to_post'),
    # this is functional view
    url(r'^comment/(?P<pk>\d+)/approve/$',views.comment_approve,name='comment_approve'),
    url(r'^comment/(?P<pk>\d+)/remove/$',views.comment_approve,name='comment_remove'),
    url(r'^post/(?P<pk>\d+)/publish/$', views.post_publish, name='post_publish'),
]