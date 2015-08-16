from django.conf.urls import patterns, url

from approval_polls import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^my-polls/$', views.myPolls, name='my_polls'),
    url(r'^(?P<poll_id>\d+)/embed_instructions/$', views.embed_instructions, name='embed_instructions'),
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.PollUpdate.as_view(), name='update')

)
