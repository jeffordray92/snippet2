from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from transaction import views

urlpatterns = patterns('',
    url(r'^info/$', views.TransactionList.as_view()),
    url(r'^info/(?P<identifier>[-\w]+)/$', views.TransactionDetail.as_view()),
    url(r'^notification/(?P<pk>[0-9]+)/$', views.NotificationDetail.as_view()),
    url(r'^notification/view/(?P<pk>[0-9]+)/$', views.NotificationView.as_view()),
    url(r'^notifications/(?P<identifier>[-\w]+)/$', views.NotificationList.as_view()),
    url(r'^notification/action/$', views.NotificationAction.as_view()),
    url(r'^history/$', views.SwappingHistory.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
