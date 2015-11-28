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
    url(r'^my-info/$', views.myInfo, name='my_info'),
    url(r'^accounts/username/change/$',views.changeUsername,name="username_change"),
    url(r'^accounts/username/change/done/$',views.changeUsernameDone,name="username_change_done"),
    url(r'^accounts/password/change/$','django.contrib.auth.views.password_change',{'post_change_redirect' : '/accounts/password_change/done/'}, name="password_change"), 
    url(r'^accounts/password/change/done/$','django.contrib.auth.views.password_change_done'),
)
