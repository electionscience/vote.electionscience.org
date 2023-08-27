from django.urls import path

from approval_polls import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:poll_id>/embed_instructions/', views.embed_instructions, name='embed_instructions'),
    path('<int:poll_id>/vote/', views.vote, name='vote'),
    path('<int:poll_id>/edit/', views.EditView.as_view(), name='edit'),
    path('<int:poll_id>/change_suspension/', views.change_suspension, name='change_suspension'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('my-polls/', views.myPolls, name='my_polls'),
    path('my-info/', views.myInfo, name='my_info'),
    path('set-user-timezone/', views.set_user_timezone, name='set-user-timezone'),
    path('invitation/<int:pk>/', views.DetailView.as_view(), name='invitation'),
    path('tag/<path:tag>/', views.taggedPolls, name='tagged_polls'),
    path('all_tags/', views.allTags, name='all_tags'),
    path('tag_cloud/', views.tagCloud, name='tag_cloud')
]
