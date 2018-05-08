from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from user_profile import views

urlpatterns = patterns('',
    url(r'^info/$', views.UserList.as_view()),
    url(r'^info/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^profile/$', views.UserProfileDetail.as_view()),
    url(r'^preference/$', views.PreferenceList.as_view()),
    url(r'^preference/(?P<pk>[0-9]+)/$', views.PreferenceDetail.as_view()),

    # Custom views
    url(r'^signup/$', views.SignupView.as_view()),
    url(r'^edit_profile/$', views.EditUserProfileView.as_view()),
    url(r'^device_token/$', views.StoreDeviceTokenView.as_view()),
    url(r'^change_password/(?P<identifier>[-\w]+)/$', views.ChangePasswordView.as_view()),
    url(r'^change_location/(?P<identifier>[-\w]+)/$', views.ChangeUserLocation.as_view()),
    url(r'^edit_preferences/$', views.ChangePreferencesView.as_view()),
    url(r'^preference_list/$', views.PreferenceList.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
