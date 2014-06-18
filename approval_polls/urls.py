from django.conf.urls import patterns, url

from approval_polls import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^create/$', views.create, name='create'),
    url(r'^created/$', views.created, name='created'),
    #url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'approval_polls/login.html'}, name='login'),
    #url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/approval_polls'}, name='logout'),
    #url(r'^register/$', views.register),
)

