from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from message import views

urlpatterns = patterns('',
    url(r'^entry/$', views.MessageList.as_view()),
    url(r'^entry/(?P<pk>[0-9]+)/$', views.MessageDetail.as_view()),
    url(r'^threads/(?P<identifier>[-\w]+)/$', views.ThreadList.as_view()),
    url(r'^thread/new/$', views.ThreadCreate.as_view()),
    url(r'^thread/(?P<pk>[0-9]+)/$', views.ThreadDetail.as_view()),
    url(r'^send/$', views.SendMessage.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
