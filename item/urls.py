from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from item import views

urlpatterns = patterns('',
    url(r'^entry/(?P<pk>[0-9]+)/$', views.ItemDetail.as_view()),
    url(r'^entry/list/(?P<identifier>[-\w]+)/$', views.ItemList.as_view()),
    url(r'^entry/view/(?P<pk>[0-9]+)/$', views.ItemView.as_view()),
    url(r'^entry/edit/(?P<pk>[0-9]+)/$', views.ItemEdit.as_view()),
    url(r'^entry/add/$', views.ItemAdd.as_view()),
    url(r'^entry/delete/(?P<pk>[0-9]+)/$', views.ItemDelete.as_view()),
    url(r'^tag/$', views.TagList.as_view()),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagDetail.as_view()),
    url(r'^category/$', views.CategoryList.as_view()),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryDetail.as_view()),
    url(r'^conflict/check/$', views.ItemConflictCheck.as_view()),
    url(r'^conflict/resolve/$', views.ItemConflictResolve.as_view()),
    url(r'^matches/(?P<pk>[0-9]+)/$', views.MatchingItems.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
