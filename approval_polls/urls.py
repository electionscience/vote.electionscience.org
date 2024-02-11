from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "approval_polls"

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    # path("passkeys/", include("passkeys.urls")),
    # path("accounts/logout/", views.logoutView, name="auth_logout"),
    # path("accounts/login/", views.loginView, name="account_login"),
    # path("accounts/", include("registration.backends.simple.urls")),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path(
        "<int:poll_id>/embed_instructions/",
        views.embed_instructions,
        name="embed_instructions",
    ),
    path("<int:poll_id>/vote/", views.vote, name="vote"),
    path("<int:poll_id>/edit/", views.EditView.as_view(), name="edit"),
    path(
        "<int:poll_id>/change_suspension/",
        views.change_suspension,
        name="change_suspension",
    ),
    path("create/", views.CreateView.as_view(), name="create"),
    path("my-polls/", views.my_polls, name="my_polls"),
    path("my-info/", views.my_info, name="my_info"),
    path("set-user-timezone/", views.set_user_timezone, name="set-user-timezone"),
    path("invitation/<int:pk>/", views.DetailView.as_view(), name="invitation"),
    path("tag/<path:tag>/", views.tagged_polls, name="tagged_polls"),
    path("all_tags/", views.all_tags, name="all_tags"),
    path("tag_cloud/", views.tag_cloud, name="tag_cloud"),
    path("accounts/", include("allauth.urls")),
]
