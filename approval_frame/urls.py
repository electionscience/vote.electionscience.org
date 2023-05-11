from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from approval_frame import views

from .views import CustomRegistrationView

# autodiscover is required only for older versions of Django
admin.autodiscover()

urlpatterns = [
    url(r"^$", RedirectView.as_view(url="/approval_polls/", permanent=False)),
    url(
        r"^approval_polls/", include("approval_polls.urls", namespace="approval_polls")
    ),
    url(r"^admin/", include(admin.site.urls)),
    url(
        r"^accounts/register/$",
        CustomRegistrationView.as_view(),
        name="registration_register",
    ),
    url(r"^accounts/", include("registration.backends.default.urls")),
    url(r"^accounts/username/change/$", views.changeUsername, name="username_change"),
    url(
        r"^accounts/username/change/done/$",
        views.changeUsernameDone,
        name="username_change_done",
    ),
    url(
        r"^accounts/subscription/change/$",
        views.manageSubscriptions,
        name="subscription_change",
    ),
    url(
        r"^accounts/subscription/change/done/$",
        views.manageSubscriptionsDone,
        name="subscription_change_done",
    ),
    url(
        r"^accounts/password/change/$",
        auth_views.password_change,
        {"post_change_redirect": "/accounts/password_change/done/"},
        name="password_change",
    ),
    url(r"^accounts/password/change/done/$", auth_views.password_change_done),
    url("", include("social.apps.django_app.urls", namespace="social")),
]
