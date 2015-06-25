from django.conf.urls import patterns, include, url
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView
from forms import RegistrationFormCustom, PasswordResetFormCustom
from django.contrib.auth.views import password_reset, password_reset_done

# autodiscover is required only for older versions of Django
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^approval_polls/', include('approval_polls.urls', namespace="approval_polls")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=RegistrationFormCustom), name='registration_register'),
    url(r'^accounts/password/reset/$', password_reset, {'password_reset_form' : PasswordResetFormCustom}),
    url(r'^accounts/password/reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^accounts/', include('registration.auth_urls')),
    url(r'^accounts/', include('registration.backends.default.urls'))
)
