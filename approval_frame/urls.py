from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^approval_polls/', include('approval_polls.urls', namespace="approval_polls")),
    # Examples:
    # url(r'^$', 'approval_frame.views.home', name='home'),
    # url(r'^approval_frame/', include('approval_frame.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))
)
