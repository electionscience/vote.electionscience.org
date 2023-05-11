from django.urls import path

from approval_polls.views import (
    CreateView,
    DetailView,
    EditView,
    ResultsView,
    allTags,
    change_suspension,
    embed_instructions,
    index,
    myInfo,
    myPolls,
    set_user_timezone,
    tagCloud,
    taggedPolls,
    vote,
)

urlpatterns = [
    path("", index, name="index"),
    path("<int:pk>/", DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", ResultsView.as_view(), name="results"),
    path(
        "<int:poll_id>/embed_instructions/",
        embed_instructions,
        name="embed_instructions",
    ),
    path("<int:poll_id>/vote/", vote, name="vote"),
    path("<int:poll_id>/edit/", EditView.as_view(), name="edit"),
    path(
        "<int:poll_id>/change_suspension/",
        change_suspension,
        name="change_suspension",
    ),
    path("create/", CreateView.as_view(), name="create"),
    path("my-polls/", myPolls, name="my_polls"),
    path("my-info/", myInfo, name="my_info"),
    path("set-user-timezone/", set_user_timezone, name="set-user-timezone"),
    path("invitation/<int:pk>/", DetailView.as_view(), name="invitation"),
    path("tag/<path:tag>/", taggedPolls, name="tagged_polls"),
    path("all_tags/", allTags, name="all_tags"),
    path("tag_cloud/", tagCloud, name="tag_cloud"),
]
