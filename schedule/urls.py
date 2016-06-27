
from django.conf.urls import url
from schedule import views

urlpatterns = [
    #url(r'^users/$', views.UserList.as_view()),
    url(r'^users/$', views.list_users),
    url(r'^users/id/(?P<pk>[0-9]+)/$', views.get_users),
    url(r'^schedule/$', views.schedule),
    url(r'^users/sessions/$', views.login),
    url(r'^users/sessions/logout$', views.logout),
    url(r'^schedule/id/(?P<pk>[0-9]+)/$', views.user_schedule),
]
