from django.urls import include, path, re_path
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from approval_frame import views

from .views import CustomRegistrationView
app_name = 'approval_polls'


urlpatterns = [
    path("", RedirectView.as_view(url="/approval_polls/", permanent=False)),
    path(
        "approval_polls/", include("approval_polls.urls")
    ),
    re_path(r"^admin/", admin.site.urls),
    path(
        "accounts/register/",
        CustomRegistrationView.as_view(),
        name="registration_register"
    ),
    path("accounts/", include("registration.backends.default.urls")),
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
    # url(
    #     r"^accounts/password/change/$",
    #     include(auth_views.password_change)
    # ),
    # url(
    #     r"^accounts/password/change/done/$",
    #     include(auth_views.password_change_done),
    # ),
]
