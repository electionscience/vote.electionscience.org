from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

from approval_frame import views

from .views import CustomRegistrationView

# autodiscover is required only for older versions of Django
admin.autodiscover()

urlpatterns = [
    path("", RedirectView.as_view(url="/approval_polls/", permanent=False)),
    url(
        "approval_polls/",
        include(("approval_polls.urls", "approval_polls"), namespace="approval_polls"),
    ),
    url("admin/", admin.site.urls),
    path(
        "accounts/register/",
        CustomRegistrationView.as_view(),
        name="registration_register",
    ),
    path('accounts/', include('registration.backends.default.urls')),
    path("accounts/username/change/", views.changeUsername, name="username_change"),
    path(
        "accounts/username/change/done/",
        views.changeUsernameDone,
        name="username_change_done",
    ),
    path(
        "accounts/subscription/change/",
        views.manageSubscriptions,
        name="subscription_change",
    ),
    path(
        "accounts/subscription/change/done/",
        views.manageSubscriptionsDone,
        name="subscription_change_done",
    ),
    path(
        "accounts/password/change/",
        auth_views.password_change,
        {"post_change_redirect": "/accounts/password_change/done/"},
        name="password_change",
    ),
    path("accounts/password/change/done/", auth_views.password_change_done),
    path("", include("social.apps.django_app.urls", namespace="social")),
]
