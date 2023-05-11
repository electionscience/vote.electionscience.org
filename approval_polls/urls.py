from django.conf.urls import url

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
    url(r"^$", index, name="index"),
    url(r"^(?P<pk>\d+)/$", DetailView.as_view(), name="detail"),
    url(r"^(?P<pk>\d+)/results/$", ResultsView.as_view(), name="results"),
    url(
        r"^(?P<poll_id>\d+)/embed_instructions/$",
        embed_instructions,
        name="embed_instructions",
    ),
    url(r"^(?P<poll_id>\d+)/vote/$", vote, name="vote"),
    url(r"^(?P<poll_id>\d+)/edit/$", EditView.as_view(), name="edit"),
    url(
        r"^(?P<poll_id>\d+)/change_suspension/$",
        change_suspension,
        name="change_suspension",
    ),
    url(r"^create/$", CreateView.as_view(), name="create"),
    url(r"^my-polls/$", myPolls, name="my_polls"),
    url(r"^my-info/$", myInfo, name="my_info"),
    url(r"^set-user-timezone/$", set_user_timezone, name="set-user-timezone"),
    url(r"^invitation/(?P<pk>\d+)/$", DetailView.as_view(), name="invitation"),
    url(r"^tag/(?P<tag>.+)/$", taggedPolls, name="tagged_polls"),
    url(r"^all_tags/$", allTags, name="all_tags"),
    url(r"^tag_cloud/$", tagCloud, name="tag_cloud"),
]
