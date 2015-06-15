from django.conf.urls import patterns, include, url
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView
from forms import RegistrationFormCustom

# autodiscover is required only for older versions of Django
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^approval_polls/', include('approval_polls.urls', namespace="approval_polls")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=RegistrationFormCustom), name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls'))
)
